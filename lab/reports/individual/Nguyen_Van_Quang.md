# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Nguyễn Văn Quang
**Vai trò trong nhóm:** Eval Owner
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Sprint đã tham gia là sprint 3 và sprint 4.
> Công việc bao gồm: chạy thử nghiệm các run_scorecard với BASELINE_CONFIG và VARIANT_CONFIG (Human as Judge) để đóng góp vào quá trình implement LLM as Judge của Eval Owner khác, và tham gia đóng góp vào việc báo cáo số liệu của Document Owner.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Sau lab này, tôi hiểu rõ hơn về evaluation loop trong RAG. Không thể chỉ dựa vào cảm giác để đánh giá kết quả, mà phải chia nhỏ thành các metric riêng biệt như Faithfulness, Relevance, Context Recall và Completeness. Khi chạy scorecard, tôi thấy có trường hợp recall cao nhưng faithfulness lại thấp (ví dụ q10), tức là retriever lấy đúng tài liệu nhưng model trả lời chưa đúng/đủ so với đáp án kỳ vọng. Nói cách khác, model bám vào câu hỏi nhưng ý trả lời vẫn chưa đầy đủ.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Tôi khá bất ngờ khi một số chỉ số đánh giá của variant hybrid lại thấp hơn baseline dense. Ban đầu tôi nghĩ nguyên nhân có thể do tỉ lệ dense_weight và sparse_weight chưa cân bằng hợp lý. Sau đó, tôi tăng dense_weight lên 0.9 để ưu tiên kết quả semantic search và chỉ giữ sparse_weight ở mức thấp nhằm hỗ trợ các trường hợp query có nhiều từ viết tắt hoặc lặp từ trong chunk. Tuy vậy, kết quả cuối cùng vẫn cho thấy các metrics của variant thấp hơn so với dense, khiến tôi nhận ra việc tuning trọng số cho hybrid retriever không đơn giản như dự đoán.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

>Tôi chọn q10 vì đây là câu phân biệt rõ khả năng retrieval và generation. Khi cả baseline (dense) và variant (hybrid) đều có điểm 1/2/5/3 (Faithfulness/Relevance/Recall/Completeness), điều này cho thấy hai cấu hình đều retrieve đúng nguồn (Recall = 5), nhưng đều chưa trả lời tốt ở tầng diễn giải.

>Cụ thể, câu trả lời kiểu “không có thông tin... tôi không biết” không tận dụng đầy đủ nội dung chunk về quy trình hoàn tiền chuẩn. Vì vậy, Faithfulness và Relevance đều thấp, còn Completeness chỉ ở mức trung bình do thiếu các ý quan trọng như mốc 3-5 ngày làm việc và kết luận rõ ràng về việc không có quy trình riêng cho VIP trong tài liệu.

>Từ case này, tôi kết luận hybrid chưa tạo cải thiện thực tế so với dense ở câu hỏi dạng policy edge-case. Vấn đề chính vẫn là generation, không phải retrieval. Hướng tối ưu tiếp theo là ép format trả lời theo template cố định: kết luận trực tiếp có/không, trích policy hiện hành, và nêu rõ phần tài liệu chưa đề cập để tránh trả lời chung chung.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> Tôi sẽ thử **custom answer prompt theo checklist completeness** (bắt buộc nêu đủ: kết luận trực tiếp, điều kiện, ngoại lệ, mốc thời gian) vì kết quả eval cho thấy completeness thấp hơn mong đợi dù faithfulness cao.
