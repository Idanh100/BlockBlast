import numpy as np

board = np.zeros((8, 8))
board[2,2] = 1
board[3,5] = 1
board[3,6] = 1
print(board)

print(board.sum(axis=0))
print(board.sum(axis=1))

blocks = {
            "square": [[1, 1], [1, 1]],
            "line2": [[1, 1]],
            "line3": [[1, 1, 1]],
            "line4": [[1, 1, 1, 1]],
            "line5": [[1, 1, 1, 1, 1]],
            "col2": [[1], [1]],
            "col3": [[1], [1], [1]],
            "col4": [[1], [1], [1], [1]],
            "col5": [[1], [1], [1], [1], [1]],
            "T": [[0, 1, 0], [1, 1, 1]],
            "T_inverted": [[1, 1, 1], [0, 1, 0]],
            "T_right": [[1, 0], [1, 1], [1, 0]],
            "T_left": [[0, 1], [1, 1], [0, 1]],
            "L": [[1, 0], [1, 0], [1, 1]],
            "L_flipped": [[0, 1], [0, 1], [1, 1]],
            "L_rotated": [[1, 1, 1], [1, 0, 0]],
            "L_rotated_flipped": [[1, 1, 1], [0, 0, 1]],
            "Z": [[1, 1, 0], [0, 1, 1]],
            "Z_vertical": [[0, 1], [1, 1], [1, 0]],
            "S": [[0, 1, 1], [1, 1, 0]],
            "S_vertical": [[1, 0], [1, 1], [0, 1]],
            "plus": [[0, 1, 0], [1, 1, 1], [0, 1, 0]],
            "dot1": [[1]],
            "dot2": [[1]],
            "dot3": [[1]],
            "dot4": [[1]],
            "dot6": [[1]],
            "dot7": [[1]],
            "dot8": [[1]],
            "dot9": [[1]],
            "dot10": [[1]],
            "dot11": [[1]],
            "dot12": [[1]],
            "dot13": [[1]],
            "dot14": [[1]],
            "dot15": [[1]],
            "small_square": [[1, 1], [1, 1]],
            "corner": [[1, 1], [1, 0]],
            "corner_flipped": [[1, 1], [0, 1]],
            "corner_rotated": [[0, 1], [1, 1]],
            "corner_rotated_flipped": [[1, 0], [1, 1]],
            "U": [[1, 0, 1], [1, 1, 1]],
            "U_rotated": [[1, 1], [1, 0], [1, 1]],
            "U_inverted": [[1, 1, 1], [1, 0, 1]],
            "U_rotated_flipped": [[1, 1], [0, 1], [1, 1]],
            "2x3": [[1, 1, 1], [1, 1, 1]],
            "3x3": [[1, 1, 1], [1, 1, 1], [1, 1, 1]]
        }

print (blocks["T"])
t = np.array(blocks["T"])
print(t)
print(t.sum())
row, col = t.shape[0], t.shape[1]
print(row, col)

print(board[2:2+row, 4:4+col])

s= board[2:2+row, 4:4+col] + t

print(s.max())