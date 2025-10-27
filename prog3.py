import random
import pygame as pygame
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 900
BOARD_SIZE = 700
BOARD_OFFSET = 50
CELL_SIZE = BOARD_SIZE // 3
LINE_WIDTH = 15

# Colors
BG_COLOR = (28, 28, 40)
BOARD_COLOR = (40, 40, 60)
LINE_COLOR = (50, 150, 200)
X_COLOR = (255, 100, 100)
O_COLOR = (100, 200, 255)
TEXT_COLOR = (255, 255, 255)
BUTTON_COLOR = (60, 60, 100)
BUTTON_HOVER_COLOR = (80, 80, 140)
WIN_LINE_COLOR = (255, 215, 0)

# Game states
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2

class TicTacToeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tic Tac Toe")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 35)
        self.reset_game()
        self.state = STATE_MENU
        self.mode = None

    def reset_game(self):
        self.board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.current_player = 1
        self.winner = None
        self.winning_line = None
        self.computer_thinking = False
        self.computer_move_time = 0

    def draw_menu(self):
        self.screen.fill(BG_COLOR)
        # Title
        title = self.font_large.render("TIC TAC TOE", True, TEXT_COLOR)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        # Human vs Human button
        hvh_rect = pygame.Rect(250, 350, 300, 80)
        hvh_color = BUTTON_HOVER_COLOR if hvh_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, hvh_color, hvh_rect, border_radius=15)
        pygame.draw.rect(self.screen, LINE_COLOR, hvh_rect, 3, border_radius=15)
        hvh_text = self.font_medium.render("Human vs Human", True, TEXT_COLOR)
        hvh_text_rect = hvh_text.get_rect(center=hvh_rect.center)
        self.screen.blit(hvh_text, hvh_text_rect)

        # Human vs Computer button
        hvc_rect = pygame.Rect(250, 470, 300, 80)
        hvc_color = BUTTON_HOVER_COLOR if hvc_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, hvc_color, hvc_rect, border_radius=15)
        pygame.draw.rect(self.screen, LINE_COLOR, hvc_rect, 3, border_radius=15)
        hvc_text = self.font_medium.render("Human vs Computer", True, TEXT_COLOR)
        hvc_text_rect = hvc_text.get_rect(center=hvc_rect.center)
        self.screen.blit(hvc_text, hvc_text_rect)

        return hvh_rect, hvc_rect

    def draw_board(self):
        self.screen.fill(BG_COLOR)

        # Draw board background
        board_rect = pygame.Rect(BOARD_OFFSET, BOARD_OFFSET + 60, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(self.screen, BOARD_COLOR, board_rect, border_radius=10)

        # Draw grid lines
        for i in range(1, 3):
            # Vertical lines
            x = BOARD_OFFSET + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR,
                            (x, BOARD_OFFSET + 60),
                            (x, BOARD_OFFSET + 60 + BOARD_SIZE), LINE_WIDTH)
            # Horizontal lines
            y = BOARD_OFFSET + 60 + i * CELL_SIZE
            pygame.draw.line(self.screen, LINE_COLOR,
                            (BOARD_OFFSET, y),
                            (BOARD_OFFSET + BOARD_SIZE, y), LINE_WIDTH)

        # Draw X's and O's
        for row in range(3):
            for col in range(3):
                if self.board[row][col] == 1:
                    self.draw_x(row, col)
                elif self.board[row][col] == 2:
                    self.draw_o(row, col)

        # Draw winning line
        if self.winning_line:
            self.draw_winning_line()

        # Draw header
        if self.state == STATE_PLAYING:
            if self.computer_thinking:
                text = "Computer is thinking..."
            else:
                player_name = "X" if self.current_player == 1 else "O"
                text = f"Player {player_name}'s Turn"
            header = self.font_medium.render(text, True, TEXT_COLOR)
        else:
            if self.winner == 1:
                text = "Player X Wins!"
            elif self.winner == 2:
                text = "Player O Wins!"
            else:
                text = "It's a Draw!"
            header = self.font_large.render(text, True, TEXT_COLOR)

        header_rect = header.get_rect(center=(WINDOW_WIDTH // 2, 30))
        self.screen.blit(header, header_rect)

        # Draw restart button if game over
        if self.state == STATE_GAME_OVER:
            mouse_pos = pygame.mouse.get_pos()
            restart_rect = pygame.Rect(300, 800, 200, 50)
            restart_color = BUTTON_HOVER_COLOR if restart_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, restart_color, restart_rect, border_radius=10)
            pygame.draw.rect(self.screen, LINE_COLOR, restart_rect, 3, border_radius=10)
            restart_text = self.font_small.render("Play Again", True, TEXT_COLOR)
            restart_text_rect = restart_text.get_rect(center=restart_rect.center)
            self.screen.blit(restart_text, restart_text_rect)
            return restart_rect
        return None

    def draw_x(self, row, col):
        x_center = BOARD_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
        y_center = BOARD_OFFSET + 60 + row * CELL_SIZE + CELL_SIZE // 2
        offset = CELL_SIZE // 3
        pygame.draw.line(self.screen, X_COLOR,
                        (x_center - offset, y_center - offset),
                        (x_center + offset, y_center + offset), 12)
        pygame.draw.line(self.screen, X_COLOR,
                        (x_center + offset, y_center - offset),
                        (x_center - offset, y_center + offset), 12)

    def draw_o(self, row, col):
        x_center = BOARD_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
        y_center = BOARD_OFFSET + 60 + row * CELL_SIZE + CELL_SIZE // 2
        radius = CELL_SIZE // 3
        pygame.draw.circle(self.screen, O_COLOR, (x_center, y_center), radius, 12)

    def draw_winning_line(self):
        if not self.winning_line:
            return
        line_type, index = self.winning_line
        if line_type == "row":
            y = BOARD_OFFSET + 60 + index * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (BOARD_OFFSET + 20, y),
                            (BOARD_OFFSET + BOARD_SIZE - 20, y), 10)
        elif line_type == "col":
            x = BOARD_OFFSET + index * CELL_SIZE + CELL_SIZE // 2
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (x, BOARD_OFFSET + 60 + 20),
                            (x, BOARD_OFFSET + 60 + BOARD_SIZE - 20), 10)
        elif line_type == "diag1":
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (BOARD_OFFSET + 20, BOARD_OFFSET + 60 + 20),
                            (BOARD_OFFSET + BOARD_SIZE - 20, BOARD_OFFSET + 60 + BOARD_SIZE - 20), 10)
        elif line_type == "diag2":
            pygame.draw.line(self.screen, WIN_LINE_COLOR,
                            (BOARD_OFFSET + BOARD_SIZE - 20, BOARD_OFFSET + 60 + 20),
                            (BOARD_OFFSET + 20, BOARD_OFFSET + 60 + BOARD_SIZE - 20), 10)

    def handle_click(self, pos):
        if self.state == STATE_MENU:
            return
        if self.state == STATE_GAME_OVER:
            return
        if self.computer_thinking:
            return

        x, y = pos
        # Check if click is within board
        if (BOARD_OFFSET <= x <= BOARD_OFFSET + BOARD_SIZE and
            BOARD_OFFSET + 60 <= y <= BOARD_OFFSET + 60 + BOARD_SIZE):
            col = (x - BOARD_OFFSET) // CELL_SIZE
            row = (y - BOARD_OFFSET - 60) // CELL_SIZE
            if 0 <= row < 3 and 0 <= col < 3:
                self.make_move(row, col)

    def make_move(self, row, col):
        if self.board[row][col] == 0:
            self.board[row][col] = self.current_player
            winner_result = check_winner(self.board)
            if winner_result:
                self.winner = winner_result
                self.winning_line = get_winning_line(self.board)
                self.state = STATE_GAME_OVER
            else:
                self.current_player = 2 if self.current_player == 1 else 1
                # If computer's turn, schedule computer move
                if self.mode == 2 and self.current_player == 2 and self.state == STATE_PLAYING:
                    self.computer_thinking = True
                    self.computer_move_time = pygame.time.get_ticks()

    def update(self):
        if self.computer_thinking:
            # Add a small delay for better UX
            if pygame.time.get_ticks() - self.computer_move_time > 500:
                row, col = get_computer_move(self.board)
                self.make_move(row, col)
                self.computer_thinking = False

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == STATE_MENU:
                        hvh_rect, hvc_rect = self.draw_menu()
                        if hvh_rect.collidepoint(event.pos):
                            self.mode = 1
                            self.state = STATE_PLAYING
                            self.reset_game()
                        elif hvc_rect.collidepoint(event.pos):
                            self.mode = 2
                            self.state = STATE_PLAYING
                            self.reset_game()
                    elif self.state == STATE_PLAYING:
                        self.handle_click(event.pos)
                    elif self.state == STATE_GAME_OVER:
                        restart_rect = self.draw_board()
                        if restart_rect and restart_rect.collidepoint(event.pos):
                            self.state = STATE_MENU
                            self.reset_game()

            self.update()

            if self.state == STATE_MENU:
                self.draw_menu()
            else:
                self.draw_board()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

