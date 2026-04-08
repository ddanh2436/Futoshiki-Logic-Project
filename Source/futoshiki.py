import os
import copy
import time
import heapq
import itertools
import glob

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

def extract_grid_from_assignment(assignment, N):
    solved_grid = [[0 for _ in range(N)] for _ in range(N)]
    for var, is_true in assignment.items():
        if is_true and var > 0:
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
# CÁC HÀM TIỆN ÍCH
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
# THUẬT TOÁN 1: BACKTRACKING
# =============================================================================

def solve_backtracking(grid, N, horiz, vert):
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
# THUẬT TOÁN 2: FORWARD CHAINING (DPLL)
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

def dpll_forward_chaining(clauses, assignment):
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
# THUẬT TOÁN 3: BACKWARD CHAINING (GIỮ NGUYÊN BẢN GỐC CỦA NHÓM)
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

def fol_bc_ask(horn_kb, query_list, visited=None):
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
    target_var = get_var_id(i, j, v, N)
    horn_kb = build_horn_kb(KB)
    return fol_bc_ask(horn_kb, [target_var])

# =============================================================================
# THUẬT TOÁN 4: A* SEARCH KẾT HỢP HEURISTIC
# =============================================================================

def find_mrv_empty_location(grid, N, horiz, vert):
    best_pos = None
    min_options = N + 1
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                options = sum(1 for v in range(1, N + 1) if is_safe(grid, r, c, v, N, horiz, vert))
                if options < min_options:
                    min_options = options
                    best_pos = (r, c)
                    if min_options == 0: return best_pos 
    return best_pos

def heuristic_A_star(grid, N, horiz, vert):
    empty_count = 0
    for r in range(N):
        for c in range(N):
            if grid[r][c] == 0:
                empty_count += 1
                possible_values = sum(1 for v in range(1, N + 1) if is_safe(grid, r, c, v, N, horiz, vert))
                if possible_values == 0: return float('inf') 
    return empty_count

def solve_astar(initial_grid, N, horiz, vert):
    initial_g = sum(1 for r in range(N) for c in range(N) if initial_grid[r][c] != 0)
    initial_h = heuristic_A_star(initial_grid, N, horiz, vert)
    if initial_h == float('inf'): return False, None, 0
        
    pq = []
    tie_breaker = itertools.count() 
    heapq.heappush(pq, (initial_g + initial_h, -initial_g, next(tie_breaker), initial_grid))
    nodes_expanded = 0 
    
    while pq:
        f, neg_g, _, current_grid = heapq.heappop(pq)
        g = -neg_g
        nodes_expanded += 1
        empty_pos = find_mrv_empty_location(current_grid, N, horiz, vert)
        if not empty_pos: return True, current_grid, nodes_expanded
        row, col = empty_pos
        for num in range(1, N + 1):
            if is_safe(current_grid, row, col, num, N, horiz, vert):
                child_grid = [r[:] for r in current_grid]
                child_grid[row][col] = num
                child_g = g + 1
                child_h = heuristic_A_star(child_grid, N, horiz, vert)
                if child_h != float('inf'):
                    heapq.heappush(pq, (child_g + child_h, -child_g, next(tie_breaker), child_grid))
    return False, None, nodes_expanded

# =============================================================================
# PHẦN MAIN: TỰ ĐỘNG CHẠY TẤT CẢ TEST CASES VÀ THỐNG KÊ
# =============================================================================

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, "Inputs")
    
    # Lấy danh sách tất cả các file input-*.txt và sắp xếp
    input_files = sorted(glob.glob(os.path.join(input_folder, "input-*.txt")))
    
    if not input_files:
        print(f"Không tìm thấy file input nào trong thư mục {input_folder}")
        exit()

    results = []

    print("BẮT ĐẦU CHẠY KIỂM THỬ TRÊN TẤT CẢ TEST CASES...\n")

    for file_path in input_files:
        filename = os.path.basename(file_path)
        N, grid, horiz, vert = read_futoshiki_input(file_path)
        
        print(f"[{filename}] - Kích thước {N}x{N} - Đang xử lý...")
        
        # Sinh KB chung
        t_start_kb = time.time()
        KB = build_full_kb(N, grid, horiz, vert)
        t_kb = time.time() - t_start_kb

        # 1. Backtracking
        grid_bt = copy.deepcopy(grid)
        t_start = time.time()
        res_bt = solve_backtracking(grid_bt, N, horiz, vert)
        t_bt = time.time() - t_start
        
        # 2. Forward Chaining (DPLL)
        t_start = time.time()
        res_fc, _ = dpll_forward_chaining(KB, {})
        t_fc = time.time() - t_start

        # 3. Backward Chaining (Test 1 ô mồi như code gốc)
        t_start = time.time()
        test_i, test_j, test_v = -1, -1, 0
        for r in range(N):
            for c in range(N):
                if grid[r][c] != 0:
                    test_i, test_j, test_v = r + 1, c + 1, grid[r][c]
                    break
            if test_v != 0: break
        
        res_bc = False
        if test_v != 0:
            res_bc = query_cell_backward_chaining(KB, test_i, test_j, test_v, N)
        t_bc = time.time() - t_start

        # 4. A* Search
        grid_astar = copy.deepcopy(grid)
        t_start = time.time()
        res_astar, _, nodes_expanded = solve_astar(grid_astar, N, horiz, vert)
        t_astar = time.time() - t_start
        
        # Lưu kết quả
        results.append({
            "File": filename,
            "Size": f"{N}x{N}",
            "Gen KB": t_kb,
            "BT Time": t_bt,
            "FC Time": t_fc,
            "BC Time": t_bc,
            "A* Time": t_astar,
            "A* Nodes": nodes_expanded
        })
        print(f"--> Hoàn tất {filename}\n")

    # =========================================================================
    # IN BẢNG TỔNG KẾT
    # =========================================================================
    print("="*105)
    print(f"{'BẢNG TỔNG KẾT THỜI GIAN CHẠY CÁC THUẬT TOÁN (giây)':^105}")
    print("="*105)
    header = f"{'File':<15} | {'Size':<6} | {'Gen KB':<10} | {'Backtracking':<15} | {'Forward Chaining':<18} | {'Backward Chaining':<18} | {'A* Search':<12}"
    print(header)
    print("-" * 105)
    
    for r in results:
        row_str = (
            f"{r['File']:<15} | "
            f"{r['Size']:<6} | "
            f"{r['Gen KB']:<10.4f} | "
            f"{r['BT Time']:<15.5f} | "
            f"{r['FC Time']:<18.5f} | "
            f"{r['BC Time']:<18.5f} | "
            f"{r['A* Time']:<12.5f}"
        )
        print(row_str)
    print("="*105)
    print("* Lưu ý: Thời gian Backward Chaining trong bảng này là thời gian truy vấn 1 ô mồi đầu tiên tìm thấy.")