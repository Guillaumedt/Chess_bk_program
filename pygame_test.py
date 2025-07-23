import pygame
import sys

# Constantes
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Couleurs
WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
HIGHLIGHT = (0, 255, 0)

# Initialisation
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

def is_valid_move(board, from_row, from_col, to_row, to_col):
    piece = board[from_row][from_col]
    if not piece:
        return False
    if piece_color(piece) != current_turn:
        return False
    target_piece = board[to_row][to_col]
    if target_piece and piece_color(target_piece) == current_turn:
        return False  # Pas capturer ses propres pièces

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
        while r != to_row and c != to_col:
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
            while r != to_row and c != to_col:
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

# Boucle principale
while True:
    draw_board()
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
                    if is_valid_move(board, from_row, from_col, row, col):
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
    
import pygame
import sys

# Constantes
WIDTH, HEIGHT = 640, 640
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Couleurs
WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
HIGHLIGHT = (0, 255, 0)

# Initialisation
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
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

def is_valid_move(board, from_row, from_col, to_row, to_col):
    piece = board[from_row][from_col]
    if not piece:
        return False
    if piece_color(piece) != current_turn:
        return False
    target_piece = board[to_row][to_col]
    if target_piece and piece_color(target_piece) == current_turn:
        return False  # Pas capturer ses propres pièces

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
        while r != to_row and c != to_col:
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
            while r != to_row and c != to_col:
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

# Boucle principale
while True:
    draw_board()
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
                    if is_valid_move(board, from_row, from_col, row, col):
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
    