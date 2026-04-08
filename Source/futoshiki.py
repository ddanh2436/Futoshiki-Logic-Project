import os
import copy
import time
import heapq
import itertools
import glob
import tracemalloc

# =============================================================================
# PHẦN 1: CÁC HÀM XỬ LÝ ĐẦU VÀO / ĐẦU RA (I/O)
# =============================================================================

def read_futoshiki_input(file_path):
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

def write_solution_to_file(grid, N, horiz, vert, filepath):
    with open(filepath, 'w') as f:
        for r in range(N):
            row_str = ""
            for c in range(N):
                row_str += f"{grid[r][c]:2d} "
                if c < N - 1:
                    if horiz[r][c] == 1: row_str += "< "
                    elif horiz[r][c] == -1: row_str += "> "
                    else: row_str += "  "
            f.write(row_str + "\n")
            
            if r < N - 1:
                vert_str = ""
                for c in range(N):
                    if vert[r][c] == 1: vert_str += " ^   "
                    elif vert[r][c] == -1: vert_str += " v   "
                    else: vert_str += "     "
                f.write(vert_str + "\n")

# =============================================================================
# PHẦN 2: CÁC HÀM SINH MÃ CNF (KNOWLEDGE BASE)
# =============================================================================

def get_var_id(i, j, v, N):
    return (i - 1) * N**2 + (j - 1) * N + v

def generate_A1_at_least_one(N):
    return [[get_var_id(i, j, v, N) for v in range(1, N + 1)] for i in range(1, N + 1) for j in range(1, N + 1)]

def generate_A2_at_most_one(N):
    return [[-get_var_id(i, j, v1, N), -get_var_id(i, j, v2, N)] for i in range(1, N + 1) for j in range(1, N + 1) for v1 in range(1, N + 1) for v2 in range(v1 + 1, N + 1)]

def generate_A3_value_in_bounds(N):
    clauses = []
    for i in range(1, N + 1):
        for j in range(1, N + 1):
            for v in range(1, N + 1):
                if not (0 < v): clauses.append([-get_var_id(i, j, v, N)])
                if not (v < N + 1): clauses.append([-get_var_id(i, j, v, N)])
    return clauses

def generate_A4_maintain_given_values(N, grid):
    return [[get_var_id(i, j, grid[i-1][j-1], N)] for i in range(1, N + 1) for j in range(1, N + 1) if grid[i-1][j-1] != 0]

def generate_A5_row_uniqueness(N):
    return [[-get_var_id(i, j1, v, N), -get_var_id(i, j2, v, N)] for i in range(1, N + 1) for v in range(1, N + 1) for j1 in range(1, N + 1) for j2 in range(j1 + 1, N + 1)]

def generate_A6_col_uniqueness(N):
    return [[-get_var_id(i1, j, v, N), -get_var_id(i2, j, v, N)] for j in range(1, N + 1) for v in range(1, N + 1) for i1 in range(1, N + 1) for i2 in range(i1 + 1, N + 1)]

def generate_A7_less_h(N, horiz):
    clauses = []
    for r in range(N):
        for c in range(N - 1):
            if horiz[r][c] == 1:
                for v1 in range(1, N + 1):
                    for v2 in range(1, v1 + 1):
                        clauses.append([-get_var_id(r+1, c+1, v1, N), -get_var_id(r+1, c+2, v2, N)])
    return clauses

def generate_A8_horizontal_greater(N, horiz):
    clauses = []
    for r in range(N):
        for c in range(N - 1):
            if horiz[r][c] == -1:
                for v1 in range(1, N + 1):
                    for v2 in range(v1, N + 1):
                        clauses.append([-get_var_id(r+1, c+1, v1, N), -get_var_id(r+1, c+2, v2, N)])
    return clauses

def generate_A9_vertical_less(N, vert):
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert[r][c] == 1:
                for v1 in range(1, N + 1):
                    for v2 in range(1, v1 + 1):
                        clauses.append([-get_var_id(r+1, c+1, v1, N), -get_var_id(r+2, c+1, v2, N)])
    return clauses

def generate_A10_greater_v(N, vert):
    clauses = []
    for r in range(N - 1):
        for c in range(N):
            if vert[r][c] == -1:
                for v1 in range(1, N + 1):
                    for v2 in range(v1, N + 1):
                        clauses.append([-get_var_id(r+1, c+1, v1, N), -get_var_id(r+2, c+1, v2, N)])
    return clauses

def build_full_kb(N, grid, horiz, vert):
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
    return KB

# =============================================================================
# CÁC HÀM TIỆN ÍCH CHUNG
# =============================================================================

def find_empty_location(grid, N):
    for i in range(N):
        for j in range(N):
            if grid[i][j] == 0: return (i, j)
    return None

def is_safe(grid, row, col, num, N, horiz, vert):
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

