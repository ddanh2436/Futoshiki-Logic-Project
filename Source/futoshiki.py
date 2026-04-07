import os
import copy
import time

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

def unit_propagate(clauses, assignment):
    """
    Thuật toán Forward Chaining (Lan truyền đơn vị).
    Rút gọn tập mệnh đề dựa trên các sự kiện (mệnh đề đơn) đã biết.
    """
    clauses_copy = [c[:] for c in clauses]  
    assignment_copy = assignment.copy()
    
    while True:
        unit_clause = None
        # 1. Tìm mệnh đề đơn (Sự kiện chắc chắn đúng)
        for clause in clauses_copy:
            if len(clause) == 1:
                unit_clause = clause[0]
                break
        
        # Nếu không còn mệnh đề đơn, dừng suy diễn
        if unit_clause is None:
            break
            
        var = abs(unit_clause)
        val = True if unit_clause > 0 else False
        
        # 2. Kiểm tra mâu thuẫn
        if var in assignment_copy and assignment_copy[var] != val:
            return False, [], {} # Phát hiện mâu thuẫn
            
        assignment_copy[var] = val
        
        # 3. Lan truyền sự kiện mới (Propagate)
        new_clauses = []
        for clause in clauses_copy:
            if unit_clause in clause:
                continue # Mệnh đề đã đúng trọn vẹn -> Bỏ qua
            elif -unit_clause in clause:
                # Literal sai -> Xóa literal này khỏi mệnh đề
                new_clause = [l for l in clause if l != -unit_clause]
                if not new_clause: # Mệnh đề rỗng -> Mâu thuẫn
                    return False, [], {}
                new_clauses.append(new_clause)
            else:
                new_clauses.append(clause)
                
        clauses_copy = new_clauses
        
    return True, clauses_copy, assignment_copy

def dpll_forward_chaining(clauses, assignment):
    """
    Kết hợp Forward Chaining và tìm kiếm quay lui (DPLL).
    Đảm bảo giải quyết được mọi ma trận kích thước lớn.
    """
    # Bước 1: Lan truyền suy diễn tiến
    status, simplified_clauses, new_assignment = unit_propagate(clauses, assignment)
    
    if not status:
        return False, {} # Mâu thuẫn nhánh này, cần quay lui
        
    if not simplified_clauses:
        return True, new_assignment # Đã thỏa mãn toàn bộ Knowledge Base
        
    # Bước 2: Rẽ nhánh (Branching) nếu Forward Chaining bị "kẹt"
    # Chọn một biến bất kỳ chưa được gán (ở đây lấy biến đầu tiên của mệnh đề đầu tiên)
    shortest_clause = min(simplified_clauses, key=len)
    chosen_var = abs(shortest_clause[0])

    # Thử giả sử biến này True (Đưa vào KB như một sự kiện/mệnh đề đơn mới)
    status_true, final_assign_true = dpll_forward_chaining(simplified_clauses + [[chosen_var]], new_assignment)
    if status_true:
        return True, final_assign_true
        
    # Nếu True thất bại, thử False
    status_false, final_assign_false = dpll_forward_chaining(simplified_clauses + [[-chosen_var]], new_assignment)
    if status_false:
        return True, final_assign_false
        
    return False, {}
def build_horn_kb(clauses):
    """
    Tiền xử lý: Chuyển đổi tập CNF thành dạng từ điển Luật Horn để Suy diễn lùi dễ truy xuất.
    Cấu trúc: KB_Dict[Head] = [Body1, Body2, ...] (Mỗi Body là một danh sách các điều kiện)
    """
    horn_kb = {}
    for clause in clauses:
        pos_lits = [l for l in clause if l > 0]
        neg_lits = [-l for l in clause if l < 0]
        
        # Chỉ lấy các mệnh đề Horn (có đúng 1 literal khẳng định làm "Head")
        if len(pos_lits) == 1:
            head = pos_lits[0]
            if head not in horn_kb:
                horn_kb[head] = []
            # Thêm phần "Body" (tiền đề) vào danh sách các cách để chứng minh "Head"
            horn_kb[head].append(neg_lits)
            
    return horn_kb

def fol_bc_ask(horn_kb, query_list, visited=None):
    """
    Thuật toán Suy diễn lùi (Backward Chaining) mô phỏng SLD Resolution.
    Tương đương với hàm FOL-BC-ASK trong sách giáo trình.
    
    :param horn_kb: Cơ sở tri thức dạng luật Horn.
    :param query_list: (truy-vấn) Danh sách các mục tiêu cần chứng minh.
    :param visited: Tập hợp các node đã duyệt để chống lặp vòng vô hạn.
    :return: True nếu chứng minh thành công, False nếu thất bại.
    """
    if visited is None:
        visited = set()

    # if truy-vấn rỗng then return thành công (Tất cả mục tiêu đã được chứng minh)
    if not query_list:
        return True

    # Lấy câu hỏi đích đầu tiên (q')
    q = query_list[0]
    rest_query = query_list[1:]

    # Chống lặp: Nếu mục tiêu này đang nằm trong chuỗi chứng minh hiện tại, bỏ qua
    if q in visited:
        return False

    visited.add(q)

    # for each câu r in KB trong đó phần kết luận đồng nhất với q
    if q in horn_kb:
        for body in horn_kb[q]:
            # truy-vấn-mới <- [Phần tiền đề của r, Phần còn lại của truy vấn]
            new_query_list = body + rest_query
            
            # Đệ quy giải quyết truy vấn mới
            if fol_bc_ask(horn_kb, new_query_list, visited.copy()):
                return True

    visited.remove(q)
    return False

