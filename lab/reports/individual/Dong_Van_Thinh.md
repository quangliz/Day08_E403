# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đồng Văn Thịnh
**Vai trò trong nhóm:** Eval Owner
**Ngày nộp:** 13/04/2026
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

> Sprint đã tham gia là sprint 3 và sprint 4.
> Công việc bao gồm: chạy thử nghiệm các run_scorecard với BASELINE_CONFIG và VARIANT_CONFIG (Human as Judge), lấy thông số delta từ 2 config để so sánh.
> Cải thiện prompt, tinh chỉnh thông số để tăng chất lượng mô hình.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

> Sau lab này, tôi đã thay đổi tư duy từ đánh giá cảm tính sang vận hành Evaluation Loop chặt chẽ với các metric định lượng như Faithfulness, Relevance, Context Recall và Completeness. Việc phân tích chỉ số Delta giúp tôi nhận diện rõ ranh giới giữa khả năng truy xuất và tổng hợp thông tin.

>Bài học từ Case q09 là minh chứng cho sức mạnh của Hybrid Search. Trong khi Vector Search thường "bó tay" trước các mã lỗi đặc thù (OOD), sự kết hợp của BM25 giúp truy xuất chính xác từ khóa kỹ thuật. Điều này cho phép LLM suy luận từ ngữ cảnh liên quan để đưa ra giải pháp hữu ích thay vì chỉ trả lời "không biết".

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

> Tôi khá bất ngờ khi một số chỉ số đánh giá của variant hybrid lại thấp hơn baseline dense. Ban đầu tôi nghĩ nguyên nhân có thể do tỉ lệ dense_weight và sparse_weight chưa cân bằng hợp lý. Sau khi tìm hiểu bản chất của các mô hình, tôi thay đổi lại prompt, thiết kế lại rerank và nó đã giúp hybrid cải thiện rõ rệt mặc dù có một số case, dense vẫn tỏ ra tốt hơn so với hybrid ở một số tiêu chí.

---

## 4. Phân tích một câu hỏi trong scorecard (150-200 từ)

>Trong bảng Scorecard, q09 là minh chứng rõ rệt nhất cho sự ưu việt của cấu hình Variant (Hybrid Search). Ở phiên bản Baseline (Dense Search), hệ thống chỉ đạt điểm Relevance 2/5 và Faithfulness 2/5. Nguyên nhân là do mã lỗi "ERR-403-AUTH" là một từ khóa đặc hiệu (Out-of-Vocabulary), khiến mô hình Vector Embedding không tìm được điểm tương đồng ngữ nghĩa chính xác, dẫn đến việc LLM trả lời mơ hồ hoặc thừa nhận không biết.

>Ngược lại, khi chuyển sang Variant_Hybrid, điểm số đã nhảy vọt lên 4/5. Nhờ sự hỗ trợ của lớp Sparse Search (BM25), hệ thống đã "tóm" được chính xác các chunk văn bản chứa từ khóa mã lỗi. Điều thú vị là dù tài liệu gốc không giải thích trực diện mã lỗi này, nhưng nhờ cấu hình Hybrid, AI đã truy xuất được các đoạn về "quy trình khóa tài khoản" và "portal SSO". Kết hợp với Prompt mới yêu cầu liệt kê chi tiết, LLM đã đưa ra được các bước xử lý logic như: kiểm tra đăng nhập, liên hệ IT Helpdesk hoặc tự reset qua portal. Điều này không chỉ tăng tính Completeness mà còn biến một câu trả lời từ "từ chối" sang "hướng dẫn giải quyết vấn đề", nâng cao trải nghiệm người dùng cuối một cách thiết thực.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

> Tôi sẽ thử **Triển khai một Cross-Encoder Reranker.** vì đôi khi LLM vẫn bị nhiễu bởi các đoạn văn bản kém liên quan. Reranker sẽ đóng vai trò như một "màng lọc tinh", đánh giá lại mối quan hệ trực tiếp giữa câu hỏi và từng chunk văn bản, giúp đẩy những thông tin quan trọng nhất lên đầu, tập trung tối đa vào dữ liệu đúng, từ đó giải quyết triệt để bài toán đánh đổi giữa độ chính xác và tính đầy đủ.
