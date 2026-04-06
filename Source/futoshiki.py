import os
import copy


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
    """Ánh xạ tọa độ (hàng i, cột j, giá trị v) thành một số nguyên duy nhất cho chuẩn CNF."""
    return (i - 1) * N**2 + (j - 1) * N + v

def generate_A1_at_least_one(N):
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            clause = [get_var_id(i, j, v, N) for v in range(1, N + 1)]
            clauses.append(clause)
    return clauses

def generate_A2_at_most_one(N):
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            for v1 in range(1, N + 1):
                for v2 in range(v1 + 1, N + 1):
                    clause = [-get_var_id(i, j, v1, N), -get_var_id(i, j, v2, N)]
                    clauses.append(clause)
    return clauses

def generate_A3_value_in_bounds(N):
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                if not (0 < v):
                    clauses.append([-get_var_id(i, j, v, N)])
                if not (v < N + 1):
                    clauses.append([-get_var_id(i, j, v, N)])
    return clauses

def generate_A4_maintain_given_values(N, grid):
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            v = grid[i - 1][j - 1]
            if v != 0:
                clause = [get_var_id(i, j, v, N)]
                clauses.append(clause)
    return clauses

def generate_A5_row_uniqueness(N):
    clauses = []
    for i in range(1, N + 1):
        for v in range(1, N + 1):
            for j1 in range(1, N + 1):
                for j2 in range(j1 + 1, N + 1):
                    clause = [-get_var_id(i, j1, v, N), -get_var_id(i, j2, v, N)]
                    clauses.append(clause)
    return clauses

def generate_A6_col_uniqueness(N):
    clauses = []
    for j in range(1, N + 1):
        for v in range(1, N + 1):
            for i1 in range(1, N + 1):
                for i2 in range(i1 + 1, N + 1):
                    clause = [-get_var_id(i1, j, v, N), -get_var_id(i2, j, v, N)]
                    clauses.append(clause)
    return clauses

def generate_A7_less_h(N, horiz_constraints):
    clauses = []
    for r in range(N):
        for c in range(N - 1):
            if horiz_constraints[r][c] == 1:
                row, col_left, col_right = r + 1, c + 1, c + 2
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        if v1 >= v2:
                            clause = [-get_var_id(row, col_left, v1, N), -get_var_id(row, col_right, v2, N)]
                            clauses.append(clause)
    return clauses

def generate_A8_horizontal_greater(N, horiz_constraints):
    clauses = []
    for r in range(N):
        for c in range(N - 1):
            if horiz_constraints[r][c] == -1:
                row, col_left, col_right = r + 1, c + 1, c + 2
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        if v1 <= v2:
                            clause = [-get_var_id(row, col_left, v1, N), -get_var_id(row, col_right, v2, N)]
                            clauses.append(clause)
    return clauses

def generate_A9_vertical_less(N, vert_constraints):
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert_constraints[r][c] == 1:
                row_top, row_bottom, col = r + 1, r + 2, c + 1
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        if v1 >= v2:
                            clause = [-get_var_id(row_top, col, v1, N), -get_var_id(row_bottom, col, v2, N)]
                            clauses.append(clause)
    return clauses

def generate_A10_greater_v(N, vert_constraints):
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert_constraints[r][c] == -1:
                row_top, row_bottom, col = r + 1, r + 2, c + 1
                for v1 in range(1, N + 1):
                    for v2 in range(1, N + 1):
                        if v1 <= v2:
                            clause = [-get_var_id(row_top, col, v1, N), -get_var_id(row_bottom, col, v2, N)]
                            clauses.append(clause)
    return clauses


def find_empty_location(grid, N):
    """Tìm ô trống đầu tiên trong ma trận (trái sang phải, trên xuống dưới)."""
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0:
                return (i, j)
    return None

