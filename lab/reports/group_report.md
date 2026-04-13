---
modified: 2026-04-13 23:26:56
created: 2026-04-13 21:25:21
---
# Báo Cáo Nhóm — Lab Day 08: Full RAG Pipeline

**Tên nhóm:** Nhóm 8
**Thành viên:**

| Tên                    | Vai trò             | Email                    |
| ---------------------- | ------------------- | ------------------------ |
| Đặng Văn Minh          | Tech Lead           | minhdv0201@gmail.com     |
| Nguyễn Thị Quỳnh Trang | Retrieval Owner     | quynhtrang1225@gmail.com |
| Nguyễn Quang Tùng      | Retrieval Owner     | ___                      |
| Đồng Văn Thịnh         | Eval Owner          | dvttvdthanhan@gmail.com  |
| Nguyễn Văn Quang       | Eval Owner          | qcontact.12@gmail.com    |
| Nguyễn Mạnh Dũng       | Documentation Owner | ___                      |

**Ngày nộp:** 13/04/2026  
**Repo:** https://github.com/quangliz/Day08_E403
**Độ dài khuyến nghị:** 600–900 từ

---

> **Hướng dẫn nộp group report:**
>
> - File này nộp tại: `reports/group_report.md`
> - Deadline: Được phép commit **sau 18:00** (xem SCORING.md)
> - Tập trung vào **quyết định kỹ thuật cấp nhóm** — không trùng lặp với individual reports
> - Phải có **bằng chứng từ code, scorecard, hoặc tuning log** — không mô tả chung chung

---

## 1. Pipeline nhóm đã xây dựng (150–200 từ)

> Mô tả ngắn gọn pipeline của nhóm:
> - Chunking strategy: size, overlap, phương pháp tách (by paragraph, by section, v.v.)
> - Embedding model đã dùng
> - Retrieval mode: dense / hybrid / rerank (Sprint 3 variant)

**Chunking decision:**
> Nhóm dùng chunk_size=400, overlap=80, tách theo paragraph để tránh cắt giữa câu."

_________________

**Embedding model:**
> Sử dụng text-embedding-3-small vì đây là mô hình phổ biến và rẻ của OpenAI, đủ cho việc biểu diễn ngữ nghĩa cơ bản các đoạn văn tiếng Việt.
_________________

**Retrieval variant (Sprint 3):**
> Lý do chọn hybrid vì có sự kết hợp giữa semantic search và BM25 (keyword search), giúp retrieve tốt hơn các từ viết tắt, trùng lặp nhiều.
_________________

---

## 2. Quyết định kỹ thuật quan trọng nhất (200–250 từ)

> Chọn **1 quyết định thiết kế** mà nhóm thảo luận và đánh đổi nhiều nhất trong lab.
> Phải có: (a) vấn đề gặp phải, (b) các phương án cân nhắc, (c) lý do chọn.

**Quyết định:** Chiến lược chunking — heading-based + paragraph split vs. fixed character size

**Bối cảnh vấn đề:**

Các tài liệu nội bộ (SOP, policy) có cấu trúc section rõ ràng (`=== ... ===`) nhưng độ dài mỗi section không đồng đều. Nếu dùng fixed character split, chunk sẽ thường xuyên cắt ngang giữa điều khoản — ví dụ cắt ngay trước điều kiện ngoại lệ của một quy định — khiến context thiếu ý khi đưa vào prompt.

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| Fixed character split (cứng theo số ký tự) | Đơn giản, dễ implement, chunk đều | Dễ cắt giữa điều khoản, mất ngữ nghĩa ranh giới tự nhiên |
| Heading-based + paragraph split + overlap | Giữ nguyên một điều khoản trong cùng chunk; overlap 80 tokens giảm mất ngữ cảnh ranh giới | Phụ thuộc vào format heading nhất quán trong tài liệu |

**Phương án đã chọn và lý do:**

Nhóm chọn heading-based split (theo pattern `=== ... ===`) kết hợp paragraph split nếu section quá dài (> 1600 ký tự), với overlap 80 tokens giữa các chunk liền kề. Lý do: corpus có cấu trúc section rõ ràng, ưu tiên cắt tại ranh giới tự nhiên giúp một điều khoản nằm trọn trong một chunk — đặc biệt quan trọng với câu hỏi multi-condition như gq05 và gq06.

**Bằng chứng từ scorecard/tuning-log:**

Context Recall đạt 5.00/5 ở cả baseline và variant (`results/scorecard_baseline.md`, `scorecard_variant.md`), tức là 100% expected source được retrieve thành công. Đây là bằng chứng trực tiếp rằng chunking giữ đủ evidence không bị mất ở lớp indexing.

---

## 3. Kết quả grading questions (100–150 từ)

> Sau khi chạy pipeline với grading_questions.json (public lúc 17:00):
> - Câu nào pipeline xử lý tốt nhất? Tại sao?
> - Câu nào pipeline fail? Root cause ở đâu (indexing / retrieval / generation)?
> - Câu gq07 (abstain) — pipeline xử lý thế nào?

**Ước tính điểm raw:** 65 / 98

