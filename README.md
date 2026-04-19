
                    ĐỒ ÁN 2: TRÍ TUỆ NHÂN TẠO - FUTOSHIKI SOLVER

Môn học: Cơ sở Trí tuệ Nhân tạo (CSC14003)
Nhóm thực hiện: Nhóm 07

1. GIỚI THIỆU
-------------
Dự án này giải quyết bài toán điền số Futoshiki bằng cách mô hình hóa các ràng 
buộc dưới dạng Logic Bậc Nhất (First-Order Logic), sau đó chuyển đổi sang Dạng 
Chuẩn Tắc Hội (CNF) và áp dụng các thuật toán Suy diễn / Tìm kiếm.

Các thuật toán được cài đặt bao gồm:
- Brute-Force / Backtracking (BT)
- Forward Chaining / DPLL (FC)
- Backward Chaining (BC - Local SLD Resolution)
- A* Search kết hợp MRV và Heuristic Inequality Degree (A*)


2. YÊU CẦU CÀI ĐẶT (PREREQUISITES)
----------------------------------
- Ngôn ngữ: Python 3.8 trở lên.
- Thư viện bên ngoài: matplotlib, numpy.

Để cài đặt các thư viện cần thiết, vui lòng mở Terminal (hoặc Command Prompt) 
tại thư mục chứa mã nguồn (thư mục Source/) và chạy lệnh sau:
    
    pip install -r requirements.txt


3. HƯỚNG DẪN SỬ DỤNG
--------------------
Dự án cung cấp 2 chế độ chạy: Giao diện trực quan (UI) và Giao diện dòng lệnh (Terminal).

CÁCH 1: Chạy Giao diện Trực quan (Khuyên dùng để chấm điểm & Theo dõi)
- Mở terminal tại thư mục Source/ và chạy lệnh:
    python futoshiki_ui.py
- Chức năng: 
  + Ứng dụng sẽ tự động quét thư mục để tìm các file input.
  + Người dùng có thể chọn thuật toán (BT, FC, BC, A*), điều chỉnh tốc độ (Speed).
  + Nhấn "▶ Solve" để xem thuật toán chạy từng bước (Visualizer).
  + Tab "📊 Benchmark" chứa biểu đồ so sánh hiệu năng thực tế của các thuật toán.

CÁCH 2: Chạy Chế độ Terminal (Dùng để Benchmark toàn bộ test case)
- Mở terminal tại thư mục Source/ và chạy lệnh:
    python futoshiki.py
- Chức năng: 
  + Chương trình sẽ đọc tất cả các file "input-*.txt" trong thư mục Inputs/.
  + Chạy ngầm cả 4 thuật toán để đo lường Thời gian, RAM, và số Nodes.
  + Ghi kết quả ma trận giải được (bằng thuật toán A*) ra thư mục Outputs/.
      ├── futoshiki_ui.py         : Code giao diện đồ họa (Visualizer & Charts)
      ├── requirements.txt        : Khai báo thư viện cần thiết
      └── README.txt              : File hướng dẫn này
================================================================================
