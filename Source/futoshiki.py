import os
import copy
import time

# =============================================================================
# PHẦN 1: CÁC HÀM XỬ LÝ ĐẦU VÀO / ĐẦU RA (I/O)
# =============================================================================

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

def extract_grid_from_assignment(assignment, N):
    """Dịch ngược kết quả biến logic (1 đến N^3) về lại ma trận N x N."""
    solved_grid = [[0 for _ in range(N)] for _ in range(N)]
    for var, is_true in assignment.items():
        if is_true:
            temp = var - 1
            v = (temp % N) + 1
            temp = temp // N
            j = (temp % N) + 1
            i = (temp // N) + 1
            solved_grid[i - 1][j - 1] = v
    return solved_grid

# =============================================================================
# PHẦN 2: CÁC HÀM SINH MÃ CNF (KNOWLEDGE BASE)
# =============================================================================

def get_var_id(i, j, v, N):
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
                if not (0 < v): clauses.append([-get_var_id(i, j, v, N)])
                if not (v < N + 1): clauses.append([-get_var_id(i, j, v, N)])
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

# =============================================================================
# PHẦN 3: THUẬT TOÁN 1 - BACKTRACKING (QUAY LUI CƠ BẢN DỰA TRÊN LƯỚI)
# =============================================================================

def find_empty_location(grid, N):
    """Tìm ô trống đầu tiên trong ma trận (trái sang phải, trên xuống dưới)."""
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0:
                return (i, j)
    return None

def is_safe(grid, row, col, num, N, horiz, vert):
    """Kiểm tra luật an toàn cơ bản (không dùng CNF)."""
    for j in range(N):
        if grid[row][j] == num: return False
    for i in range(N):
        if grid[i][col] == num: return False

    if col > 0 and grid[row][col - 1] != 0:
        if horiz[row][col - 1] == 1 and not (grid[row][col - 1] < num): return False
        if horiz[row][col - 1] == -1 and not (grid[row][col - 1] > num): return False

    if col < N - 1 and grid[row][col + 1] != 0:
        if horiz[row][col] == 1 and not (num < grid[row][col + 1]): return False
        if horiz[row][col] == -1 and not (num > grid[row][col + 1]): return False

    if row > 0 and grid[row - 1][col] != 0:
        if vert[row - 1][col] == 1 and not (grid[row - 1][col] < num): return False
        if vert[row - 1][col] == -1 and not (grid[row - 1][col] > num): return False

    if row < N - 1 and grid[row + 1][col] != 0:
        if vert[row][col] == 1 and not (num < grid[row + 1][col]): return False
        if vert[row][col] == -1 and not (num > grid[row + 1][col]): return False

    return True

def solve_backtracking(grid, N, horiz, vert):
    """Giải Futoshiki bằng Backtracking mảng truyền thống."""
    empty_pos = find_empty_location(grid, N)
    if not empty_pos: return True 
        
    row, col = empty_pos
    for num in range(1, N + 1):
        if is_safe(grid, row, col, num, N, horiz, vert):
            grid[row][col] = num
            if solve_backtracking(grid, N, horiz, vert): return True
            grid[row][col] = 0 
            
    return False

# =============================================================================
# PHẦN 4: THUẬT TOÁN 2 - FORWARD CHAINING (DPLL)
# =============================================================================

def unit_propagate(clauses, assignment):
    """Lan truyền sự kiện chắc chắn đúng để cắt tỉa logic (Forward Chaining)."""
    clauses_copy = [c[:] for c in clauses]  
    assignment_copy = assignment.copy()
    
    while True:
        unit_clause = None
        for clause in clauses_copy:
            if len(clause) == 1:
                unit_clause = clause[0]
                break
        
        if unit_clause is None: break
            
        var = abs(unit_clause)
        val = True if unit_clause > 0 else False
        
        if var in assignment_copy and assignment_copy[var] != val:
            return False, [], {} 
            
        assignment_copy[var] = val
        
        new_clauses = []
        for clause in clauses_copy:
            if unit_clause in clause:
                continue 
            elif -unit_clause in clause:
                new_clause = [l for l in clause if l != -unit_clause]
                if not new_clause: 
                    return False, [], {}
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)
                
        clauses_copy = new_clauses
        
    return True, clauses_copy, assignment_copy

def dpll_forward_chaining(clauses, assignment):
    """Khung thuật toán DPLL."""
    status, simplified_clauses, new_assignment = unit_propagate(clauses, assignment)
    
    if not status: return False, {} 
    if not simplified_clauses: return True, new_assignment 
        
    shortest_clause = min(simplified_clauses, key=len)
    chosen_var = abs(shortest_clause[0])

    if dpll_forward_chaining(simplified_clauses + [[chosen_var]], new_assignment)[0]: 
        return True, dpll_forward_chaining(simplified_clauses + [[chosen_var]], new_assignment)[1]
        
    if dpll_forward_chaining(simplified_clauses + [[-chosen_var]], new_assignment)[0]: 
        return True, dpll_forward_chaining(simplified_clauses + [[-chosen_var]], new_assignment)[1]
        
    return False, {}

# =============================================================================
# PHẦN 5: THUẬT TOÁN 3 - BACKWARD CHAINING TRUY VẤN Ô (PROLOG STYLE)
# =============================================================================

def build_horn_kb(clauses):
    """Trích xuất các mệnh đề Horn (đặc biệt là Fact) để chuẩn bị truy vấn."""
    horn_kb = {}
    for clause in clauses:
        pos_lits = [l for l in clause if l > 0]
        neg_lits = [-l for l in clause if l < 0]
        
        if len(pos_lits) == 1:
            head = pos_lits[0]
            if head not in horn_kb:
                horn_kb[head] = []
            horn_kb[head].append(neg_lits)
            
    return horn_kb

