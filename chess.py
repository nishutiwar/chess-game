import tkinter as tk
from tkinter import messagebox, simpledialog
import copy

WHITE = "white"
BLACK = "black"

uniDict = {WHITE : { 'Pawn' : "♙", 'Rook' : "♖", 'Knight' : "♘", 'Bishop' : "♗", 'King' : "♔", 'Queen' : "♕" }, BLACK : { 'Pawn' : "♟", 'Rook' : "♜", 'Knight' : "♞", 'Bishop' : "♝", 'King' : "♚", 'Queen' : "♛" }}

chessCardinals = [(1,0),(0,1),(-1,0),(0,-1)]
chessDiagonals = [(1,1),(-1,1),(1,-1),(-1,-1)]

def knightList(x,y,int1,int2):
    return [(x+int1,y+int2),(x-int1,y+int2),(x+int1,y-int2),(x-int1,y-int2),(x+int2,y+int1),(x-int2,y+int1),(x+int2,y-int1),(x-int2,y-int1)]

def kingList(x,y):
    return [(x+1,y),(x+1,y+1),(x+1,y-1),(x,y+1),(x,y-1),(x-1,y),(x-1,y+1),(x-1,y-1)]

class Piece:
    def __init__(self, color, name):
        self.name = name
        self.position = None
        self.Color = color

    def isValid(self, startpos, endpos, Color, gameboard):
        if endpos in self.availableMoves(startpos[0], startpos[1], gameboard, Color):
            return True
        return False

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def availableMoves(self, x, y, gameboard, Color=None):
        print("ERROR: no movement for base class")

    def AdNauseum(self, x, y, gameboard, Color, intervals):
        answers = []
        for xint, yint in intervals:
            xtemp, ytemp = x + xint, y + yint
            while self.isInBounds(xtemp, ytemp):
                target = gameboard.get((xtemp, ytemp), None)
                if target is None:
                    answers.append((xtemp, ytemp))
                elif target.Color != Color:
                    answers.append((xtemp, ytemp))
                    break
                else:
                    break
                xtemp, ytemp = xtemp + xint, ytemp + yint
        return answers

    def isInBounds(self, x, y):
        return 0 <= x < 8 and 0 <= y < 8

    def noConflict(self, gameboard, initialColor, x, y):
        return self.isInBounds(x, y) and ((x, y) not in gameboard or gameboard[(x, y)].Color != initialColor)

class Knight(Piece):
    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        return [(xx, yy) for xx, yy in knightList(x, y, 2, 1) if self.noConflict(gameboard, Color, xx, yy)]

class Rook(Piece):
    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        return self.AdNauseum(x, y, gameboard, Color, chessCardinals)

class Bishop(Piece):
    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        return self.AdNauseum(x, y, gameboard, Color, chessDiagonals)

class Queen(Piece):
    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        return self.AdNauseum(x, y, gameboard, Color, chessCardinals + chessDiagonals)

class King(Piece):
    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        return [(xx, yy) for xx, yy in kingList(x, y) if self.noConflict(gameboard, Color, xx, yy)]

class Pawn(Piece):
    def __init__(self, color, name, direction):
        super().__init__(color, name)
        self.has_moved = False
        self.direction = direction

    def availableMoves(self, x, y, gameboard, Color=None):
        if Color is None:
            Color = self.Color
        answers = []
        diag1 = (x + 1, y + self.direction)
        if self.isInBounds(diag1[0], diag1[1]) and diag1 in gameboard and gameboard[diag1].Color != Color:
            answers.append(diag1)
        diag2 = (x - 1, y + self.direction)
        if self.isInBounds(diag2[0], diag2[1]) and diag2 in gameboard and gameboard[diag2].Color != Color:
            answers.append(diag2)
        forward1 = (x, y + self.direction)
        if self.isInBounds(forward1[0], forward1[1]) and forward1 not in gameboard:
            answers.append(forward1)
        forward2 = (x, y + 2 * self.direction)
        if not self.has_moved and self.isInBounds(forward2[0], forward2[1]) and forward1 not in gameboard and forward2 not in gameboard:
            answers.append(forward2)
        return answers

class ChessGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Game")
        self.root.geometry("600x650")
        self.gameboard = {}
        self.selected = None
        self.playersturn = WHITE
        self.place_pieces()
        self.canvas = tk.Canvas(self.root, width=512, height=512, bg='lightgray')
        self.canvas.pack(pady=10)
        self.canvas.bind("<Button-1>", self.click)
        self.message_label = tk.Label(self.root, text="White's turn", font=("Arial", 16))
        self.message_label.pack()
        self.update_board()
        self.root.mainloop()

    def place_pieces(self):
        piece_types = ['Rook', 'Knight', 'Bishop', 'Queen', 'King', 'Bishop', 'Knight', 'Rook']
        for i in range(8):
            self.gameboard[(i, 1)] = Pawn(WHITE, uniDict[WHITE]['Pawn'], 1)
            self.gameboard[(i, 6)] = Pawn(BLACK, uniDict[BLACK]['Pawn'], -1)
            self.gameboard[(i, 0)] = globals()[piece_types[i]](WHITE, uniDict[WHITE][piece_types[i]])
            self.gameboard[(i, 7)] = globals()[piece_types[7-i]](BLACK, uniDict[BLACK][piece_types[7-i]])

    def click(self, event):
        col = event.x // 64
        row = 7 - (event.y // 64)
        pos = (col, row)
        if pos not in self.gameboard:
            self.message_label.config(text="Invalid square")
            return
        piece = self.gameboard[pos]
        if self.selected is None:
            if piece.Color == self.playersturn:
                self.selected = pos
                self.message_label.config(text=f"Selected {piece} at {chr(pos[0]+97)}{pos[1]+1}")
            else:
                self.message_label.config(text="Wrong turn or no piece")
        else:
            if self.is_valid_move(self.selected, pos):
                self.make_move(self.selected, pos)
                self.playersturn = BLACK if self.playersturn == WHITE else WHITE
                self.update_status()
            self.selected = None
            self.update_board()

    def is_valid_move(self, start, end):
        piece = self.gameboard[start]
        moves = piece.availableMoves(start[0], start[1], self.gameboard, piece.Color)
        if end not in moves:
            return False
        sim_board = self.simulate_move(start, end)
        return not self.in_check(piece.Color, sim_board)

    def make_move(self, start, end):
        moved_piece = self.gameboard.pop(start)
        self.gameboard[end] = moved_piece
        if isinstance(moved_piece, Pawn):
            promote_row = 7 if moved_piece.Color == WHITE else 0
            if end[1] == promote_row:
                choice = simpledialog.askstring("Promote Pawn", "Enter q, r, b, or n:")
                if choice:
                    choices = {'q': ('Queen', Queen), 'r': ('Rook', Rook), 'b': ('Bishop', Bishop), 'n': ('Knight', Knight)}
                    choice = choice.lower()
                    if choice in choices:
                        name, cls = choices[choice]
                        new_piece = cls(moved_piece.Color, uniDict[moved_piece.Color][name])
                        self.gameboard[end] = new_piece

    def simulate_move(self, start, end):
        board = copy.deepcopy(self.gameboard)
        piece = board.pop(start)
        board[end] = piece
        return board

    def in_check(self, color, board):
        opp_color = BLACK if color == WHITE else WHITE
        king_pos = next((pos for pos, p in board.items() if isinstance(p, King) and p.Color == color), None)
        if not king_pos:
            return False
        for pos, piece in board.items():
            if piece.Color == opp_color:
                if piece.isValid(pos, king_pos, opp_color, board):
                    return True
        return False

    def is_checkmate(self, color):
        if not self.in_check(color, self.gameboard):
            return False
        for start, piece in self.gameboard.items():
            if piece.Color == color:
                for end in piece.availableMoves(start[0], start[1], self.gameboard):
                    sim_board = self.simulate_move(start, end)
                    if not self.in_check(color, sim_board):
                        return False
        return True

    def update_status(self):
        turn_text = self.playersturn.capitalize() + "'s turn"
        if self.in_check(self.playersturn, self.gameboard):
            turn_text += " - CHECK!"
        self.message_label.config(text=turn_text)
        if self.is_checkmate(self.playersturn):
            win_color = BLACK if self.playersturn == WHITE else WHITE
            messagebox.showinfo("Checkmate!", win_color.capitalize() + " wins!")
            self.root.quit()

    def update_board(self):
        self.canvas.delete("all")
        for i in range(8):
            for j in range(8):
                x1, y1 = i * 64, (7 - j) * 64
                x2, y2 = x1 + 64, y1 + 64
                color = "white" if (i + j) % 2 == 0 else "#D18B47"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="black", width=1)
                pos = (i, j)
                piece = self.gameboard.get(pos)
                if piece:
                    x = x1 + 32
                    y = y1 + 32
                    self.canvas.create_text(x, y, text=str(piece), font=("Arial", 48, "bold"), fill="black")
        if self.selected:
            sx, sy = self.selected
            x1 = sx * 64
            y1 = (7 - sy) * 64
            self.canvas.create_rectangle(x1, y1, x1 + 64, y1 + 64, outline="red", width=4, tags="selected")

if __name__ == "__main__":
    ChessGUI()