import os
from typing import List, Dict, Any, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# CẤU HÌNH
# =============================================================================

TOP_K_SEARCH = 10    # Số chunk lấy từ vector store trước rerank (search rộng)
TOP_K_SELECT = 3     # Số chunk gửi vào prompt sau rerank/select (top-3 sweet spot)

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")


# =============================================================================
# RETRIEVAL — DENSE (Vector Search)
# =============================================================================

def retrieve_dense(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    
    try:
        import chromadb
        from index import get_embedding, CHROMA_DB_DIR

        client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        collection = client.get_collection("lab_rag")

        query_embedding = get_embedding(query)
        result = collection.query(
            query_embeddings=query_embedding,
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        import json
        # print(json.dumps(result, indent=2, ensure_ascii=False))
        chunks = []
        num_returned = len(result["documents"][0]) 
    
        for i in range(num_returned):
            chunks.append({
                "text": result["documents"][0][i],
                "metadata": result["metadatas"][0][i],
                "score": 1 - result["distances"][0][i]
            })
        return chunks
    except Exception as e:
        raise e
    except NotImplementedError:
        raise NotImplementedError(
            "TODO Sprint 2: Implement retrieve_dense().\n"
            "Tham khảo comment trong hàm để biết cách query ChromaDB."
        )


# =============================================================================
# RETRIEVAL — SPARSE / BM25 (Keyword Search)
# Dùng cho Sprint 3 Variant hoặc kết hợp Hybrid
# =============================================================================

from index import CHROMA_DB_DIR
from pathlib import Path

def _get_all_chunks(db_dir: Path = CHROMA_DB_DIR) -> dict:
    import chromadb
    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_collection("lab_rag")
    result = collection.get()
    return result

def retrieve_sparse(query: str, top_k: int = TOP_K_SEARCH) -> List[Dict[str, Any]]:
    
    # TODO Sprint 3: Implement BM25 search
    from rank_bm25 import BM25Okapi
    from index import list_chunks

    all_chunks = _get_all_chunks()
    corpus = all_chunks["documents"]
    # corpus = [chunk["text"] for chunk in all_chunks]
    tokenized_corpus = [doc.lower().split() for doc in corpus]
    bm25 = BM25Okapi(tokenized_corpus)
    tokenized_query = query.lower().split()
    scores = bm25.get_scores(tokenized_query)
    top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
    # print(top_indices)
    # Tạm thời return empty list
    # print("[retrieve_sparse] Chưa implement — Sprint 3")
    # return []
    result = []
    for i in top_indices:
        result.append({
            "text": all_chunks["documents"][i],
            "metadata": all_chunks["metadatas"][i],
            "score": scores[i]
        })
    return result

# =============================================================================
# RETRIEVAL — HYBRID (Dense + Sparse với Reciprocal Rank Fusion)
# =============================================================================

def retrieve_hybrid(
    query: str,
    top_k: int = TOP_K_SEARCH,
    dense_weight: float = 0.8,
    sparse_weight: float = 0.2,
) -> List[Dict[str, Any]]:
    
    # Lấy pool kết quả rộng hơn để fusion hiệu quả hơn
    search_depth = max(top_k * 2, 20)
    
    dense_results = retrieve_dense(query, top_k=search_depth)
    sparse_results = retrieve_sparse(query, top_k=search_depth)

    # Reciprocal Rank Fusion (RRF)
    rrf_scores = {}
    doc_map = {} # Để lưu metadata và text gốc

    # 60 là hằng số k tiêu chuẩn trong RRF để ngăn các rank thấp áp đảo
    K = 60

    # Chấm điểm dense
    for rank, doc in enumerate(dense_results, 1):
        text = doc["text"]
        rrf_scores[text] = rrf_scores.get(text, 0) + dense_weight * (1.0 / (K + rank))
        doc_map[text] = doc

    # Chấm điểm sparse
    for rank, doc in enumerate(sparse_results, 1):
        text = doc["text"]
        rrf_scores[text] = rrf_scores.get(text, 0) + sparse_weight * (1.0 / (K + rank))
        if text not in doc_map:
            doc_map[text] = doc

    # Sắp xếp theo RRF score
    sorted_texts = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
    
    hybrid_results = []
    for text in sorted_texts[:top_k]:
        doc = doc_map[text].copy()
        doc["score"] = rrf_scores[text]
        hybrid_results.append(doc)
        
    return hybrid_results


# =============================================================================
# RERANK (Sprint 3 alternative)
# Cross-encoder để chấm lại relevance sau search rộng
# =============================================================================

def rerank(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = TOP_K_SELECT,
) -> List[Dict[str, Any]]:
    if not candidates:
        return []
    
    # Ở Sprint 3, nếu chưa cài SentenceTransformer, 
    # hãy đảm bảo không lấy quá số lượng đang có
    actual_top_k = min(top_k, len(candidates))
    return candidates[:actual_top_k]


# =============================================================================
# QUERY TRANSFORMATION (Sprint 3 alternative)
# =============================================================================

def transform_query(query: str, strategy: str = "expansion") -> List[str]:
    
    # TODO Sprint 3: Implement query transformation
    # Tạm thời trả về query gốc
    return [query]


# =============================================================================
# GENERATION — GROUNDED ANSWER FUNCTION
# =============================================================================

def build_context_block(chunks: List[Dict[str, Any]]) -> str:
    """
    Đóng gói danh sách chunks thành context block để đưa vào prompt.

    Format: structured snippets với source, section, score (từ slide).
    Mỗi chunk có số thứ tự [1], [2], ... để model dễ trích dẫn.
    """
    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        meta = chunk.get("metadata", {})
        source = meta.get("source", "unknown")
        section = meta.get("section", "")
        score = chunk.get("score", 0)
        text = chunk.get("text", "")

        # TODO: Tùy chỉnh format nếu muốn (thêm effective_date, department, ...)
        header = f"[{i}] {source}"
        if section:
            header += f" | {section}"
        if score > 0:
            header += f" | score={score:.2f}"

        context_parts.append(f"{header}\n{text}")

    return "\n\n".join(context_parts)


def build_grounded_prompt(query: str, context_block: str) -> str:
    
    prompt = f"""Answer only from the retrieved context below.
If the context is insufficient to answer the question, say you do not know and do not make up information.
If the context does not fully address the question, state what information is missing, and then provide any related or general information from the context that might be helpful. Do not make up any information not present in the context.
Following that, if the query looks like a technical error, guess the error and ask them to contact IT helpdesk.
List all conditions, timestamps, and special notes from the context. Include every regulatory detail (e.g., specific days, frequencies, department names) without omission.

Cite the source field (in brackets like [1]) at the end of each relevant sentence or phrase.

Keep your answer short, clear, and factual.
Respond in the same language as the question.

Question: {query}

Context:
{context_block}

Answer:"""
    return prompt


def call_llm(prompt: str) -> str:
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,     # temperature=0 để output ổn định, dễ đánh giá
            max_tokens=512,
        )
        return response.choices[0].message.content
    except:
        raise NotImplementedError(
            "TODO Sprint 2: Implement call_llm().\n"
            "Chọn Option A (OpenAI) hoặc Option B (Gemini) trong TODO comment."
        )


def rag_answer(
    query: str,
    retrieval_mode: str = "dense",
    top_k_search: int = TOP_K_SEARCH,
    top_k_select: int = TOP_K_SELECT,
    use_rerank: bool = False,
    verbose: bool = False,
) -> Dict[str, Any]:
    
    config = {
        "retrieval_mode": retrieval_mode,
        "top_k_search": top_k_search,
        "top_k_select": top_k_select,
        "use_rerank": use_rerank,
    }

    # --- Bước 1: Retrieve ---
    if retrieval_mode == "dense":
        candidates = retrieve_dense(query, top_k=top_k_search)
    elif retrieval_mode == "sparse":
        candidates = retrieve_sparse(query, top_k=top_k_search)
    elif retrieval_mode == "hybrid":
        candidates = retrieve_hybrid(query, top_k=top_k_search)
    else:
        raise ValueError(f"retrieval_mode không hợp lệ: {retrieval_mode}")

    if verbose:
        print(f"\n[RAG] Query: {query}")
        print(f"[RAG] Retrieved {len(candidates)} candidates (mode={retrieval_mode})")
        for i, c in enumerate(candidates[:3]):
            print(f"  [{i+1}] score={c.get('score', 0):.3f} | {c['metadata'].get('source', '?')}")

    # --- Bước 2: Rerank (optional) ---
    if use_rerank:
        candidates = rerank(query, candidates, top_k=top_k_select)
    else:
        candidates = candidates[:top_k_select]

    if verbose:
        print(f"[RAG] After select: {len(candidates)} chunks")

    # --- Bước 3: Build context và prompt ---
    context_block = build_context_block(candidates)
    prompt = build_grounded_prompt(query, context_block)

    if verbose:
        print(f"\n[RAG] Prompt:\n{prompt[:500]}...\n")

    # --- Bước 4: Generate ---
    answer = call_llm(prompt)

    # --- Bước 5: Extract sources ---
    sources = list({
        c["metadata"].get("source", "unknown")
        for c in candidates
    })

    return {
        "query": query,
        "answer": answer,
        "sources": sources,
        "chunks_used": candidates,
        "config": config,
    }


# =============================================================================
# SPRINT 3: SO SÁNH BASELINE VS VARIANT
# =============================================================================

def compare_retrieval_strategies(query: str) -> None:
    
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    strategies = ["dense", "sparse", "hybrid"]  # Thêm "sparse" sau khi implement

    for strategy in strategies:
        print(f"\n--- Strategy: {strategy} ---")
        try:
            result = rag_answer(query, retrieval_mode=strategy, verbose=False)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except NotImplementedError as e:
            print(f"Chưa implement: {e}")
        except Exception as e:
            print(f"Lỗi: {e}")


# =============================================================================
# MAIN — Demo và Test
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("Sprint 2 + 3: RAG Answer Pipeline")
    print("=" * 60)

    # Test queries từ data/test_questions.json
    test_queries = [
        "SLA xử lý ticket P1 là bao lâu?",
        "Khách hàng có thể yêu cầu hoàn tiền trong bao nhiêu ngày?",
        "Ai phải phê duyệt để cấp quyền Level 3?",
        "ERR-403-AUTH là lỗi gì?",  # Query không có trong docs → kiểm tra abstain
    ]

    print("\n--- Sprint 2: Test Baseline (Dense) ---")
    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            result = rag_answer(query, retrieval_mode="hybrid", verbose=True)
            print(f"Answer: {result['answer']}")
            print(f"Sources: {result['sources']}")
        except NotImplementedError:
            print("Chưa implement — hoàn thành TODO trong retrieve_dense() và call_llm() trước.")
        except Exception as e:
            print(f"Lỗi: {e}")

    # Uncomment sau khi Sprint 3 hoàn thành:
    print("\n--- Sprint 3: So sánh strategies ---")
    compare_retrieval_strategies("Approval Matrix để cấp quyền là tài liệu nào?")
    compare_retrieval_strategies("ERR-403-AUTH")

    # print("\n\nViệc cần làm Sprint 2:")
    # print("  1. Implement retrieve_dense() — query ChromaDB")
    # print("  2. Implement call_llm() — gọi OpenAI hoặc Gemini")
    # print("  3. Chạy rag_answer() với 3+ test queries")
    # print("  4. Verify: output có citation không? Câu không có docs → abstain không?")

    # print("\nViệc cần làm Sprint 3:")
    # print("  1. Chọn 1 trong 3 variants: hybrid, rerank, hoặc query transformation")
    # print("  2. Implement variant đó")
    # print("  3. Chạy compare_retrieval_strategies() để thấy sự khác biệt")
    # print("  4. Ghi lý do chọn biến đó vào docs/tuning-log.md")