def main():
    game = TicTacToeGame()
    game.run()

def check_winner(b):
    """Check if there's a winner and return the player number (1 or 2), 3 for draw, 0 for ongoing"""
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != 0:
            return b[i][0]
    for j in range(3):  # Column check
        if b[0][j] == b[1][j] == b[2][j] != 0:
            return b[0][j]
    if b[0][0] == b[1][1] == b[2][2] != 0:  # Check diagonals
        return b[0][0]
    if b[0][2] == b[1][1] == b[2][0] != 0:
        return b[1][1]
    if all(b[i][j] != 0 for i in range(3) for j in range(3)):
        return 3  # Draw
    return 0  # No winner

def get_winning_line(b):
    """Get the winning line information for drawing"""
    # Check rows
    for i in range(3):
        if b[i][0] == b[i][1] == b[i][2] != 0:
            return ("row", i)
    # Check columns
    for j in range(3):
        if b[0][j] == b[1][j] == b[2][j] != 0:
            return ("col", j)
    # Check diagonals
    if b[0][0] == b[1][1] == b[2][2] != 0:
        return ("diag1", 0)
    if b[0][2] == b[1][1] == b[2][0] != 0:
        return ("diag2", 0)
    return None

def get_winning_move(b, player):
    """Find winning move for player"""
    # Check rows
    for i in range(3):
        row = b[i]
        if row.count(player) == 2 and 0 in row:
            return (i, row.index(0))
    # Check columns
    for j in range(3):
        col = [b[i][j] for i in range(3)]
        if col.count(player) == 2 and 0 in col:
            return (col.index(0), j)
    # Check diagonals
    diag = [b[i][i] for i in range(3)]
    if diag.count(player) == 2 and 0 in diag:
        idx = diag.index(0)
        return (idx, idx)
    anti_diag = [b[i][2 - i] for i in range(3)]
    if anti_diag.count(player) == 2 and 0 in anti_diag:
        idx = anti_diag.index(0)
        return (idx, 2 - idx)
    return None

def get_computer_move(b):
    """Get computer move with strategy - returns (row, col) tuple"""
    # Try to win
    win_move = get_winning_move(b, 2)
    if win_move:
        return win_move

    # Try to block
    block_move = get_winning_move(b, 1)
    if block_move:
        return block_move

    # Try to take center
    if b[1][1] == 0:
        return (1, 1)

    # Try corners
    corners = [(0, 0), (0, 2), (2, 0), (2, 2)]
    empty_corners = [c for c in corners if b[c[0]][c[1]] == 0]
    if empty_corners:
        return random.choice(empty_corners)

    # Random move
    empty = [(i, j) for i in range(3) for j in range(3) if b[i][j] == 0]
    if empty:
        return random.choice(empty)
    return (1, 1)  # Fallback (shouldn't reach here)

if __name__ == "__main__":
    main()