def is_safe(grid, row, col, num, N, horiz, vert):
    """Kiểm tra xem việc điền 'num' vào tọa độ (row, col) có hợp lệ không."""
    # 1. Tiên đề A5 (Duy nhất hàng)
    for j in range(N):
        if grid[row][j] == num:
            return False

    # 2. Tiên đề A6 (Duy nhất cột)
    for i in range(N):
        if grid[i][col] == num:
            return False

    # 3. Tiên đề A7, A8 (Ràng buộc ngang)
    if col > 0 and grid[row][col - 1] != 0:
        if horiz[row][col - 1] == 1 and not (grid[row][col - 1] < num): return False
        if horiz[row][col - 1] == -1 and not (grid[row][col - 1] > num): return False

    if col < N - 1 and grid[row][col + 1] != 0:
        if horiz[row][col] == 1 and not (num < grid[row][col + 1]): return False
        if horiz[row][col] == -1 and not (num > grid[row][col + 1]): return False

    # 4. Tiên đề A9, A10 (Ràng buộc dọc)
    if row > 0 and grid[row - 1][col] != 0:
        if vert[row - 1][col] == 1 and not (grid[row - 1][col] < num): return False
        if vert[row - 1][col] == -1 and not (grid[row - 1][col] > num): return False

    if row < N - 1 and grid[row + 1][col] != 0:
        if vert[row][col] == 1 and not (num < grid[row + 1][col]): return False
        if vert[row][col] == -1 and not (num > grid[row + 1][col]): return False

    return True

def solve_backtracking(grid, N, horiz, vert):
    """Hàm đệ quy để giải lưới Futoshiki bằng Backtracking."""
    empty_pos = find_empty_location(grid, N)
    if not empty_pos:
        return True # Đã giải xong
        
    row, col = empty_pos

    for num in range(1, N + 1):
        if is_safe(grid, row, col, num, N, horiz, vert):
            grid[row][col] = num
            if solve_backtracking(grid, N, horiz, vert):
                return True
            grid[row][col] = 0 # Quay lui
            
    return False

def print_solution(grid, N, horiz, vert):
    """In ma trận kết quả kèm theo các dấu bất đẳng thức."""
    for r in range(N):
        row_str = ""
        for c in range(N):
            row_str += f"{grid[r][c]:2d} "
            if c < N - 1:
                if horiz[r][c] == 1: row_str += "< "
                elif horiz[r][c] == -1: row_str += "> "
                else: row_str += "  "
        print(row_str)
        
        if r < N - 1:
            vert_str = ""
            for c in range(N):
                if vert[r][c] == 1: vert_str += " ^   "
                elif vert[r][c] == -1: vert_str += " v   "
                else: vert_str += "     "
            print(vert_str)

if __name__ == "__main__":
    # Đảm bảo đường dẫn file chính xác với cấu trúc thư mục của bạn
    input_file = os.path.join("Inputs", "input-01.txt")
    
    try:
        # Bước 1: Đọc dữ liệu
        N, grid, horiz, vert = read_futoshiki_input(input_file)
        
        print(f"Kích thước ma trận N = {N}")
        print("Đọc dữ liệu thành công!\n")
        
        # Bước 2: Sinh Knowledge Base (CNF)
        print("--- ĐANG SINH MÃ CNF CHO KNOWLEDGE BASE ---")
        a1 = generate_A1_at_least_one(N)
        a2 = generate_A2_at_most_one(N)
        a3 = generate_A3_value_in_bounds(N)
        a4 = generate_A4_maintain_given_values(N, grid)
        a5 = generate_A5_row_uniqueness(N)
        a6 = generate_A6_col_uniqueness(N)
        a7 = generate_A7_less_h(N, horiz)
        a8 = generate_A8_horizontal_greater(N, horiz)
        a9 = generate_A9_vertical_less(N, vert)
        a10 = generate_A10_greater_v(N, vert)
        
        KB = a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8 + a9 + a10
        print(f"Hoàn tất! Tổng số mệnh đề (clauses) trong KB: {len(KB)}\n")
        
        # Bước 3: Giải bài toán bằng Backtracking
        print("--- KẾT QUẢ GIẢI BẰNG THUẬT TOÁN BACKTRACKING ---")
        grid_to_solve = copy.deepcopy(grid)
        
        is_solved = solve_backtracking(grid_to_solve, N, horiz, vert)
        
        if is_solved:
            print("Đã tìm thấy giải pháp!\n")
            print_solution(grid_to_solve, N, horiz, vert)
        else:
            print("Không tìm thấy giải pháp nào cho cấu hình này!")
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {input_file}. Hãy kiểm tra lại cấu trúc thư mục!")