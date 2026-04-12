# 🧩 Đồ án: Trí tuệ nhân tạo - Giải mã Futoshiki (Futoshiki Logic Solver)

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

> [!NOTE]
> Đồ án này là một ứng dụng Trí tuệ nhân tạo dùng để tự động giải bài toán logic **Futoshiki** — một trò chơi giải đố trên lưới tương tự Sudoku nhưng đi kèm với các ràng buộc về dấu lớn hơn/nhỏ hơn giữa các ô. 

Chương trình được phát triển bằng ngôn ngữ Python, tích hợp giao diện người dùng (GUI) trực quan và cài đặt nhiều thuật toán suy diễn logic, tìm kiếm khác nhau để đánh giá hiệu năng.

## ✨ Tính năng nổi bật

* **Tích hợp 4 Thuật toán Logic & Tìm kiếm:** Triển khai từ các phương pháp cơ bản đến nâng cao:
  * **Backtracking (BT)**
  * **Forward Chaining / DPLL (FC)**
  * **Backward Chaining (BC)**
  * **A* Search với Heuristic cải tiến**
* **Giao diện trực quan (UI/UX):** Xây dựng bằng `tkinter` với Dark-theme hiện đại.
* **Mô phỏng từng bước (Visualization):** Theo dõi quá trình thuật toán điền số và quay lui ngay trên lưới trò chơi.
* **Hệ thống Benchmark:** Đo lường chính xác thời gian chạy (Runtime), bộ nhớ (RAM) và số lượng nút (Nodes) đã duyệt.

## 🧠 Chi tiết các thuật toán

1. **Backtracking (BT):** Thử sai và quay lui cơ bản để tìm lời giải hợp lệ.
2. **Forward Chaining / DPLL (FC):**
   * Chuyển đổi bài toán sang dạng chuẩn tắc hội (CNF).
   * Sử dụng 12 tiên đề logic để ràng buộc giá trị, hàng, cột và các dấu so sánh.
   * Giải quyết bằng thuật toán DPLL kết hợp kỹ thuật Unit Propagation.
3. **Backward Chaining (BC):**
   * Sử dụng cơ chế suy diễn lùi (SLD Resolution) giống như ngôn ngữ Prolog.
   * Thực hiện truy vấn (Query) để tìm miền giá trị hợp lệ cho ô trống cụ thể.
4. **A* Search (Tối ưu nhất):**
   * **Heuristic MRV:** Ưu tiên chọn ô có ít giá trị khả thi nhất.
   * **Tie-breaker:** Ưu tiên ô bị kẹp bởi nhiều dấu ràng buộc nhất (Inequality Degree) để giảm không gian tìm kiếm nhanh nhất.

## 📂 Cấu trúc thư mục dự án

```text
Futoshiki-Logic-Project/
├── Source/
│   ├── futoshiki.py          # Chạy CLI và Benchmark tổng hợp
│   ├── futoshiki_ui.py       # Giao diện đồ họa (GUI) chính
│   ├── requirements.txt      # Thư viện cần thiết (matplotlib, numpy)
│   ├── Inputs/               # 10 bộ dữ liệu mẫu (N=4 đến N=9)
│   └── Outputs/              # Kết quả giải (output-*.txt)
├── .gitignore                # Cấu hình bỏ qua file rác
└── README.md                 # Tài liệu hướng dẫn
```

## ⚙️ Cài đặt & Yêu cầu hệ thống

> [!IMPORTANT]
> Dự án yêu cầu **Python 3.8 trở lên** để đảm bảo tính ổn định của các thư viện đồ họa.

### 1. Cài đặt thư viện
Mở Terminal/Command Prompt tại thư mục dự án và chạy lệnh:

```bash
pip install -r Source/requirements.txt
```
*(Thư viện chính: `matplotlib>=3.5.0`, `numpy>=1.21.0`)*

## 🚀 Hướng dẫn chạy chương trình

### Cách 1: Giao diện đồ họa (GUI) — Khuyên dùng
Đây là cách tốt nhất để xem thuật toán giải từng bước và xem biểu đồ so sánh:

```bash
python Source/futoshiki_ui.py
```

> [!TIP]
> **Sử dụng:** Nhấn "Open Folder" để chọn thư mục `Inputs`, chọn thuật toán ở thanh điều hướng và nhấn **▶ Solve** để bắt đầu xem mô phỏng.

### Cách 2: Giao diện dòng lệnh (CLI)
Dùng để giải nhanh hàng loạt file và lấy bảng thống kê hiệu năng ngay trên Terminal:

```bash
python Source/futoshiki.py
```
* **Kết quả:** Các file lời giải sẽ được lưu tự động vào thư mục `Source/Outputs/`.

## 📝 Định dạng dữ liệu đầu vào (Input)

Mỗi file `input-*.txt` gồm 4 phần chính:
1. **Kích thước N:** (Ví dụ: 4, 5, 9).
2. **Ma trận số:** N hàng, mỗi hàng N số (0 là ô trống).
3. **Dấu ngang:** Ràng buộc ngang (1: `<`, -1: `>`, 0: không).
4. **Dấu dọc:** Ràng buộc dọc (1: `^`, -1: `v`, 0: không).

---
> [!CAUTION]
> Đảm bảo các file input nằm đúng cấu trúc thư mục để chương trình không gặp lỗi khi tìm đường dẫn.

***
*Sản phẩm được thực hiện cho mục đích nghiên cứu các thuật toán Logic trong Trí tuệ nhân tạo.*