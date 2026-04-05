import os

def read_futoshiki_input(file_path):
    """Đọc dữ liệu từ file input Futoshiki."""
    with open(file_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    N = int(lines[0])
    current_line = 1
    
    grid = []
    for _ in range(N):
        row = list(map(int, lines[current_line].split(',')))
        grid.append(row)
        current_line += 1
        
    horiz_constraints = []
    for _ in range(N):
        row = list(map(int, lines[current_line].split(',')))
        horiz_constraints.append(row)
        current_line += 1
        
    vert_constraints = []
    for _ in range(N - 1):
        row = list(map(int, lines[current_line].split(',')))
        vert_constraints.append(row)
        current_line += 1
        
    return N, grid, horiz_constraints, vert_constraints

def get_var_id(i, j, v, N):
    """
    Ánh xạ tọa độ (hàng i, cột j, giá trị v) thành một số nguyên duy nhất cho chuẩn CNF.
    Lưu ý: i, j, v trong công thức toán học bắt đầu từ 1.
    """
    return (i - 1) * N**2 + (j - 1) * N + v

def generate_A3_value_in_bounds(N):
    """
    A3: Giá trị v phải nằm trong khoảng từ 1 đến N.
    CNF 1: ~Val(i, j, v) V Less(0, v)
    CNF 2: ~Val(i, j, v) V Less(v, N+1)
    """
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                
                # Mệnh đề 1: ~Val(i, j, v) V Less(0, v)
                # Ý nghĩa code: Nếu điều kiện Less(0, v) là Sai, ta phải cấm Val(i, j, v)
                if not (0 < v):
                    clauses.append([-get_var_id(i, j, v, N)])
                
                # Mệnh đề 2: ~Val(i, j, v) V Less(v, N + 1)
                # Ý nghĩa code: Nếu điều kiện Less(v, N+1) là Sai, ta cũng phải cấm Val(i, j, v)
                if not (v < N + 1):
                    clauses.append([-get_var_id(i, j, v, N)])
                    
    return clauses

def generate_A4_maintain_given_values(N, grid):
    """
    A4: Duy trì các giá trị đã cho.
    Nếu ô (i, j) đã có giá trị v trong grid, thì Val(i, j, v) phải đúng.
    """
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            v = grid[i - 1][j - 1]
            if v != 0:  # Nếu ô đã có giá trị (không phải 0)
                clause = [get_var_id(i, j, v, N)]  # Val(i, j, v) phải đúng
                clauses.append(clause)
    return clauses

def generate_A5_row_uniqueness(N):
    """
    A5: Tính duy nhất của hàng. 
    Không có 2 ô trên cùng 1 hàng có cùng giá trị.
    """
    clauses = []
    for i in range(1, N + 1):
        for v in range(1, N + 1):
            for j1 in range(1, N + 1):
                for j2 in range(j1 + 1, N + 1):
                    # CNF: ~Val(i, j1, v) OR ~Val(i, j2, v)
                    clause = [-get_var_id(i, j1, v, N), -get_var_id(i, j2, v, N)]
                    clauses.append(clause)
    return clauses

def generate_A8_horizontal_greater(N, horiz_constraints):
    """
    A8: Ràng buộc lớn hơn theo chiều ngang.
    Nếu horiz_constraints tại tọa độ đó là 1 (ô trái > ô phải).
    """
    clauses = []
    for r in range(N):
        for c in range(N - 1):
            if horiz_constraints[r][c] == -1:
                row = r + 1          # Tọa độ i
                col_left = c + 1     # Tọa độ j
                col_right = c + 2    # Tọa độ j+1
                
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        # Nếu v1 <= v2 thì đây là tổ hợp vi phạm luật, ta cần cấm (phủ định) nó
                        if v1 <= v2:
                            # CNF: ~Val(row, col_left, v1) OR ~Val(row, col_right, v2)
                            clause = [-get_var_id(row, col_left, v1, N), -get_var_id(row, col_right, v2, N)]
                            clauses.append(clause)
    return clauses

def generate_A9_vertical_less(N, vert_constraints):
    """
    A9: Ràng buộc nhỏ hơn theo chiều dọc.
    Nếu vert_constraints tại tọa độ đó là 1 (ô trên < ô dưới).
    """
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert_constraints[r][c] == 1:
                row_top = r + 1      # Tọa độ i
                row_bottom = r + 2   # Tọa độ i+1
                col = c + 1          # Tọa độ j
                
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        # Nếu v1 >= v2 thì đây là tổ hợp vi phạm luật, ta cần cấm (phủ định) nó
                        if v1 >= v2:
                            # CNF: ~Val(row_top, col, v1) OR ~Val(row_bottom, col, v2)
                            clause = [-get_var_id(row_top, col, v1, N), -get_var_id(row_bottom, col, v2, N)]
                            clauses.append(clause)
    return clauses

def generate_A10_greater_v(N, vert_constraints):
    """
    A10: Ràng buộc lớn hơn theo chiều dọc.
    Nếu vert_constraints tại tọa độ đó là -1 (ô trên > ô dưới).
    """
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert_constraints[r][c] == -1:
                row_top = r + 1      # Tọa độ i
                row_bottom = r + 2   # Tọa độ i+1
                col = c + 1          # Tọa độ j
                
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        # Nếu v1 <= v2 thì đây là tổ hợp vi phạm luật, ta cần cấm (phủ định) nó
                        if v1 <= v2:
                            # CNF: ~Val(row_top, col, v1) OR ~Val(row_bottom, col, v2)
                            clause = [-get_var_id(row_top, col, v1, N), -get_var_id(row_bottom, col, v2, N)]
                            clauses.append(clause)
    return clauses

# --- CHƯƠNG TRÌNH CHÍNH ---
if __name__ == "__main__":
    input_file = os.path.join("Inputs", "input-01.txt")
    
    try:
        # Bước 1: Đọc dữ liệu từ file
        N, grid, horiz, vert = read_futoshiki_input(input_file)
        
        print(f"Kích thước ma trận N = {N}")
        print("Đọc dữ liệu thành công! Đang chuyển sang tạo Knowledge Base...")
        
        # Bước 2: Sinh các tập mệnh đề (Clauses) cho Knowledge Base
        print("\n--- BẮT ĐẦU SINH MÃ CNF ---")
        
        a3_clauses = generate_A3_value_in_bounds(N)
        print(f"[A3] Giới hạn giá trị 1 đến N: {len(a3_clauses)} mệnh đề")
        
        a4_clauses = generate_A4_maintain_given_values(N, grid)
        print(f"[A4] Giữ nguyên các ô cho sẵn: {len(a4_clauses)} mệnh đề")

        a5_clauses = generate_A5_row_uniqueness(N)
        print(f"[A5] Tính duy nhất của hàng: {len(a5_clauses)} mệnh đề")
        if len(a5_clauses) > 0: print(f"     Ví dụ: {a5_clauses[0]}")
        
        a8_clauses = generate_A8_horizontal_greater(N, horiz)
        print(f"[A8] Ràng buộc '>' ngang: {len(a8_clauses)} mệnh đề")
        if len(a8_clauses) > 0: print(f"     Ví dụ: {a8_clauses[0]}")
            
        a9_clauses = generate_A9_vertical_less(N, vert)
        print(f"[A9] Ràng buộc '<' dọc: {len(a9_clauses)} mệnh đề")
        if len(a9_clauses) > 0: print(f"     Ví dụ: {a9_clauses[0]}")
        
        a10_clauses = generate_A10_greater_v(N, vert)
        print(f"[A10] Ràng buộc '>' dọc: {len(a10_clauses)} mệnh đề")
        if len(a10_clauses) > 0: print(f"     Ví dụ: {a10_clauses[0]}")
            
        # Gộp tất cả vào một Knowledge Base chung
        KB = a3_clauses + a4_clauses + a5_clauses + a8_clauses + a9_clauses + a10_clauses
        print(f"\n--- TỔNG KẾT ---")
        print(f"Tổng số mệnh đề (clauses) hiện có trong KB: {len(KB)}")
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {input_file}. Hãy kiểm tra lại cấu trúc thư mục!")