def fol_bc_ask(horn_kb, query_list, visited=None):
    """Thuật toán Suy diễn lùi (SLD Resolution) nguyên bản."""
    if visited is None: visited = set()
    if not query_list: return True

    q = query_list[0]
    rest_query = query_list[1:]

    if q in visited: return False
    visited.add(q)

    if q in horn_kb:
        for body in horn_kb[q]:
            new_query_list = body + rest_query
            if fol_bc_ask(horn_kb, new_query_list, visited.copy()):
                return True

    visited.remove(q)
    return False

def query_cell_backward_chaining(KB, i, j, v, N):
    """Dùng Backward Chaining để hỏi: Val(i, j) có phải là v không?"""
    target_var = get_var_id(i, j, v, N)
    horn_kb = build_horn_kb(KB)
    return fol_bc_ask(horn_kb, [target_var])

# =============================================================================
# PHẦN 6: CHƯƠNG TRÌNH CHÍNH (MAIN EXECUTION)
# =============================================================================

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "Inputs", "input-10.txt")
    
    try:
        # Bước 1: Đọc dữ liệu
        N, grid, horiz, vert = read_futoshiki_input(input_file)
        print(f"Kích thước ma trận N = {N}")
        print(f"Đang xử lý file: {os.path.basename(input_file)}")
        print("Đọc dữ liệu thành công!\n")
        
        # Bước 2: Sinh Knowledge Base (CNF)
        print("--- ĐANG SINH MÃ CNF CHO KNOWLEDGE BASE ---")
        KB = []
        KB.extend(generate_A1_at_least_one(N))
        KB.extend(generate_A2_at_most_one(N))
        KB.extend(generate_A3_value_in_bounds(N))
        KB.extend(generate_A4_maintain_given_values(N, grid))
        KB.extend(generate_A5_row_uniqueness(N))
        KB.extend(generate_A6_col_uniqueness(N))
        KB.extend(generate_A7_less_h(N, horiz))
        KB.extend(generate_A8_horizontal_greater(N, horiz))
        KB.extend(generate_A9_vertical_less(N, vert))
        KB.extend(generate_A10_greater_v(N, vert))
        
        print(f"Hoàn tất! Tổng số mệnh đề (clauses) trong KB: {len(KB)}\n")
        
        # -------------------------------------------------------------
        # THUẬT TOÁN 1: BACKTRACKING TRUYỀN THỐNG (TÌM KIẾM TOÀN BỘ MAP)
        # -------------------------------------------------------------
        print("="*60)
        print("1. KẾT QUẢ GIẢI BẰNG THUẬT TOÁN BACKTRACKING")
        print("="*60)
        
        grid_to_solve_bt = copy.deepcopy(grid)
        start_time_bt = time.time()
        is_solved_bt = solve_backtracking(grid_to_solve_bt, N, horiz, vert)
        end_time_bt = time.time()
        
        if is_solved_bt:
            print(f"Đã tìm thấy giải pháp! (Thời gian chạy: {end_time_bt - start_time_bt:.5f} giây)\n")
            print_solution(grid_to_solve_bt, N, horiz, vert)
        else:
            print("Không tìm thấy giải pháp nào cho cấu hình này!")

        # -------------------------------------------------------------
        # THUẬT TOÁN 2: FORWARD CHAINING / DPLL (TÌM KIẾM TOÀN BỘ MAP)
        # -------------------------------------------------------------
        print("\n" + "="*60)
        print("2. KẾT QUẢ GIẢI BẰNG FORWARD CHAINING (DPLL)")
        print("="*60)
        
        start_time_fc = time.time()
        is_solved_fc, final_assignment = dpll_forward_chaining(KB, {})
        end_time_fc = time.time()
        
        if is_solved_fc:
            print(f"Đã tìm thấy giải pháp! (Thời gian chạy: {end_time_fc - start_time_fc:.5f} giây)\n")
            solved_grid_fc = extract_grid_from_assignment(final_assignment, N)
            print_solution(solved_grid_fc, N, horiz, vert)
        else:
            print("Không tìm thấy giải pháp nào cho cấu hình này (Có thể KB chứa mâu thuẫn)!")
            
        # -------------------------------------------------------------
        # THUẬT TOÁN 3: BACKWARD CHAINING (TRUY VẤN - PROLOG STYLE)
        # -------------------------------------------------------------
        print("\n" + "="*60)
        print("3. KẾT QUẢ TRUY VẤN BẰNG BACKWARD CHAINING")
        print("="*60)
        
        # Tự động quét tìm một ô đã cho sẵn số (Given Clue) để làm test case truy vấn
        test_i, test_j, test_v = -1, -1, 0
        for r in range(N):
            for c in range(N):
                if grid[r][c] != 0:
                    test_i, test_j = r + 1, c + 1
                    test_v = grid[r][c]
                    break 
            if test_v != 0: 
                break 
        
        if test_v != 0:
            print(f"Đang truy vấn (SLD Resolution) xem Val({test_i}, {test_j}) có phải là {test_v} không...")
            is_proven = query_cell_backward_chaining(KB, test_i, test_j, test_v, N)
            
            if is_proven:
                print(f"-> SUY DIỄN THÀNH CÔNG: Val({test_i}, {test_j}, {test_v}) là ĐÚNG dựa trên KB.")
            else:
                print(f"-> THẤT BẠI: Không thể chứng minh bằng Backward Chaining.")
        else:
            print("Ma trận này trống hoàn toàn, không có số mồi nào để test truy vấn!")

    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {input_file}. Hãy kiểm tra lại cấu trúc thư mục!")