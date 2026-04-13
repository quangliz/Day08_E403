# Lab Day 08 — RAG Pipeline: E403

**Môn:** AI in Action (AICB-P1) · **Nhóm:** E403  
**Ngày nộp:** 13/04/2026

---

## Thành viên nhóm

| Họ và tên | MSHV | Vai trò |
|-----------|------|---------|
| Đặng Văn Minh | 2A202600027 | Tech Lead — Sprint 1, kết nối end-to-end |
| Nguyễn Quang Tùng | 2A202600197 | Retrieval Owner — Sprint 2, `rag_answer.py` |
| Đồng Văn Thịnh | 2A202600365 | Retrieval Owner — Sprint 3, Hybrid RRF |
| Nguyễn Thị Quỳnh Trang | 2A202600406 | Eval Owner — Sprint 3+4, scorecard |
| Nguyễn Văn Quang | 2A202600236 | Eval Owner — Sprint 4, LLM-as-Judge |
| Nguyễn Mạnh Dũng | 2A202600177 | Documentation Owner — Sprint 4, docs |

---

## Tổng quan hệ thống

Nhóm xây dựng **trợ lý nội bộ RAG** cho khối CS + IT Helpdesk — trả lời câu hỏi về chính sách, SLA ticket, quy trình cấp quyền và FAQ dựa trên 5 tài liệu nội bộ, có trích dẫn nguồn kiểm soát được.

```
[5 tài liệu .txt]
        ↓  index.py
[ChromaDB — text-embedding-3-small · cosine]
        ↓  rag_answer.py
[Hybrid Retrieval: Dense + BM25 → RRF]
        ↓
[Grounded Prompt → gpt-4o-mini]
        ↓
[Answer + Citation [1][2] · Abstain nếu không có dữ liệu]
```
---

## Cấu trúc thư mục

```
lab/
├── index.py                      # Sprint 1: Preprocess → Chunk → Embed → Store
├── rag_answer.py                 # Sprint 2+3: Dense / Sparse / Hybrid → Generate
├── eval.py                       # Sprint 4: LLM-as-Judge · Scorecard · A/B
│
├── data/
│   ├── docs/                     # 5 tài liệu nguồn
│   │   ├── policy_refund_v4.txt
│   │   ├── sla_p1_2026.txt
│   │   ├── access_control_sop.txt
│   │   ├── it_helpdesk_faq.txt
│   │   └── hr_leave_policy.txt
│   └── test_questions.json       # 10 câu test + expected answers
│
├── logs/
│   └── grading_run.json          # ★ Log chạy 10 câu grading (17:23 ngày 13/04)
│
├── results/
│   ├── scorecard_baseline.md     # ★ Điểm baseline (LLM-as-Judge)
│   ├── scorecard_variant.md      # ★ Điểm variant hybrid
│   └── ab_comparison.csv         # So sánh per-question
│
├── docs/
│   ├── architecture.md           # ★ Thiết kế pipeline
│   └── tuning-log.md             # ★ A/B experiment log
│
└── reports/
    └── group_report.md
    └── individual/
        ├── Dang_Van_Minh.md
        ├── Nguyen_Quang_Tung.md
        ├── nguyen_thi_quynh_trang.md
        ├── Nguyen_Van_Quang.md
        └── Nguyen_Manh_Dung.md
```

> ★ = file bắt buộc theo rubric `lab/SCORING.md`

---

## Kết quả chính

### Scorecard (10 test questions · LLM-as-Judge)

| Metric | Baseline (Dense) | Variant (Hybrid) | Delta |
|--------|:---:|:---:|:---:|
| Faithfulness | 4.80/5 | 4.90/5 | **+0.10** |
| Answer Relevance | 4.60/5 | 4.60/5 | +0.00 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 4.30/5 | 4.30/5 | +0.00 |

> Variant tốt hơn baseline rõ nhất ở các câu access-control nhiều điều kiện (q03, q07).  
> Chi tiết: [`lab/results/ab_comparison.csv`](lab/results/ab_comparison.csv)

### Grading run (dùng Hybrid)

Log đầy đủ: [`lab/logs/grading_run.json`](lab/logs/grading_run.json)

| Câu | Tóm tắt | Ghi chú |
|-----|---------|---------|
| gq01 | SLA P1 thay đổi từ 6h → 4h | ✓ |
| gq02 | VPN tối đa 2 thiết bị cùng lúc | ✓ |
| gq03 | Flash Sale + đã kích hoạt → không hoàn tiền | ✓ |
| gq04 | Store credit = 110% | ✓ |
| gq05 | Contractor + Admin Access: 5 ngày + security training | ✓ |
| gq06 | P1 2am: quyền tạm thời 24h + audit log | ✓ multi-hop |
| gq07 | Phạt vi phạm SLA P1 → abstain "Tôi không biết" | ⚠ abstain ngắn |
| gq08 | Nghỉ phép 3 ngày ≠ nghỉ ốm 3 ngày | ✓ |
| gq09 | Mật khẩu đổi mỗi 90 ngày, nhắc trước 7 ngày | ✓ |
| gq10 | Policy v4 không áp dụng đơn trước 01/02/2026 | ✓ |

---

## Chạy pipeline

### Cài đặt

```bash
cd lab
pip install -r requirements.txt
cp .env.example .env
# Điền OPENAI_API_KEY vào .env
```

### Chạy từng bước

```bash
# Sprint 1 — Build index
python lab/index.py

# Sprint 2+3 — Test RAG answer
python lab/rag_answer.py

# Sprint 4 — Chạy scorecard (baseline + variant + A/B)
python lab/eval.py
```

### Chạy lại grading log

```python
import json
from datetime import datetime
from lab.rag_answer import rag_answer

with open("lab/data/grading_questions.json") as f:
    questions = json.load(f)

log = []
for q in questions:
    result = rag_answer(q["question"], retrieval_mode="hybrid", verbose=False)
    log.append({
        "id": q["id"],
        "question": q["question"],
        "answer": result["answer"],
        "sources": result["sources"],
        "chunks_retrieved": len(result["chunks_used"]),
        "retrieval_mode": result["config"]["retrieval_mode"],
        "timestamp": datetime.now().isoformat(),
    })

with open("lab/logs/grading_run.json", "w", encoding="utf-8") as f:
    json.dump(log, f, ensure_ascii=False, indent=2)
```

---

## Cấu hình pipeline

| Tham số | Baseline | Variant |
|---------|----------|---------|
| `retrieval_mode` | `dense` | `hybrid` (dense + BM25 · RRF) |
| `top_k_search` | 10 | 10 |
| `top_k_select` | 3 | 3 |
| `use_rerank` | False | False |
| Embedding | `text-embedding-3-small` | `text-embedding-3-small` |
| LLM | `gpt-4o-mini` · temp=0 | `gpt-4o-mini` · temp=0 |
| Vector store | ChromaDB · cosine | ChromaDB · cosine |

---

## Checklist nộp bài

- [x] `index.py` — chạy được, tạo ChromaDB index đủ 5 tài liệu
- [x] `rag_answer.py` — dense / sparse / hybrid, citation `[1]`, abstain
- [x] `eval.py` — LLM-as-Judge, scorecard, A/B comparison (bonus +2)
- [x] `logs/grading_run.json` — 10 câu, timestamp 17:23 (bonus +1)
- [x] `results/scorecard_baseline.md`
- [x] `results/scorecard_variant.md`
- [x] `docs/architecture.md`
- [x] `docs/tuning-log.md`
- [x] Individual reports — 6 thành viên
- [x] `reports/group_report.md`
