import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import random
import time

# --- RENK VE STİL AYARLARI ---
BG_COLOR = "#2c3e50"
FRAME_COLOR = "#34495e"
BUTTON_COLOR = "#ecf0f1"
X_COLOR = "#3498db"
O_COLOR = "#e74c3c"
WIN_COLOR = "#2ecc71"
TEXT_COLOR = "#ecf0f1"

# --- ANA PENCERE ---
root = tk.Tk()
root.title("Modern XOX Oyunu")
root.geometry("500x650")
root.resizable(False, False)
root.configure(bg=BG_COLOR)

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

# --- Stil Tanımlamaları ---
style = ttk.Style()
style.theme_use('clam')
style.configure("TFrame", background=BG_COLOR)
style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=('Calibri', 12))
style.configure("Header.TLabel", font=('Calibri', 24, 'bold'))
style.configure("Status.TLabel", font=('Calibri', 16, 'italic'))
style.configure("TRadiobutton", background=BG_COLOR, foreground=TEXT_COLOR, font=('Calibri', 11))
style.map("TRadiobutton", background=[('active', FRAME_COLOR)], foreground=[('active', TEXT_COLOR)])
style.configure("Menu.TButton", font=('Calibri', 14, 'bold'), padding=10)

# --- Oyun Durumu Değişkenleri ---
game_mode = tk.StringVar(value="Bilgisayara Karşı")
difficulty = tk.StringVar(value="Orta")
current_player = "X"
board = [["", "", ""], ["", "", ""], ["", "", ""]]
winner = None
winning_cells = []
player_names = {"X":"Oyuncu X", "O":"Oyuncu O"}  # Default isimler

# --- OYUN MANTIĞI ---
def check_winner(b=None):
    b = b or board
    lines = [[(r, c) for c in range(3)] for r in range(3)] + \
            [[(r, c) for r in range(3)] for c in range(3)] + \
            [[(i, i) for i in range(3)]] + [[(i, 2-i) for i in range(3)]]
    for line in lines:
        p1,p2,p3 = line
        if b[p1[0]][p1[1]] == b[p2[0]][p2[1]] == b[p3[0]][p3[1]] != "":
            return b[p1[0]][p1[1]], line
    return None, []

def check_draw(b=None):
    b = b or board
    return all(cell!="" for row in b for cell in row) and not check_winner(b)[0]

def get_empty_cells(b=None):
    b = b or board
    return [(r,c) for r in range(3) for c in range(3) if b[r][c]== ""]

def easy_move():
    return random.choice(get_empty_cells())

def medium_move():
    for player in ["O","X"]:
        for r,c in get_empty_cells():
            board[r][c]=player
            if check_winner()[0]==player:
                board[r][c] = ""
                return r,c
            board[r][c] = ""
    return easy_move()

def minimax(b,is_maximizing):
    winner_check,_ = check_winner(b)
    if winner_check: return {"O":1,"X":-1}[winner_check]
    if check_draw(b): return 0
    player = "O" if is_maximizing else "X"
    scores = []
    for r,c in get_empty_cells(b):
        b[r][c] = player
        scores.append(minimax(b,not is_maximizing))
        b[r][c] = ""
    return max(scores) if is_maximizing else min(scores)

def hard_move():
    best_score,move = -float('inf'),None
    for r,c in get_empty_cells():
        board[r][c] = "O"
        score = minimax(board,False)
        board[r][c] = ""
        if score > best_score:
            best_score = score
            move = (r,c)
    return move

# --- OYUN AKIŞI ---
def toggle_board_state(state):
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(state=state if board[r][c]=="" else "disabled")

def bot_move():
    if winner or check_draw(): return
    toggle_board_state("disabled")
    root.update()
    time.sleep(0.5)
    moves = {"Kolay": easy_move, "Orta": medium_move, "Zor": hard_move}
    row,col = moves[difficulty.get()]()
    make_move(row,col,"O")
    if not winner and not check_draw():
        toggle_board_state("normal")

def make_move(row,col,player):
    global winner,winning_cells,current_player
    if board[row][col]=="" and not winner:
        board[row][col]=player
        color = X_COLOR if player=="X" else O_COLOR
        buttons[row][col].config(text=player, fg=color,state="disabled",disabledforeground=color)
        winner,winning_cells = check_winner()
        if winner:
            highlight_winner()
            end_game()
        elif check_draw():
            status_label.config(text="Oyun Berabere!")
            messagebox.showinfo("Oyun Bitti","Oyun Berabere!")
        else:
            if game_mode.get()=="2 Oyuncu":
                current_player = "O" if current_player=="X" else "X"
                status_label.config(text=f"Sıra: {player_names[current_player]}")
            else:
                status_label.config(text="Sıra: Bot (O)" if player=="X" else f"Sıra: {player_names['X']}")

