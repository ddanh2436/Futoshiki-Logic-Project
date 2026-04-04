import os

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

if __name__ == "__main__":
    input_file = os.path.join("Inputs", "input-01.txt")
    
    try:
        N, grid, horiz, vert = read_futoshiki_input(input_file)
        print(f"Kích thước ma trận N = {N}")
        print("\n--- Ma trận ban đầu ---")
        for row in grid:
            print(row)
            
        print("\n--- Ràng buộc ngang ---")
        for row in horiz:
            print(row)
            
        print("\n--- Ràng buộc dọc ---")
        for row in vert:
            print(row)
            
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại đường dẫn {input_file}. Hãy kiểm tra lại cấu trúc thư mục!")