def query_cell_backward_chaining(KB, i, j, v, N):
    """
    Hàm giao tiếp: Truy vấn xem ô (i, j) có thể chắc chắn mang giá trị v hay không.
    """
    target_var = get_var_id(i, j, v, N)
    horn_kb = build_horn_kb(KB)
    
    # Bắt đầu truy vấn với mục tiêu duy nhất là target_var
    result = fol_bc_ask(horn_kb, [target_var])
    return result

def extract_grid_from_assignment(assignment, N):
    """
    Dịch ngược kết quả biến logic (1 đến N^3) về lại ma trận N x N.
    """
    solved_grid = [[0 for _ in range(N)] for _ in range(N)]
    for var, is_true in assignment.items():
        if is_true:
            # Dịch ngược công thức get_var_id
            temp = var - 1
            v = (temp % N) + 1
            temp = temp // N
            j = (temp % N) + 1
            i = (temp // N) + 1
            solved_grid[i - 1][j - 1] = v
    return solved_grid

if __name__ == "__main__":
    # 1. Lấy thư mục chứa file futoshiki.py hiện tại
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Tạo đường dẫn tuyệt đối đến file input
    input_file = os.path.join(script_dir, "Inputs", "input-10.txt")
    
    try:
        # Bước 1: Đọc dữ liệu
        N, grid, horiz, vert = read_futoshiki_input(input_file)
        
        print(f"Kích thước ma trận N = {N}")
        print("Đọc dữ liệu thành công!\n")
        
        # Bước 2: Sinh Knowledge Base (CNF) chung cho Forward Chaining
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
        
        # ==============================================================
        # PHẦN 1: GIẢI BẰNG THUẬT TOÁN BACKTRACKING
        # ==============================================================
        print("="*60)
        print("1. KẾT QUẢ GIẢI BẰNG THUẬT TOÁN BACKTRACKING")
        print("="*60)
        
        # Tạo một bản sao của grid để Backtracking không làm hỏng dữ liệu gốc
        grid_to_solve_bt = copy.deepcopy(grid)
        
        start_time_bt = time.time()
        is_solved_bt = solve_backtracking(grid_to_solve_bt, N, horiz, vert)
        end_time_bt = time.time()
        
        if is_solved_bt:
            print(f"Đã tìm thấy giải pháp! (Thời gian chạy: {end_time_bt - start_time_bt:.5f} giây)\n")
            print_solution(grid_to_solve_bt, N, horiz, vert)
        else:
            print("Không tìm thấy giải pháp nào cho cấu hình này!")

        print("\n")

        # ==============================================================
        # PHẦN 2: GIẢI BẰNG THUẬT TOÁN FORWARD CHAINING (DPLL)
        # ==============================================================
        print("="*60)
        print("2. KẾT QUẢ GIẢI BẰNG FORWARD CHAINING (DPLL)")
        print("="*60)
        
        start_time_fc = time.time()
        # Gọi hàm DPLL với KB ban đầu và tập gán (assignment) rỗng
        is_solved_fc, final_assignment = dpll_forward_chaining(KB, {})
        end_time_fc = time.time()
        
        if is_solved_fc:
            print(f"Đã tìm thấy giải pháp! (Thời gian chạy: {end_time_fc - start_time_fc:.5f} giây)\n")
            solved_grid_fc = extract_grid_from_assignment(final_assignment, N)
            print_solution(solved_grid_fc, N, horiz, vert)
        else:
            print("Không tìm thấy giải pháp nào cho cấu hình này (Có thể KB chứa mâu thuẫn)!")
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {input_file}. Hãy kiểm tra lại cấu trúc thư mục!")
        
        # ==============================================================
        # PHẦN 3: DEMO TRUY VẤN BẰNG BACKWARD CHAINING (PROLOG-STYLE)
        # ==============================================================
        print("\n" + "="*60)
        print("3. KẾT QUẢ TRUY VẤN BẰNG BACKWARD CHAINING")
        print("="*60)
        
        # Ví dụ: Thử truy vấn giá trị của một ô đã cho sẵn (Given Clue)
        # Em có thể lấy tọa độ của một ô có số > 0 trong file input để test
        test_i, test_j = 1, 1 
        test_v = grid[test_i - 1][test_j - 1] 
        
        if test_v != 0:
            print(f"Đang truy vấn (SLD Resolution) xem Val({test_i}, {test_j}) có phải là {test_v} không...")
            is_proven = query_cell_backward_chaining(KB, test_i, test_j, test_v, N)
            
            if is_proven:
                print(f"-> SUY DIỄN THÀNH CÔNG: Val({test_i}, {test_j}, {test_v}) là ĐÚNG dựa trên KB.")
            else:
                print(f"-> THẤT BẠI: Không thể chứng minh bằng Backward Chaining.")

