# Bộ công cụ phân tích văn bản + Chatbot "Bác sĩ lỗi Python"

Dự án Python cho môn Intro to Programming.
- **Tuần 1:** bộ công cụ phân tích văn bản (`main.py`).
- **Tuần 2:** chatbot "Bác sĩ lỗi Python" (`main_chat.py`): dán thông báo lỗi hoặc mô tả triệu chứng,
  bot chẩn đoán nguyên nhân và gợi ý cách sửa, dựa trên bộ hồ sơ `data/errors.json`.

## Tính năng
- Chuẩn hóa văn bản tiếng Việt: chữ thường, bỏ dấu câu, xử lý có dấu / không dấu.
- Hiểu số tiền nhiều cách viết: `12tr`, `12 triệu`, `12.000.000đ` đều thành `12000000`.
- Thống kê: số từ, số câu, độ dài câu trung bình, độ đa dạng từ vựng, top từ phổ biến.
- Trích từ khóa bằng TF-IDF (tự cài đặt, không dùng thư viện).
- So sánh độ giống nhau giữa hai văn bản: Jaccard và cosine.

## Cách chatbot hoạt động
1. `error_parser.py` (luật/regex): đọc traceback, nhận ra loại lỗi, file và dòng.
2. `knowledge_base.py`: biến mỗi hồ sơ lỗi thành vector TF-IDF (có thêm cặp từ - bigram).
3. `chatbot.py`: nếu nhận ra loại lỗi thì chỉ xét hồ sơ cùng loại, rồi chọn hồ sơ khớp nội dung nhất
   bằng cosine; nếu không thì tìm theo độ giống của câu chữ. Điểm quá thấp thì thừa nhận không biết
   và ghi câu hỏi vào `unanswered.log`. Nhớ ngữ cảnh ngắn: 'ví dụ', 'cách khác'.
4. `evaluate.py`: đo tỉ lệ chọn đúng hồ sơ (top-1, top-3) trên bộ câu hỏi dễ và khó.

## Cấu trúc
| File | Vai trò |
|---|---|
| `text_processor.py` | Chuẩn hóa, bỏ dấu, hiểu số tiền, tách câu, tách từ |
| `analyzer.py` | Đếm từ, thống kê, TF-IDF, Jaccard, cosine |
| `main.py` | Menu console phân tích văn bản (tuần 1) |
| `error_parser.py` | Đọc traceback: loại lỗi, nội dung, file, dòng |
| `knowledge_base.py` | Nạp hồ sơ lỗi, TF-IDF + bigram, tìm kiếm |
| `chatbot.py` | Bác sĩ lỗi Python: chẩn đoán, ngữ cảnh, log |
| `main_chat.py` | Giao diện console của chatbot |
| `evaluate.py` | Đo độ chính xác |
| `data/errors.json` | Bộ hồ sơ lỗi (25 hồ sơ) |
| `test_*.py` | Kiểm thử |
| `run_tests.py` | Chạy tất cả test một lần |
| `embedding_demo.py` | Thí nghiệm so sánh đếm từ và embedding (tùy chọn) |
| `requirements.txt` | Thư viện cần cho phần tùy chọn |
| `samples/` | Văn bản mẫu (UTF-8) |

## Cách chạy
```
python main.py                    # phân tích văn bản (tuần 1)
python main_chat.py               # chatbot Bác sĩ lỗi Python (tuần 2)
python evaluate.py                # đo độ chính xác chatbot
python run_tests.py               # chạy tất cả test
python embedding_demo.py          # tùy chọn, cần: pip install -r requirements.txt
```
Yêu cầu: Python 3.10 trở lên. Chương trình chính không cần cài thêm thư viện
(chỉ `embedding_demo.py` cần `sentence-transformers`). File văn bản phải lưu mã hóa UTF-8.

## Hạn chế đã biết
- Chatbot chỉ hiểu những cách diễn đạt có từ trùng với hồ sơ; câu hỏi dùng từ khác (đồng nghĩa) dễ bị sai. Bộ câu hỏi khó đạt khoảng 63% top-1 (84% top-3).
- Bộ câu hỏi đánh giá do người viết hồ sơ soạn nên có thiên vị.
- Tách từ theo khoảng trắng, nên từ ghép tiếng Việt như "sinh viên" bị tách thành "sinh" và "viên".
- Số tiền viết bằng chữ ("mười hai triệu") chưa được hiểu.
- Dấu chấm kiểu `1.500` luôn được coi là hàng nghìn.
- Danh sách từ dừng còn nhỏ, cần bổ sung dần.

## Hướng phát triển
- Bổ sung hồ sơ lỗi và từ đồng nghĩa dựa trên `unanswered.log`.
- Thử embedding để hiểu nghĩa thay vì chỉ khớp từ (xem `embedding_demo.py`).
- Tuần 3: giao diện tkinter, đánh giá bằng câu hỏi do bạn bè đặt.