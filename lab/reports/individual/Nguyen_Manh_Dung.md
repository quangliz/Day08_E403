# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Mạnh Dũng  
**Vai trò trong nhóm:** Documentation Owner  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Phụ trách vai trò Documentation Owner và làm nhiều nhất ở Sprint 4. Phối hợp với Eval Owner để đọc toàn bộ `scorecard_baseline.md`, `scorecard_variant.md` và `ab_comparison.csv`, sau đó cập nhật `docs/architecture.md` và `docs/tuning-log.md` theo đúng dữ liệu thực chạy. T

Kiểm tra sự nhất quán giữa config, metric và nhận xét A/B để tránh tình trạng “report nói một kiểu, kết quả chạy một kiểu”.

Kết nối phần code và phần trình bày: giúp cả nhóm có tài liệu dễ review, có thể truy vết và bám đúng rubric chấm điểm.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

RAG phải tách thành nhiều lớp, không thể nhìn một câu trả lời “nghe hợp lý” rồi kết luận hệ thống tốt. Cần kiểm tra retrieval có kéo đúng evidence chưa, generation có bám evidence không, rồi completeness có đủ ý không. Ở bộ chạy này, context recall đạt 5.00/5 nhưng completeness chỉ 3.80/5. Nghĩa là hệ thống thường tìm đúng nguồn, nhưng trả lời chưa đủ chi tiết.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Khó khăn lớn nhất là đảm bảo tài liệu phản ánh đúng kết quả, đặc biệt khi có nhiều file và nhiều chỉ số. Ban đầu tôi nghĩ chỉ cần viết phần tổng kết là đủ. Nhưng khi đối chiếu kỹ, tôi thấy nhiều điểm dễ sai nếu không bám log, ví dụ nhầm bộ câu hỏi (`q01` vs `qg01`) hoặc diễn giải delta không đúng. Điều làm tôi bất ngờ là câu `qg07` vẫn rất thấp ở cả baseline và variant (1/1/1), dù các câu khác khá ổn. Đây là dấu hiệu failure mode về abstain: model nói “Tôi không biết” nhưng chưa giải thích grounded theo tài liệu đã truy hồi. Từ đó tôi rút ra rằng documentation không chỉ là ghi chép, mà là lớp kiểm soát chất lượng cuối cùng để nhóm trình bày đúng bản chất hệ thống.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

**Câu hỏi:** `qg05` — “Contractor từ bên ngoài công ty có thể được cấp quyền Admin Access không? Nếu có, cần bao nhiêu ngày và có yêu cầu đặc biệt gì?”

**Phân tích:**

Đây là câu thể hiện rõ tác động của tuning retrieval. Ở baseline (`dense`), câu trả lời nhìn bề ngoài khá đúng, nhưng Faithfulness chỉ 2/5. Theo notes trong `ab_comparison.csv`, hệ thống đã nêu contractor có thể được cấp Admin Access, thời gian 5 ngày và yêu cầu training, nhưng evidence retrieve ở baseline chưa đủ để chống lại rủi ro suy diễn. Nói cách khác, câu trả lời có vẻ đúng nội dung nhưng chưa đủ grounded.

Khi chuyển sang variant (`hybrid`), Faithfulness của cùng câu tăng từ 2 lên 5, còn Relevance/Recall/Completeness giữ mức cao. Điều này ủng hộ giả thuyết rằng hybrid giúp truy hồi tốt hơn các đoạn liên quan phạm vi áp dụng cho contractor/third-party vendor trong Access Control SOP. Với vai trò Documentation Owner, tôi coi `qg05` là “case chứng minh” tốt nhất cho quyết định đổi retrieval mode: chỉ đổi một biến, có delta rõ, có câu minh họa cụ thể, và có thể giải thích nguyên nhân kỹ thuật hợp lý.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Nếu có thêm thời gian, tôi sẽ làm 2 việc cụ thể. Thứ nhất, tối ưu prompt abstain để xử lý `qg07`: bắt buộc nêu “không có thông tin trong tài liệu hiện có” và liệt kê nguồn đã kiểm tra, thay vì chỉ “Tôi không biết”. Thứ hai, chạy thêm A/B nhỏ chỉ đổi `top_k_select` từ 3 lên 4 để cải thiện completeness ở các câu multi-detail (`qg01`, `qg02`, `qg09`, `qg10`). Hai thay đổi này có khả năng tăng chất lượng mà vẫn giữ groundedness.

---
