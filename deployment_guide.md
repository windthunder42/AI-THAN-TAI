# Hướng Dẫn Đưa App Lên Mạng (Miễn Phí Trọn Đời) 🚀☁️

Cách tốt nhất, ổn định nhất và hoàn toàn miễn phí để chạy ứng dụng **AI Thần Tài Pro** này là sử dụng **Streamlit Community Cloud**.

## Bước 1: Chuẩn bị Code (Tôi đã làm cho bạn) ✅
1.  File `app.py`: Code chính của ứng dụng.
2.  File `xskt_scraper.py`: Module lấy dữ liệu xổ số (cần thiết).
3.  File `requirements.txt`: Danh sách các thư viện cần cài đặt.
4.  File `lucky_bg.png`: Hình nền (nếu có).

**QUAN TRỌNG:**
-   **KHÔNG** tải thư mục `.venv` lên GitHub.
-   **KHÔNG** tải thư mục `__pycache__` lên GitHub.

## Bước 2: Tải lên GitHub 🐙
Để nhận host miễn phí, bạn cần đưa code lên GitHub.
1.  Đăng nhập [GitHub.com](https://github.com) (tạo tài khoản nếu chưa có).
2.  Bấm dấu **+** ở góc trên bên phải -> chọn **New repository**.
3.  Đặt tên Repository (ví dụ: `ai-than-tai`).
4.  Chọn **Public**.
5.  Check vào ô **Add a README file** (tùy chọn).
6.  Bấm **Create repository**.
7.  Trong trang repo mới tạo, bấm **Add file** -> **Upload files**.
8.  Kéo thả các file sau vào:
    -   `app.py`
    -   `xskt_scraper.py`
    -   `requirements.txt`
    -   `lucky_bg.png`
    -   (Các file `.py` khác nếu có logic riêng, ví dụ `find_vietlott_url.py` nếu được import)
9.  Chờ tải xong, kéo xuống dưới bấm **Commit changes**.

## Bước 3: Đưa lên Streamlit Cloud 🎈
1.  Truy cập [share.streamlit.io](https://share.streamlit.io/) và đăng nhập bằng tài khoản GitHub.
2.  Bấm nút **New app**.
3.  Chọn Repository bạn vừa tạo (`ai-than-tai`).
4.  Mục **Main file path**, điền: `app.py`.
5.  Bấm **Deploy!**.
6.  (Tùy chọn) Trong mục **Advanced settings**, không cần chỉnh gì trừ khi bạn dùng Python version quá cũ/mới (mặc định 3.9+ là tốt).

## Bước 4: Tận Hưởng 🎉
-   Chờ khoảng 2-3 phút để hệ thống cài đặt (bạn sẽ thấy màn hình "Oven is cooking...").
-   Sau khi xong, bạn sẽ có một đường link dạng `https://ai-than-tai.streamlit.app`.
-   Bạn có thể gửi link này cho mọi người, truy cập bằng điện thoại, máy tính bảng thoải mái.
-   App sẽ chạy 24/7 và hoàn toàn miễn phí.

---
**Lưu ý:**
-   Nếu gặp lỗi "ModuleNotFoundError", hãy kiểm tra xem bạn đã upload file `.py` tương ứng chưa hoặc đã thêm tên thư viện vào `requirements.txt` chưa.
-   Vì God Mode sử dụng nhiều tài nguyên tính toán, trên gói miễn phí có thể sẽ chạy chậm hơn máy cá nhân một chút.
