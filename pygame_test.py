import pygame
import sys
import stockfish as s

# Constantes
WIDTH, HEIGHT = 640, 640
EVAL_BAR_WIDTH = 20
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Couleurs
WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
HIGHLIGHT = (0, 255, 0)

# Initialisation
pygame.init()
font = pygame.font.SysFont('Arial', 14)
screen = pygame.display.set_mode((WIDTH + EVAL_BAR_WIDTH, HEIGHT))
pygame.display.set_caption("Échiquier Pygame")

# Charger les images de pièces
pieces = {}
PIECE_NAMES = ['white-pawn', 'white-rook', 'white-knight', 'white-bishop', 'white-queen', 'white-king',
               'black-pawn', 'black-rook', 'black-knight', 'black-bishop', 'black-queen', 'black-king']
for name in PIECE_NAMES:
    img = pygame.image.load(f"pieces/{name}.png")
    img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
    pieces[name] = img

# Position de départ simplifiée
start_position = [
    ["black-rook", "black-knight", "black-bishop", "black-queen", "black-king", "black-bishop", "black-knight", "black-rook"],
    ["black-pawn"] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    [None] * 8,
    ["white-pawn"] * 8,
    ["white-rook", "white-knight", "white-bishop", "white-queen", "white-king", "white-bishop", "white-knight", "white-rook"]
]

board = [row[:] for row in start_position]
selected = None
moves = []