def on_click(row,col):
    if game_mode.get()=="2 Oyuncu":
        make_move(row,col,current_player)
    else:
        make_move(row,col,"X")
        bot_move()

def highlight_winner():
    for r,c in winning_cells:
        buttons[r][c].config(bg=WIN_COLOR)

def end_game():
    status_label.config(text=f"Oyunu Kazanan: {player_names[winner]}")
    messagebox.showinfo("Oyun Bitti", f"Oyunu Kazanan: {player_names[winner]}")
    toggle_board_state("disabled")

def new_game():
    global board,winner,winning_cells,current_player
    board,winner,winning_cells,current_player=[["","",""],["","",""],["","",""]],None,[], "X"
    # 2 oyunculu modda isimleri sor
    if game_mode.get()=="2 Oyuncu":
        name1 = simpledialog.askstring("İsim Girin","1. Oyuncu Adı:") or "Oyuncu X"
        name2 = simpledialog.askstring("İsim Girin","2. Oyuncu Adı:") or "Oyuncu O"
        player_names["X"]=name1
        player_names["O"]=name2
    status_label.config(text=f"Sıra: {player_names['X']}" if game_mode.get()!="2 Oyuncu" else f"Sıra: {player_names['X']}")
    for r in range(3):
        for c in range(3):
            buttons[r][c].config(text="",state="normal",bg=BUTTON_COLOR)

def return_to_menu():
    game_frame.grid_forget()
    setup_frame.grid(row=0,column=0)

def start_game():
    new_game()
    setup_frame.grid_forget()
    game_frame.grid(row=0,column=0)

# --- AYAR EKRANI ---
setup_frame = ttk.Frame(root, style="TFrame")
setup_frame.grid_rowconfigure(list(range(7)), weight=1)
setup_frame.grid_columnconfigure(0, weight=1)

ttk.Label(setup_frame,text="Modern XOX Oyunu", style="Header.TLabel").grid(row=0,column=0,pady=(0,40))
ttk.Label(setup_frame,text="Oyun Modu Seçin:").grid(row=1,column=0,pady=5)
ttk.Radiobutton(setup_frame,text="Bilgisayara Karşı", variable=game_mode, value="Bilgisayara Karşı").grid(row=2,column=0,pady=2)
ttk.Radiobutton(setup_frame,text="İki Oyuncu", variable=game_mode, value="2 Oyuncu").grid(row=3,column=0,pady=2)
ttk.Label(setup_frame,text="Zorluk Seviyesi:").grid(row=4,column=0,pady=(20,5))
difficulty_frame = ttk.Frame(setup_frame, style="TFrame")
difficulty_frame.grid(row=5,column=0)
ttk.Radiobutton(difficulty_frame,text="Kolay", variable=difficulty, value="Kolay").pack(side="left", padx=5)
ttk.Radiobutton(difficulty_frame,text="Orta", variable=difficulty, value="Orta").pack(side="left", padx=5)
ttk.Radiobutton(difficulty_frame,text="Zor", variable=difficulty, value="Zor").pack(side="left", padx=5)
ttk.Button(setup_frame,text="Oyuna Başla", command=start_game, style="Menu.TButton").grid(row=6,column=0,pady=40)

# --- OYUN EKRANI ---
game_frame = ttk.Frame(root, style="TFrame")
game_frame.grid_rowconfigure([0,2], weight=1)
game_frame.grid_columnconfigure(0, weight=1)

# --- OYUN TAHTASI ---
board_frame = tk.Frame(game_frame, bg=FRAME_COLOR)
board_frame.grid(row=0,column=0,pady=10,padx=10)
buttons = [[tk.Button(board_frame,text="",font=('Calibri',40,'bold'),width=5,height=2,bg=BUTTON_COLOR,relief="flat",disabledforeground="black",command=lambda r=r,c=c:on_click(r,c)) for c in range(3)] for r in range(3)]
for r in range(3):
    for c in range(3):
        buttons[r][c].grid(row=r,column=c,padx=5,pady=5)

# --- OYUN KONTROL BUTONLARI ---
control_frame = tk.Frame(game_frame, bg=FRAME_COLOR)
control_frame.grid(row=1,column=0,pady=10)
tk.Button(control_frame,text="Yeni Oyun", command=new_game, bg=BUTTON_COLOR, fg=BG_COLOR, font=('Calibri',12,'bold')).pack(side="left", padx=20)
tk.Button(control_frame,text="Menüye Dön", command=return_to_menu, bg=BUTTON_COLOR, fg=BG_COLOR, font=('Calibri',12,'bold')).pack(side="left", padx=20)

# --- DURUM LABELI ---
status_label = ttk.Label(game_frame,text="", style="Status.TLabel")
status_label.grid(row=2,column=0,pady=20)

# --- UYGULAMA BAŞLAT ---
setup_frame.grid(row=0,column=0)
root.mainloop()