# =============================================================================
# BENCHMARK WRAPPER (ĐO TIME & RAM)
# =============================================================================
def run_benchmark(func, *args):
    """Hàm bọc để đo RAM và Thời gian thực thi của một hàm thuật toán"""
    tracemalloc.start()
    start_time = time.perf_counter()
    
    result = func(*args)
    
    end_time = time.perf_counter()
    exec_time = end_time - start_time
    
    current_ram, peak_ram = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_ram_mb = peak_ram / (1024 * 1024)
    
    return result, exec_time, peak_ram_mb

# =============================================================================
# THUẬT TOÁN 1: BACKTRACKING (KÈM ĐẾM NODE)
# =============================================================================

def run_backtracking(grid, N, horiz, vert):
    stats = [0] # List để truyền tham chiếu đếm node
    
    def solve_bt(curr_grid):
        stats[0] += 1
        empty_pos = find_empty_location(curr_grid, N)
        if not empty_pos: return True 
        row, col = empty_pos
        for num in range(1, N + 1):
            if is_safe(curr_grid, row, col, num, N, horiz, vert):
                curr_grid[row][col] = num
                if solve_bt(curr_grid): return True
                curr_grid[row][col] = 0 
        return False
        
    res = solve_bt(grid)
    return res, stats[0]

# =============================================================================
# THUẬT TOÁN 2: FORWARD CHAINING (DPLL KÈM ĐẾM SUY DIỄN)
# =============================================================================

def unit_propagate(clauses, assignment):
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

def run_dpll(clauses):
    stats = [0] # Đếm số nhánh DPLL
    
    def dpll_recursive(cls, asn):
        stats[0] += 1
        status, simplified_clauses, new_assignment = unit_propagate(cls, asn)
        if not status: return False, {} 
        if not simplified_clauses: return True, new_assignment 
            
        shortest_clause = min(simplified_clauses, key=len)
        chosen_var = abs(shortest_clause[0])

        # Sửa lỗi: Gán biến tạm thay vì gọi đệ quy 2 lần giống code cũ
        res1, asn1 = dpll_recursive(simplified_clauses + [[chosen_var]], new_assignment)
        if res1: return True, asn1
        
        res2, asn2 = dpll_recursive(simplified_clauses + [[-chosen_var]], new_assignment)
        if res2: return True, asn2
        
        return False, {}

    res, final_asn = dpll_recursive(clauses, {})
    return res, final_asn, stats[0]

# =============================================================================
# THUẬT TOÁN 3: BACKWARD CHAINING (PROLOG STYLE)
# =============================================================================

def build_horn_kb(clauses):
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

def run_backward_chaining(KB, i, j, v, N):
    horn_kb = build_horn_kb(KB)
    target_var = get_var_id(i, j, v, N)
    stats = [0] # Đếm số phép suy diễn lùi
    
    def fol_bc_ask(query_list, visited):
        stats[0] += 1
        if not query_list: return True
        q = query_list[0]
        rest_query = query_list[1:]
        if q in visited: return False
        visited.add(q)
        if q in horn_kb:
            for body in horn_kb[q]:
                new_query_list = body + rest_query
                if fol_bc_ask(new_query_list, visited.copy()):
                    return True
        visited.remove(q)
        return False
        
    res = fol_bc_ask([target_var], set())
    return res, stats[0]


def get_heuristic_and_mrv(grid, N, horiz, vert):
    empty_count = 0
    min_options = N + 1
    best_pos = None

    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                empty_count += 1
                # Đếm số giá trị hợp lệ (Forward Checking)
                options = sum(1 for v in range(1, N + 1) if is_safe(grid, r, c, v, N, horiz, vert))
                
                if options == 0:
                    return float('inf'), None  # Nhánh vô nghiệm, cắt tỉa ngay
                
                if options < min_options:
                    min_options = options
                    best_pos = (r, c)
                    
    return empty_count, best_pos

def run_astar(initial_grid, N, horiz, vert):
    initial_g = sum(1 for r in range(N) for c in range(N) if initial_grid[r][c] != 0)
    initial_h, initial_mrv = get_heuristic_and_mrv(initial_grid, N, horiz, vert)
    
    if initial_h == float('inf'): return False, None, 0
        
    pq = []
    tie_breaker = itertools.count() 
    # MẸO: Lưu sẵn initial_mrv vào tuple để khỏi phải tính lại
    heapq.heappush(pq, (initial_g + initial_h, -initial_g, next(tie_breaker), initial_grid, initial_mrv))
    nodes_expanded = 0 
    
    while pq:
        # Lấy trực tiếp empty_pos từ queue
        f, neg_g, _, current_grid, empty_pos = heapq.heappop(pq)
        g = -neg_g
        nodes_expanded += 1
        
        if not empty_pos: return True, current_grid, nodes_expanded
        
        row, col = empty_pos
        for num in range(1, N + 1):
            if is_safe(current_grid, row, col, num, N, horiz, vert):
                child_grid = [r[:] for r in current_grid]
                child_grid[row][col] = num
                child_g = g + 1
                
                # Tính trước thông số cho node con
                child_h, child_mrv = get_heuristic_and_mrv(child_grid, N, horiz, vert)
                
                if child_h != float('inf'):
                    heapq.heappush(pq, (child_g + child_h, -child_g, next(tie_breaker), child_grid, child_mrv))
                    
    return False, None, nodes_expanded