current_turn = "white"  # Blancs commencent

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            if selected == (row, col):
                pygame.draw.rect(screen, HIGHLIGHT, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

def draw_pieces():
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece:
                screen.blit(pieces[piece], (col * SQUARE_SIZE, row * SQUARE_SIZE))

def pos_to_square(pos):
    col, row = pos
    return chr(col + ord('a')) + str(8 - row)

def piece_color(piece_name):
    if piece_name.startswith("white"):
        return "white"
    elif piece_name.startswith("black"):
        return "black"
    return None

def is_valid_move(board, from_row, from_col, to_row, to_col, is_test = False):
    piece = board[from_row][from_col]
    if not piece:
        return False
    if not is_test:
        if piece_color(piece) != current_turn:
            return False
        target_piece = board[to_row][to_col]
        if target_piece and piece_color(target_piece) == current_turn:
            return False
    else:
        target_piece = board[to_row][to_col]
        # On autorise de capturer une pièce alliée en mode test (utile pour détecter les chemins),
        # mais on interdit juste de capturer une pièce qui bloquerait l’attaque :
        if target_piece and piece_color(target_piece) == piece_color(piece):
            return False

    dr = to_row - from_row
    dc = to_col - from_col

    # Pion
    if piece.endswith("pawn"):
        direction = -1 if piece_color(piece) == "white" else 1
        start_row = 6 if piece_color(piece) == "white" else 1

        # Avancer d'une case
        if dc == 0 and dr == direction and target_piece is None:
            return True
        # Premier déplacement: avancer de deux cases
        if dc == 0 and dr == 2*direction and from_row == start_row and board[from_row + direction][from_col] is None and target_piece is None:
            return True
        # Prise en diagonale
        if abs(dc) == 1 and dr == direction and target_piece is not None and piece_color(target_piece) != piece_color(piece):
            return True
        return False

    # Tour (déplacement en ligne droite, vérifier obstacles)
    elif piece.endswith("rook"):
        if dr != 0 and dc != 0:
            return False
        # Vérifier chemin libre
        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
        r, c = from_row + step_r, from_col + step_c
        while (r != to_row or c != to_col):
            if board[r][c] is not None:
                return False
            r += step_r
            c += step_c
        return True

    # Cavalier (mouvement en L)
    elif piece.endswith("knight"):
        if (abs(dr), abs(dc)) in [(2,1),(1,2)]:
            return True
        return False

    # Fou (diagonales, vérifier obstacles)
    elif piece.endswith("bishop"):
        if abs(dr) != abs(dc):
            return False
        step_r = 1 if dr > 0 else -1
        step_c = 1 if dc > 0 else -1
        r, c = from_row + step_r, from_col + step_c
        while r != to_row or c != to_col:
            if board[r][c] is not None:
                return False
            r += step_r
            c += step_c
        return True

    # Reine (combinaison tour + fou)
    elif piece.endswith("queen"):
        # Si déplacement droit (tour)
        if dr == 0 or dc == 0:
            # réutiliser logique tour
            step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
            step_c = 0 if dc == 0 else (1 if dc > 0 else -1)
            r, c = from_row + step_r, from_col + step_c
            while (r != to_row or c != to_col):
                if board[r][c] is not None:
                    return False
                r += step_r
                c += step_c
            return True
        # Si déplacement diagonal (fou)
        if abs(dr) == abs(dc):
            step_r = 1 if dr > 0 else -1
            step_c = 1 if dc > 0 else -1
            r, c = from_row + step_r, from_col + step_c
            while r != to_row or c != to_col:
                if board[r][c] is not None:
                    return False
                r += step_r
                c += step_c
            return True
        return False

    # Roi (mouvements d'une case dans toutes les directions)
    elif piece.endswith("king"):
        if max(abs(dr), abs(dc)) == 1:
            return True
        return False

    return False

# vérifie si une fois la pièce bougée, le roi se situe en échec : si c'est le cas return false (mouvement illégal)
def verify_check(board, from_row, from_col, to_row, to_col):
    import copy
    temp_board = copy.deepcopy(board)

    # Simule le déplacement
    piece = temp_board[from_row][from_col]
    temp_board[to_row][to_col] = piece
    temp_board[from_row][from_col] = None
    print("from row: ",from_row,"\nfrom col: ",from_col)
    print("to row: ",to_row,"\nto col: ",to_col)

    # Trouve le roi du joueur courant
    king_color = piece_color(piece)
    print("king_color: ",king_color)
    king_pos = None
    for r in range(8):
        for c in range(8):
            if temp_board[r][c] == f"{king_color}-king":
                king_pos = (r, c)
                break
        if king_pos:
            break


    # Vérifie si une pièce adverse peut l'attaquer
    print("Test de mouvement de", piece, "en", pos_to_square((to_col, to_row)))
    print("Position du roi : ", king_pos)
    print("Attaques potentielles après déplacement :")
    for r in range(8):
        for c in range(8):
            attacker = temp_board[r][c]
            if attacker and piece_color(attacker) != king_color:
                if is_valid_move(temp_board, r, c, king_pos[0], king_pos[1], True):
                    print(f"  {attacker} en {pos_to_square((c,r))} peut attaquer le roi en {pos_to_square((king_pos[1], king_pos[0]))}")
                    return False  # Le roi serait en échec
    return True  # Le roi est en sécurité



def draw_labels():
    padding = 5  # un petit décalage du bord

    # Lettres (a-h) en bas à gauche des cases de la dernière rangée (row 7)
    for col in range(COLS):
        letter = chr(ord('a') + col)
        text = font.render(letter, True, (0, 0, 0))
        x = col * SQUARE_SIZE + padding
        y = (ROWS - 1) * SQUARE_SIZE + SQUARE_SIZE - padding
        text_rect = text.get_rect(bottomleft=(x, y))
        screen.blit(text, text_rect)

    # Chiffres (8-1) en haut à gauche des cases de la première colonne (col 0)
    for row in range(ROWS):
        number = str(8 - row)
        text = font.render(number, True, (0, 0, 0))
        x = padding
        y = row * SQUARE_SIZE + padding
        text_rect = text.get_rect(topleft=(x, y))
        screen.blit(text, text_rect)

def board_to_fen(board):
    piece_to_fen = {
        "white-pawn": "P", "white-rook": "R", "white-knight": "N", "white-bishop": "B", "white-queen": "Q", "white-king": "K",
        "black-pawn": "p", "black-rook": "r", "black-knight": "n", "black-bishop": "b", "black-queen": "q", "black-king": "k"
    }
    fen_rows = []
    for row in board:
        empty = 0
        fen_row = ""
        for cell in row:
            if cell is None:
                empty += 1
            else:
                if empty > 0:
                    fen_row += str(empty)
                    empty = 0
                fen_row += piece_to_fen[cell]
        if empty > 0:
            fen_row += str(empty)
        fen_rows.append(fen_row)
    fen = "/".join(fen_rows)
    fen += " " + ("w" if current_turn == "white" else "b") + " - - 0 1"  # Simplification, pas de roque ni échec
    return fen

def stockfish_move():
    stockfish.go(movetime=50)
    eval = stockfish.get_eval()
    # mettre à jour un état partagé, ex :
    global evaluation
    evaluation = eval

def draw_eval_bar(eval_score):
    max_eval = 5  # +5 pions max affiché, au-delà on bloque la barre

    bar_height = HEIGHT
    bar_x = WIDTH  # juste à droite de l'échiquier
    bar_y = 0

    pygame.draw.rect(screen, (200, 200, 200), (bar_x, bar_y, EVAL_BAR_WIDTH, bar_height))  # fond gris clair

    # Clamp score entre -max_eval et +max_eval
    score = max(-max_eval, min(max_eval, eval_score))

    middle = bar_height // 2
    offset = int((score / max_eval) * (bar_height // 2))

    if score >= 0:
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, middle - offset, EVAL_BAR_WIDTH, offset))
    else:
        pygame.draw.rect(screen, (0, 0, 0), (bar_x, middle, EVAL_BAR_WIDTH, -offset))

    pygame.draw.line(screen, (100, 100, 100), (bar_x, middle), (bar_x + EVAL_BAR_WIDTH, middle), 2)

    # Texte d'évaluation centré verticalement dans la barre
    eval_text = f"{eval_score:.2f}"
    # Texte noir sur fond clair, blanc sur fond foncé : ici je propose noir partout, puisque fond global est gris clair
    text_color = (0, 0, 0)
    text_surface = font.render(eval_text, True, text_color)

    # Centrage horizontal + vertical dans la barre d'éval
    text_rect = text_surface.get_rect(center=(bar_x + EVAL_BAR_WIDTH // 2, middle))

    screen.blit(text_surface, text_rect)

stockfish = s.Stockfish(path = "stockfish\\stockfish-windows-x86-64-avx2.exe")
stockfish.set_depth(15)


# Boucle principale
while True:
    draw_board()
    draw_labels()
    draw_pieces()
    pygame.display.flip()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            print("Coups joués :", moves)
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row = y // SQUARE_SIZE
            col = x // SQUARE_SIZE

            if selected:
                from_row, from_col = selected
                piece = board[from_row][from_col]
                if piece:
                    if is_valid_move(board, from_row, from_col, row, col) and verify_check(board, from_row, from_col, row, col):
                        # Enregistrement du coup
                        move = pos_to_square((from_col, from_row)) + pos_to_square((col, row))
                        moves.append(move)

                        # Déplacement
                        board[row][col] = piece
                        board[from_row][from_col] = None

                        # Changer de joueur
                        current_turn = "black" if current_turn == "white" else "white"
                    else:
                        print("Mouvement illégal !")
                selected = None
            else:
                if board[row][col] and piece_color(board[row][col]) == current_turn:
                    selected = (row, col)
    fen = board_to_fen(board)
    stockfish.set_fen_position(fen)
    eval_cp = stockfish.get_evaluation()
    draw_eval_bar(eval_cp["value"]/100)
# testing commit 