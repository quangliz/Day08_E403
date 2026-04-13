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

**Quyết định:** ___________________

**Bối cảnh vấn đề:**

_________________

**Các phương án đã cân nhắc:**

| Phương án | Ưu điểm | Nhược điểm |
|-----------|---------|-----------|
| ___ | ___ | ___ |
| ___ | ___ | ___ |

**Phương án đã chọn và lý do:**

_________________

**Bằng chứng từ scorecard/tuning-log:**

_________________

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
> Variant tốt hơn ở Faithfulness

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

> Cùng tham gia vào 

**Điều nhóm làm chưa tốt:**

>

---

## 6. Nếu có thêm 1 ngày, nhóm sẽ làm gì? (50–100 từ)

> 1–2 cải tiến cụ thể với lý do có bằng chứng từ scorecard.

>

---

*File này lưu tại: `reports/group_report.md`*  
*Commit sau 18:00 được phép theo SCORING.md*