if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "Inputs")
    output_folder = os.path.join(script_dir, "Outputs")
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    input_files = sorted(glob.glob(os.path.join(input_folder, "input-*.txt")))
    
    if not input_files:
        print(f"Không tìm thấy file input nào trong thư mục {input_folder}")
        exit()

    results = []
    print("BẮT ĐẦU CHẠY KIỂM THỬ VÀ ĐO LƯỜNG HIỆU NĂNG...\n")

    for file_path in input_files:
        filename = os.path.basename(file_path)
        N, grid, horiz, vert = read_futoshiki_input(file_path)
        
        print(f"[{filename}] - Kích thước {N}x{N} - Đang xử lý...")
        
        # --- Gen KB ---
        KB = build_full_kb(N, grid, horiz, vert)

        # 1. Backtracking
        grid_bt = copy.deepcopy(grid)
        (res_bt, nodes_bt), t_bt, ram_bt = run_benchmark(run_backtracking, grid_bt, N, horiz, vert)
        
        # 2. Forward Chaining (DPLL)
        (res_fc, _, nodes_fc), t_fc, ram_fc = run_benchmark(run_dpll, KB)

        # 3. Backward Chaining (Test 1 ô mồi)
        test_i, test_j, test_v = -1, -1, 0
        for r in range(N):
            for c in range(N):
                if grid[r][c] != 0:
                    test_i, test_j, test_v = r + 1, c + 1, grid[r][c]
                    break
            if test_v != 0: break
        
        if test_v != 0:
            (res_bc, nodes_bc), t_bc, ram_bc = run_benchmark(run_backward_chaining, KB, test_i, test_j, test_v, N)
        else:
            t_bc, ram_bc, nodes_bc = 0, 0, 0

        # 4. A* Search
        grid_astar = copy.deepcopy(grid)
        (res_astar, final_grid_astar, nodes_astar), t_astar, ram_astar = run_benchmark(run_astar, grid_astar, N, horiz, vert)
        
        # Ghi file Output (Lấy theo kết quả của A*)
        if res_astar:
            out_filename = filename.replace("input-", "output-")
            out_filepath = os.path.join(output_folder, out_filename)
            write_solution_to_file(final_grid_astar, N, horiz, vert, out_filepath)
            print(f"--> Đã tìm thấy nghiệm & lưu vào: Outputs/{out_filename}")
        else:
            print("--> Ma trận vô nghiệm.")
        
        # Lưu số liệu
        results.append({
            "File": filename, "Size": f"{N}x{N}",
            "BT": (t_bt, ram_bt, nodes_bt),
            "FC": (t_fc, ram_fc, nodes_fc),
            "BC": (t_bc, ram_bc, nodes_bc),
            "AStar": (t_astar, ram_astar, nodes_astar)
        })
        print("-" * 50)

    # =========================================================================
    # IN BẢNG TỔNG KẾT SIÊU RỘNG (TIME / RAM / NODES)
    # =========================================================================
    # T(s) = Time in seconds | R(MB) = Peak RAM in MB | Nodes = Nodes expanded / Inferences made
    
    print("\n" + "="*160)
    print(f"{'BẢNG TỔNG KẾT HIỆU NĂNG THUẬT TOÁN (THỜI GIAN / RAM / NODES)':^160}")
    print("="*160)
    
    header = f"{'File':<15} | {'Size':<6} | " \
             f"{'BT: T(s)':<10} | {'R(MB)':<8} | {'Nodes':<8} | " \
             f"{'FC: T(s)':<10} | {'R(MB)':<8} | {'Nodes':<8} | " \
             f"{'BC: T(s)':<10} | {'R(MB)':<8} | {'Nodes':<8} | " \
             f"{'A*: T(s)':<10} | {'R(MB)':<8} | {'Nodes':<8}"
    print(header)
    print("-" * 160)
    
    for r in results:
        # Unpack dữ liệu
        bt_t, bt_r, bt_n = r["BT"]
        fc_t, fc_r, fc_n = r["FC"]
        bc_t, bc_r, bc_n = r["BC"]
        as_t, as_r, as_n = r["AStar"]
        
        row_str = f"{r['File']:<15} | {r['Size']:<6} | " \
                  f"{bt_t:<10.4f} | {bt_r:<8.3f} | {bt_n:<8} | " \
                  f"{fc_t:<10.4f} | {fc_r:<8.3f} | {fc_n:<8} | " \
                  f"{bc_t:<10.4f} | {bc_r:<8.3f} | {bc_n:<8} | " \
                  f"{as_t:<10.4f} | {as_r:<8.3f} | {as_n:<8}"
        print(row_str)
        
    print("="*160)
    print("* T(s): Thời gian chạy (giây) | R(MB): Đỉnh RAM tiêu thụ (Megabyte) | Nodes: Số node đã duyệt hoặc phép suy diễn logic.")
    print("* Backward Chaining (BC) chỉ đo lường thời gian truy vấn để kiểm tra 1 ô mồi đầu tiên được tìm thấy.")