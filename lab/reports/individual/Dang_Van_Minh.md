# Báo Cáo Cá Nhân — Lab Day 08: RAG Pipeline

**Họ và tên:** Đặng Văn Minh  
**Mã số học viên:** 2A202600027  
**Vai trò trong nhóm:** Tech Lead  
**Ngày nộp:** 13/04/2026  
**Độ dài yêu cầu:** 500–800 từ

---

## 1. Tôi đã làm gì trong lab này? (100-150 từ)

Với vai trò Tech Lead, tôi dẫn Sprint 1 và giữ nhịp kết nối code giữa các sprint. Nhiệm vụ cụ thể là implement toàn bộ `index.py`: viết `preprocess_document()` để extract metadata từ header file (Source, Department, Effective Date, Access), viết `chunk_document()` và `_split_by_size()` để chia tài liệu theo section heading trước rồi split tiếp theo paragraph với overlap 80 tokens. Quyết định dùng OpenAI `text-embedding-3-small` để embed và lưu vào ChromaDB `PersistentClient` với cosine similarity.

Sau khi build index xong (commit `b100c78 add index pipeline`, `72e44fb add chrom_db`), tôi kiểm tra bằng `list_chunks()` và `inspect_metadata_coverage()` trước khi bàn giao cho Retrieval Owner. Phần index là nền tảng — nếu chunk hoặc metadata sai, toàn bộ pipeline phía sau đều bị ảnh hưởng.

---

## 2. Điều tôi hiểu rõ hơn sau lab này (100-150 từ)

Sau lab này, tôi thực sự hiểu rõ hơn về **chuỗi grounding từ indexing đến citation**. Trước lab, tôi nghĩ grounded answer chỉ đơn giản là "model không bịa". Nhưng sau khi xây toàn bộ lớp indexing, tôi thấy grounding là một chuỗi liên kết: metadata (`source`, `section`, `effective_date`) được gắn vào từng chunk khi index → `build_context_block()` trong `rag_answer.py` đóng gói metadata thành header `[1] source | section | score=...` → prompt yêu cầu model cite bằng `[1]` → kết quả answer có nguồn truy vết được.

Nếu bất kỳ mắt xích nào đứt — ví dụ metadata thiếu `source`, hoặc header format không nhất quán — model vẫn trả lời được nhưng citation sẽ sai hoặc thiếu. Context Recall đạt 5.00/5 ở cả baseline và variant là bằng chứng chuỗi này hoạt động đúng từ đầu.

---

## 3. Điều tôi ngạc nhiên hoặc gặp khó khăn (100-150 từ)

Điều bất ngờ nhất là regex split heading gặp nhiều edge case hơn dự kiến. Pattern `r"(===.*?===)"` không match một số dòng heading có thêm khoảng trắng ở đầu hoặc ký tự đặc biệt, khiến toàn bộ section bị gộp vào một chunk duy nhất. Chỉ phát hiện ra khi chạy `list_chunks()` và thấy preview text dài bất thường. Phải đọc từng file `.txt` để điều chỉnh logic.

Khó khăn thứ hai là ChromaDB upsert im lặng khi có chunk bị lỗi: nếu embedding vector sai dimension hoặc id trùng, collection không throw exception rõ ràng mà chỉ fail khi query sau đó. Từ kinh nghiệm này, tôi học được thói quen chạy `inspect_metadata_coverage()` ngay sau mỗi lần `build_index()`, thay vì chờ đến lúc retrieval trả kết quả lạ mới bắt đầu debug từ dưới lên.

---

## 4. Phân tích một câu hỏi trong grading (150-200 từ)

**Câu hỏi:** `qg06` — *"Lúc 2 giờ sáng xảy ra sự cố P1, on-call engineer cần cấp quyền tạm thời cho một engineer xử lý incident. Quy trình cụ thể như thế nào và quyền này tồn tại bao lâu?"*

**Phân tích:**

Đây là câu khó nhất trong bộ grading (12 điểm) vì đòi hỏi tổng hợp từ hai tài liệu độc lập: `sla_p1_2026.txt` (quy trình leo thang P1 ngoài giờ hành chính) và `access_control_sop.txt` (điều kiện và giới hạn thời gian khi cấp quyền tạm thời).

Pipeline trả lời đúng: on-call IT Admin cấp quyền tạm thời tối đa 24 giờ sau khi Tech Lead phê duyệt bằng lời; sau 24 giờ phải có ticket chính thức hoặc quyền bị thu hồi tự động; toàn bộ phải ghi log vào Security Audit. Sources khớp cả hai tài liệu liên quan.

Câu này thành công vì chunking giữ nguyên toàn bộ đoạn "Emergency Access Procedure" trong một chunk, không cắt ngang điều kiện 24 giờ. Hybrid retrieval kết hợp semantic (`P1 incident`, `emergency`) với keyword (`quyền tạm thời`, `on-call`) nên cả hai nguồn đều được retrieve vào context. Nếu chunk bị cắt ngang hoặc chỉ dùng dense search, rủi ro là bỏ sót một trong hai tài liệu, câu trả lời sẽ thiếu bước ghi Security Audit hoặc sai thời hạn 24 giờ — dẫn đến Partial thay vì Full marks.

---

## 5. Nếu có thêm thời gian, tôi sẽ làm gì? (50-100 từ)

Tôi sẽ thử hai cải tiến có evidence từ eval. Thứ nhất, bổ sung **metadata filter theo `effective_date`** khi query để ưu tiên phiên bản policy mới nhất — câu `qg10` (phân biệt v4 với đơn trước 01/02) cho thấy rủi ro của việc không filter theo ngày hiệu lực. Thứ hai, tăng `overlap` từ 80 lên 120 tokens ở các section dài nhiều điều kiện, vì completeness đạt 4.30/5 — nhiều khả năng các điều kiện ngoại lệ nằm tại ranh giới chunk vẫn đang bị underrepresented trong context gửi vào LLM.
