# Tuning Log — RAG Pipeline (Day 08 Lab)

> Template: Ghi lại mỗi thay đổi và kết quả quan sát được.
> A/B Rule: Chỉ đổi MỘT biến mỗi lần.

---

## Baseline (Sprint 2)

**Ngày:** 2026-04-13  
**Config:**
```
retrieval_mode = "dense"
chunk_size = 400 tokens
overlap = 80 tokens
top_k_search = 10
top_k_select = 3
use_rerank = False
llm_model = gpt-4o-mini
```

**Scorecard Baseline:**
| Metric | Average Score |
|--------|--------------|
| Faithfulness | 4.20 /5 |
| Answer Relevance | 4.60 /5 |
| Context Recall | 5.00 /5 |
| Completeness | 3.80 /5 |
> NOTE: `qg07` có `expected_sources = []` nên `Context Recall = None`; trung bình recall 5.00/5 được tính trên các câu còn lại có expected source.

**Câu hỏi yếu nhất (điểm thấp):**
- `qg07` (Insufficient Context): Faithfulness 1, Relevance 1, Completeness 1.
- `qg05` (Access Control): Faithfulness 2 dù Relevance/Recall/Completeness cao.
- `qg01`, `qg02`: Completeness 3 (thiếu chi tiết version/date hoặc cross-doc constraints).

**Giả thuyết nguyên nhân (Error Tree):**
- [x] Retrieval bias trong dense với câu access-control phức hợp (`qg05`)
- [x] Generation trả lời abstain quá ngắn cho câu thiếu dữ liệu (`qg07`)
- [ ] Cần xác nhận lại chất lượng chunking bằng log index thực tế (không có trong `results/`)
- [ ] Chưa có bằng chứng về token overload từ log runtime

---

## Variant 1 (Sprint 3)

**Ngày:** 2026-04-13  
**Biến thay đổi:** Retrieval strategy từ dense → hybrid (dense + sparse/BM25)  
**Lý do chọn biến này:**
Chọn hybrid vì corpus có cả câu tự nhiên và keyword/mã lỗi. Kỳ vọng hybrid cải thiện truy hồi
đối với alias/keyword (Approval Matrix, ERR-403) so với dense thuần.

**Config thay đổi:**
```
retrieval_mode = "hybrid"
# Các tham số còn lại giữ nguyên như baseline
```

**Scorecard Variant 1:**
| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.20/5 | 4.50/5 | +0.30 |
| Answer Relevance | 4.60/5 | 4.60/5 | +0.00 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 3.80/5 | 3.80/5 | +0.00 |
> NOTE: Cách tính recall ở variant tương tự baseline (bỏ qua câu `qg07` không có expected source).

**Nhận xét:**
- Hybrid cải thiện rõ ở `qg05` (Access Control): Faithfulness tăng từ 2 → 5.
- Các metric còn lại gần như không đổi ở mức trung bình.
- `qg07` vẫn là failure mode lớn nhất ở cả baseline và variant (1/1/1).

**Kết luận:**
Variant 1 tốt hơn baseline về Faithfulness tổng thể (+0.30), các metric khác giữ nguyên.
Hybrid là lựa chọn hợp lý cho bộ câu grading hiện tại vì cải thiện được câu hỏi access-control nhiều điều kiện.
Tuy nhiên, chưa xử lý được failure mode abstain chất lượng thấp ở câu thiếu thông tin (`qg07`).

---

## Variant 2 (nếu có thời gian)

**Biến thay đổi:** ___________  
**Config:**
```
# TODO
```
> NOTE: Chưa chạy Variant 2.

**Scorecard Variant 2:**
| Metric | Baseline | Variant 1 | Variant 2 | Best |
|--------|----------|-----------|-----------|------|
| Faithfulness | ? | ? | ? | ? |
| Answer Relevance | ? | ? | ? | ? |
| Context Recall | ? | ? | ? | ? |
| Completeness | ? | ? | ? | ? |

---

## Tóm tắt học được

1. **Lỗi phổ biến nhất trong pipeline này là gì?**
   > Lỗi không nằm ở recall (đã đạt 5.00/5) mà ở generation completeness/abstain quality:
   > câu trả lời thường đúng ý chính nhưng thiếu chi tiết yêu cầu theo expected answer.

2. **Biến nào có tác động lớn nhất tới chất lượng?**
   > Biến retrieval mode (dense → hybrid) có tác động tích cực rõ ràng nhất lên Faithfulness
   > trong bộ chạy này, đặc biệt với câu access-control nhiều ràng buộc (`qg05`).

3. **Nếu có thêm 1 giờ, nhóm sẽ thử gì tiếp theo?**
   > Tối ưu prompt abstain theo format bắt buộc:
   > "không có thông tin trong tài liệu hiện có + nêu nguồn đã kiểm tra" để cải thiện `qg07`.
   > Sau đó thử 1 A/B nhỏ chỉ đổi `top_k_select` (3 → 4) để tăng completeness ở câu multi-detail.

---

## NOTE — Thiếu thông tin cần bổ sung thủ công

- `results/` chưa có log runtime chi tiết theo câu (danh sách chunks retrieve, prompt đầy đủ), nên chưa thể kết luận chính xác lỗi do retrieval hay generation ở từng case.
- Chưa có bằng chứng từ phiên chạy index gần nhất (số chunk thực tế theo tài liệu, độ phủ metadata tại thời điểm chấm).
- Nếu nộp theo rubric `SCORING.md`, nên bổ sung thêm `logs/grading_run.json` để truy vết rõ hơn.