**Câu tốt nhất:** ID: qg06 — Lý do: Đây là câu khó nhất (12 điểm, cross-doc multi-hop) nhưng pipeline trả lời đầy đủ các ý cốt lõi: on-call IT Admin, phê duyệt bằng lời từ Tech Lead, thời hạn 24h, và yêu cầu log Security Audit. Đây cho thấy khả năng tổng hợp đa tài liệu khá tốt.

**Câu fail:** ID: qg02 — Root cause: generation/completeness (kèm một phần retrieval coverage). Pipeline chỉ trả lời “tối đa 2 thiết bị”, nhưng bỏ mất vế “remote phải dùng VPN” và không tổng hợp đủ ý cross-document như yêu cầu. Theo rubric nên rơi vào mức `Zero`.

**Câu gq07 (abstain):** Pipeline trả lời: “Tôi không biết.”. Đây là abstain đúng hướng (không bịa mức phạt), nhưng còn mơ hồ vì chưa nói rõ “tài liệu hiện có không có quy định penalty”. Theo bảng chấm riêng của gq07: khoảng 5/10 thay vì full.

---

## 4. A/B Comparison — Baseline vs Variant (150–200 từ)

> Dựa vào `docs/tuning-log.md`. Tóm tắt kết quả A/B thực tế của nhóm.

**Biến đã thay đổi (chỉ 1 biến):** retrieve mode từ dense thành hybrid

| Metric | Baseline | Variant 1 | Delta |
|--------|----------|-----------|-------|
| Faithfulness | 4.20/5 | 4.50/5 | +0.30 |
| Answer Relevance | 4.60/5 | 4.60/5 | +0.00 |
| Context Recall | 5.00/5 | 5.00/5 | +0.00 |
| Completeness | 3.80/5 | 3.80/5 | +0.00 |

**Kết luận:**
> Variant hybrid tốt hơn baseline dense ở Faithfulness (+0.30 trong tuning-log, +0.10 trong scorecard chính thức 10 test questions). Cải thiện rõ nhất ở câu access-control nhiều điều kiện, đặc biệt q07 (Approval Matrix) — query dùng alias tên cũ, dense search dễ bỏ sót trong khi BM25 bắt được keyword chính xác. Các metric còn lại (Relevance, Recall, Completeness) giữ nguyên, xác nhận hybrid không gây regression. Kết luận: chỉ thay đổi một biến (retrieval mode), delta rõ ràng và có câu minh họa cụ thể — đúng với A/B rule của lab.

---

## 5. Phân công và đánh giá nhóm (100–150 từ)

> Đánh giá trung thực về quá trình làm việc nhóm.

**Phân công thực tế:**

| Thành viên             | Phần đã làm                                          | Sprint |
| ---------------------- | ---------------------------------------------------- | ------ |
| Đặng Văn Minh          | Hoàn thiện index.py                                  | 1      |
| Nguyễn Quang Tùng      | Xây dựng rag_answer, lựa chọn hybrid                 | 2, 3   |
| Nguyễn Thị Quỳnh Trang | Cải tiến rerank để so sánh với hybrid                | 3      |
| Đồng Văn Thịnh         | Triển khai LLM as judge, tinh chỉnh prompt           | 4      |
| Nguyễn Văn Quang       | Chạy các run_scorecard để đánh giá và hỗ trợ báo cáo | 4      |
| Nguyễn Mạnh Dũng       | Hoàn thiện documents                                 | 4      |

**Điều nhóm làm tốt:**

> Phân công theo vai trò rõ ràng từ đầu giúp mỗi sprint có người chịu trách nhiệm chính. Toàn bộ pipeline chạy end-to-end đúng deadline 18:00 và log grading được nộp đúng giờ (timestamp 17:23). Cả nhóm cùng tham gia review scorecard để xác nhận kết quả trước khi commit.

**Điều nhóm làm chưa tốt:**

> Chưa xử lý tốt hai failure mode rõ ràng từ scorecard: (1) câu abstain gq07 trả lời quá ngắn "Tôi không biết" mà không nêu rõ lý do không có trong tài liệu — ước tính 5/10 thay vì 10/10; (2) câu cross-doc gq02 bỏ sót vế "phải dùng VPN" do chưa kết hợp đủ context từ hai tài liệu. Cả hai lỗi đều nằm ở tầng generation/prompt, không phải retrieval, nhưng nhóm chưa có thời gian chạy A/B thêm cho prompt.

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> Nhóm sẽ thử hai cải tiến có evidence từ scorecard. Thứ nhất, cải thiện prompt abstain: bắt buộc nêu rõ "không tìm thấy thông tin trong tài liệu [x]" và liệt kê nguồn đã kiểm tra — hiện tại gq07 ước tính chỉ 5/10 do abstain mơ hồ, cải tiến này có thể đưa lên 10/10. Thứ hai, tăng `top_k_select` từ 3 lên 4 cho các câu cross-doc (gq02, gq06) để completeness tăng — scorecard cho thấy nhiều câu đúng nguồn nhưng thiếu ý từ tài liệu thứ hai trong context.

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*