import pygame
import sys
import json
import random

# Initialize Pygame and the mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe Collection")

# Fonts
font = pygame.font.Font(None, 74)
button_font = pygame.font.Font(None, 50)
description_font = pygame.font.Font(None, 36)

# Icon
game_icon = pygame.image.load('src/icon.png')
pygame.display.set_icon(game_icon)

# Load settings from file
def load_settings():
    with open('src/settings.json', 'r') as f:
        settings = json.load(f)
    return settings

settings = load_settings()
game_volume = settings["game_volume"]
music_volume = settings["music_volume"]
theme_name = settings["theme"]

# Load themes from file
def load_themes():
    with open('src/themes.json', 'r') as f:
        themes = json.load(f)
    return themes

themes = load_themes()
theme = themes[theme_name]

# Save settings to file
def save_settings():
    settings = {
        "game_volume": game_volume,
        "music_volume": music_volume,
        "theme": theme_name
    }
    with open('src/settings.json', 'w') as f:
        json.dump(settings, f)

# Apply the current theme to UI elements
def apply_theme():
    global theme
    theme = themes[theme_name]
    screen.fill(theme["background_color"])

    # Update colors for all buttons and other UI elements
    for button in main_menu_buttons + [arrow_left, arrow_right, select_button, back_button, theme_left, theme_right, settings_back_button, save_changes_button]:
        button.draw(screen)

    game_volume_slider.draw(screen)
    music_volume_slider.draw(screen)
    checkbox_bot.draw(screen)

# Load sound effects
click_sound = pygame.mixer.Sound("src/click.mp3")
click_sound.set_volume(game_volume)

# Load and play background music
pygame.mixer.music.load("src/background_music.mp3")
pygame.mixer.music.set_volume(music_volume)
pygame.mixer.music.play(-1)  # Play indefinitely

# Button class
class Button:
    def __init__(self, text, x, y, w, h, action=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(mouse_pos):
            color = theme["button_hover_color"]
        else:
            color = theme["button_color"]
        pygame.draw.rect(screen, color, self.rect)

        text_surface = button_font.render(self.text, True, theme["font_color"])
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.action:
                click_sound.play()
                self.action()

# Checkbox class
class Checkbox:
    def __init__(self, x, y, size, label, checked=False, action=None):
        self.rect = pygame.Rect(x, y, size, size)
        self.label = label
        self.checked = checked
        self.action = action

    def draw(self, screen):
        pygame.draw.rect(screen, theme["font_color"], self.rect, 2)
        if self.checked:
            pygame.draw.rect(screen, theme["font_color"], self.rect.inflate(-4, -4))

        label_surface = description_font.render(self.label, True, theme["font_color"])
        label_rect = label_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
        screen.blit(label_surface, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                click_sound.play()
                self.checked = not self.checked
                if self.action:
                    self.action(self.checked)

# Slider class
class Slider:
    def __init__(self, x, y, w, h, min_val=0, max_val=1, value=0.5, label=None, action=None):
        self.rect = pygame.Rect(x, y, w, h)
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.label = label
        self.action = action
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, theme["font_color"], self.rect, 2)

        handle_x = int(self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width)
        handle_rect = pygame.Rect(handle_x - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, theme["font_color"], handle_rect)

        if self.label:
            label_surface = description_font.render(f"{self.label}: {int(self.value * 100)}%", True, theme["font_color"])
            label_rect = label_surface.get_rect(midleft=(self.rect.right + 10, self.rect.centery))
            screen.blit(label_surface, label_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel_x = min(max(event.pos[0] - self.rect.x, 0), self.rect.width)
            self.value = self.min_val + (rel_x / self.rect.width) * (self.max_val - self.min_val)
            self.value = round(self.value, 2)
            if self.action:
                self.action(self.value)

# Theme selection logic
themes = load_themes()
theme_names = list(themes.keys())
current_theme_index = theme_names.index(theme_name)

def previous_theme():
    global current_theme_index, theme_name
    current_theme_index = (current_theme_index - 1) % len(theme_names)
    theme_name = theme_names[current_theme_index]
    apply_theme()

def next_theme():
    global current_theme_index, theme_name
    current_theme_index = (current_theme_index + 1) % len(theme_names)
    theme_name = theme_names[current_theme_index]
    apply_theme()


# Button actions
def play_game():
    game_mode_screen()

def open_settings():
    settings_menu()

def quit_game():
    pygame.quit()
    sys.exit()

def back_to_menu():
    main_menu()

def save_changes():
    save_settings()
    print(f"Settings Saved - Game Volume: {int(game_volume * 100)}%, Music Volume: {int(music_volume * 100)}%, Theme: {theme_name}")
    main_menu()

def previous_mode():
    global current_mode
    current_mode = (current_mode - 1) % len(game_modes)

def next_mode():
    global current_mode
    current_mode = (current_mode + 1) % len(game_modes)

def select_mode():
    mode_name = game_modes[current_mode]["name"]
    mode_type = "Bot" if checkbox_bot.checked else "Real Player"
    print(f"{mode_name} selected! Playing against: {mode_type}")
    if mode_name == "Classic":
        run_game_mode_classic(theme, checkbox_bot.checked)
    elif mode_name == "3-Tac":
        run_game_mode_3moves(theme, checkbox_bot.checked)
    elif mode_name == "Tetris-like":
        run_game_mode_tetris(theme, checkbox_bot.checked)
    elif mode_name == "Ultimate Tic-tac-toe":
        run_game_mode_ultimate(theme, checkbox_bot.checked)

# Create buttons
main_menu_buttons = [
    Button("Play", (SCREEN_WIDTH // 2) - 100, 250, 200, 60, play_game),
    Button("Settings", (SCREEN_WIDTH // 2) - 100, 350, 200, 60, open_settings),
    Button("Quit", (SCREEN_WIDTH // 2) - 100, 450, 200, 60, quit_game),
]
# Game mode information
game_modes = [
    {"name": "Classic", "desc": "Classic Tic-Tac-Toe, 3x3 board"},
    {"name": "3-Tac", "desc": "You are limited to 3 last moves"},
    {"name": "Tetris-like", "desc": "Tic-tac-toe + tetris"},
    {"name": "Ultimate Tic-tac-toe", "desc": "Meta-game"},
]

current_mode = 0

# Navigation buttons for game mode selection
arrow_left = Button("<", (SCREEN_WIDTH // 2) - 155, 400, 60, 60, previous_mode)
arrow_right = Button(">", (SCREEN_WIDTH // 2) + 95, 400, 60, 60, next_mode)
select_button = Button("Select", (SCREEN_WIDTH // 2) - 75, 550, 150, 60, select_mode)
back_button = Button("Back", (SCREEN_WIDTH // 2) + 125, 650, 150, 60, back_to_menu)

# Checkbox for playing against a bot
checkbox_bot = Checkbox((SCREEN_WIDTH // 2) - 55, 500, 30, "Play against a bot", action=None)

def set_game_volume(value):
    global game_volume
    game_volume = value
    click_sound.set_volume(game_volume)
    print(f"Game Volume: {int(game_volume * 100)}%")

def set_music_volume(value):
    global music_volume
    music_volume = value
    pygame.mixer.music.set_volume(music_volume)
    print(f"Music Volume: {int(music_volume * 100)}%")

# Settings sliders
game_volume_slider = Slider(
    (SCREEN_WIDTH // 2) - 100, 300, 200, 20, 0, 1, game_volume, "Game", set_game_volume)
music_volume_slider = Slider(
    (SCREEN_WIDTH // 2) - 100, 350, 200, 20, 0, 1, music_volume, "Music", set_music_volume)

# Theme selection with arrows
theme_left = Button("<", (SCREEN_WIDTH // 2) - 150, 420, 40, 40, previous_theme)
theme_right = Button(">", (SCREEN_WIDTH // 2) + 110, 420, 40, 40, next_theme)

# Display current theme
def draw_current_theme(screen):
    theme_text = theme_name
    theme_surface = description_font.render(f"Theme: {theme_text}", True, theme["font_color"])
    theme_rect = theme_surface.get_rect(center=((SCREEN_WIDTH // 2), 440))
    screen.blit(theme_surface, theme_rect)

# Settings back button and save button
settings_back_button = Button("Back", (SCREEN_WIDTH // 2) + 125, 650, 150, 60, back_to_menu)
save_changes_button = Button("Save", (SCREEN_WIDTH // 2) - 75, 650, 150, 60, save_changes)

# Settings menu
def settings_menu():
    while True:
        screen.fill(theme["background_color"])
        title_surface = font.render("Settings", True, theme["font_color"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        game_volume_slider.draw(screen)
        music_volume_slider.draw(screen)
        theme_left.draw(screen)
        theme_right.draw(screen)
        draw_current_theme(screen)
        settings_back_button.draw(screen)
        save_changes_button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in [settings_back_button, save_changes_button, theme_left, theme_right]:
                        button.handle_event(event)
            game_volume_slider.handle_event(event)
            music_volume_slider.handle_event(event)

        pygame.display.update()

# Main menu loop
def main_menu():
    apply_theme()  # Apply the theme colors at the start
    while True:
        screen.fill(theme["background_color"])
        title_surface = font.render("Tic-Tac-Toe Collection", True, theme["font_color"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        for button in main_menu_buttons:
            button.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in main_menu_buttons:
                        button.handle_event(event)

        pygame.display.update()

# Game mode screen
def game_mode_screen():
    checkbox_bot.checked = False
    while True:
        screen.fill(theme["background_color"])
        title_surface = font.render("Select Game Mode", True, theme["font_color"])
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_surface, title_rect)

        mode_name = game_modes[current_mode]["name"]
        mode_desc = game_modes[current_mode]["desc"]

        mode_name_surface = button_font.render(mode_name, True, theme["font_color"])
        mode_name_rect = mode_name_surface.get_rect(center=(SCREEN_WIDTH // 2, 250))
        screen.blit(mode_name_surface, mode_name_rect)

        mode_desc_surface = description_font.render(mode_desc, True, theme["font_color"])
        mode_desc_rect = mode_desc_surface.get_rect(center=(SCREEN_WIDTH // 2, 300))
        screen.blit(mode_desc_surface, mode_desc_rect)

        arrow_left.draw(screen)
        arrow_right.draw(screen)
        select_button.draw(screen)
        back_button.draw(screen)
        checkbox_bot.draw(screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                click_sound.play()
                previous_mode()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                click_sound.play()
                next_mode()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in [arrow_left, arrow_right, select_button, back_button]:
                        button.handle_event(event)
                    checkbox_bot.handle_event(event)

        pygame.display.update()


def run_game_mode_classic(theme, play_with_bot=False):

    # Constants
    screen_width, screen_height = 600, 800
    grid_size = 500
    offset = (screen_width - grid_size) // 2
    cell_size = grid_size // 3
    font = pygame.font.Font(None, 40)

    # Theme Colors
    bg_color = theme["background_color"]
    font_color = theme["font_color"]
    grid_color = theme["grid_color"]
    x_color = theme["x_color"]
    o_color = theme["o_color"]
    highlight_color = theme["highlight_color"]

    # Initialize the markers
    markers = [[0 for _ in range(3)] for _ in range(3)]
    clicked = False
    player = 1
    player1_score, player2_score = 0, 0
    game_over = False
    winner = 0
    winner_line = None  # To store the coordinates of the winning line

    def draw_grid():
        screen.fill(bg_color)
        for x in range(1, 3):
            pygame.draw.line(screen, grid_color, (x * cell_size + offset, offset), (x * cell_size + offset, grid_size + offset), 8)
            pygame.draw.line(screen, grid_color, (offset, x * cell_size + offset), (grid_size + offset, x * cell_size + offset), 8)

    def draw_xo():
        top_shift = round(cell_size * 0.15)
        bottom_shift = round(cell_size * 0.85)
        for row in range(3):
            for col in range(3):
                x_pos = col * cell_size + offset
                y_pos = row * cell_size + offset
                if markers[row][col] == 1:
                    pygame.draw.line(screen, x_color, (x_pos + top_shift, y_pos + top_shift), (x_pos + bottom_shift, y_pos + bottom_shift), 8)
                    pygame.draw.line(screen, x_color, (x_pos + top_shift, y_pos + bottom_shift), (x_pos + bottom_shift, y_pos + top_shift), 8)
                elif markers[row][col] == -1:
                    pygame.draw.circle(screen, o_color, (x_pos + cell_size // 2, y_pos + cell_size // 2), (cell_size // 2) - 20, 10)

    def draw_players_score():
        p1_font = pygame.font.SysFont(None, 40)
        p1_color = theme["p1_color"]
        p2_font = pygame.font.SysFont(None, 40)
        p2_color = theme["p2_color"]
        if player == -1:
            p1_font, p2_font = p2_font, p1_font
            p1_color, p2_color = p2_color, p1_color

        p1_img = p1_font.render('Player X: ' + str(player1_score), True, p1_color)
        p1_rect = p1_img.get_rect(center=(screen_width // 3, grid_size + offset * 2))
        screen.blit(p1_img, p1_rect)

        p2_img = p2_font.render('Player O: ' + str(player2_score), True, p2_color)
        p2_rect = p2_img.get_rect(center=(screen_width - screen_width // 3, grid_size + offset * 2))
        screen.blit(p2_img, p2_rect)

        esc_font = pygame.font.SysFont(None, 30)
        esc_img = esc_font.render("Esc - menu", True, font_color)
        ecs_rect = esc_img.get_rect(center=(60, 20))
        screen.blit(esc_img, ecs_rect)

    def check_winner():
        nonlocal winner, game_over, player1_score, player2_score, winner_line

        # Check rows
        for row in range(3):
            if sum(markers[row]) == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 2)]
                return
            elif sum(markers[row]) == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 2)]
                return

        # Check columns
        for col in range(3):
            col_sum = markers[0][col] + markers[1][col] + markers[2][col]
            if col_sum == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(0, col), (2, col)]
                return
            elif col_sum == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(0, col), (2, col)]
                return

        # Check diagonals
        diag1 = markers[0][0] + markers[1][1] + markers[2][2]
        diag2 = markers[0][2] + markers[1][1] + markers[2][0]

        if diag1 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 0), (2, 2)]
        elif diag1 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 0), (2, 2)]
        elif diag2 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 2), (2, 0)]
        elif diag2 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 2), (2, 0)]

        # Check for a tie
        if all(marker != 0 for row in markers for marker in row) and winner == 0:
            winner = -1
            game_over = True

    def draw_winner_text(winner):
        if winner == -1:
            win_text = 'Tie!'
        else:
            win_text = f'Player {"X" if winner == 1 else "O"} wins!'

        text = font.render(win_text, True, font_color)
        text_rect = text.get_rect(center=(screen_width // 2, grid_size + offset + ((screen_height - (grid_size + offset)) // 2)))
        pa_font = pygame.font.SysFont(None, 60, bold=True, italic=True)
        play_again_img = pa_font.render("Press SPACE to play again", True, font_color)
        play_again_rect = play_again_img.get_rect(center=(screen_width // 2, text_rect.bottom + offset))
        screen.blit(text, text_rect)
        screen.blit(play_again_img, play_again_rect)


    def highlight_winner_line(winner_line):
        if not winner_line:
            return
        # Start and end points based on the grid
        start_pos = winner_line[0]
        end_pos = winner_line[1]

        # Convert grid positions to pixel positions
        start_px = (start_pos[1] * cell_size + cell_size // 2 + offset, start_pos[0] * cell_size + cell_size // 2 + offset)
        end_px = (end_pos[1] * cell_size + cell_size // 2 + offset, end_pos[0] * cell_size + cell_size // 2 + offset)

        pygame.draw.line(screen, highlight_color, start_px, end_px, 10)

    def bot_move():
        # Check for possible winning move to take or to block opponent's winning move
        for player_marker in [-1, 1]:
            for row in range(3):
                if sum(markers[row]) == player_marker * 2:
                    for col in range(3):
                        if markers[row][col] == 0:
                            markers[row][col] = -1
                            return

            for col in range(3):
                col_sum = sum(markers[r][col] for r in range(3))
                if col_sum == player_marker * 2:
                    for row in range(3):
                        if markers[row][col] == 0:
                            markers[row][col] = -1
                            return

            # Diagonal checks
            diag1 = sum(markers[i][i] for i in range(3))
            if diag1 == player_marker * 2:
                for i in range(3):
                    if markers[i][i] == 0:
                        markers[i][i] = -1
                        return

            diag2 = sum(markers[i][2 - i] for i in range(3))
            if diag2 == player_marker * 2:
                for i in range(3):
                    if markers[i][2 - i] == 0:
                        markers[i][2 - i] = -1
                        return

        # No winning or blocking move, choose random empty cell
        empty_cells = [(r, c) for r in range(3) for c in range(3) if markers[r][c] == 0]
        if empty_cells:
            row, col = random.choice(empty_cells)
            markers[row][col] = -1



    def get_cell_from_click(pos):
        x, y = pos
        if offset <= x <= offset + grid_size and offset <= y <= offset + grid_size:
            col = (x - offset) // cell_size
            row = (y - offset) // cell_size
            return int(row), int(col)
        return None, None

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game
                    click_sound.play()
                    markers = [[0 for _ in range(3)] for _ in range(3)]
                    winner = 0
                    game_over = False
                    winner_line = None
                    player = 1
            else:
                if not game_over and ((play_with_bot and player == 1) or not play_with_bot):
                    if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                        clicked = True
                    if event.type == pygame.MOUSEBUTTONUP and clicked:
                        clicked = False
                        pos = pygame.mouse.get_pos()
                        row, col = get_cell_from_click(pos)
                        if row is not None and col is not None and markers[row][col] == 0:
                            click_sound.play()
                            markers[row][col] = player
                            check_winner()
                            player *= -1

                            if not game_over and play_with_bot and player == -1:
                                pygame.time.set_timer(pygame.USEREVENT, 1000)

        # Bot reaction move
        if play_with_bot and player == -1 and not game_over:
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Turn off the timer
                bot_move()
                check_winner()
                player *= -1

        screen.fill(bg_color)
        draw_grid()
        draw_xo()
        draw_players_score()

        if game_over:
            draw_winner_text(winner)
            if winner_line:
                highlight_winner_line(winner_line)

        pygame.display.flip()

def run_game_mode_3moves(theme, play_with_bot=False):

    # Constants
    screen_width, screen_height = 600, 800
    grid_size = 500
    offset = (screen_width - grid_size) // 2
    cell_size = grid_size // 3
    font = pygame.font.Font(None, 40)

    # Theme Colors
    bg_color = theme["background_color"]
    font_color = theme["font_color"]
    grid_color = theme["grid_color"]
    x_color = theme["x_color"]
    o_color = theme["o_color"]
    highlight_color = theme["highlight_color"]


    # Initialize the markers and lists
    markers = [[0 for _ in range(3)] for _ in range(3)]
    x_list = []
    o_list = []
    clicked = False
    player = 1
    player1_score = 0
    player2_score = 0
    game_over = False
    winner = 0
    winner_line = None

    def draw_grid():
        screen.fill(bg_color)
        for x in range(1, 3):
            pygame.draw.line(screen, grid_color, (x * cell_size + offset, offset), (x * cell_size + offset, grid_size + offset), 6)
            pygame.draw.line(screen, grid_color, (offset, x * cell_size + offset), (grid_size + offset, x * cell_size + offset), 6)


    def draw_xo():
        top_shift = round(cell_size * 0.15)
        bottom_shift = round(cell_size * 0.85)
        for row in range(3):
            for col in range(3):
                x_pos = col * cell_size + offset
                y_pos = row * cell_size + offset
                if markers[row][col] == 1:
                    color = x_color if (row, col) not in x_list[:1] or len(x_list) < 3 else '#808080'
                    pygame.draw.line(screen, color, (x_pos + top_shift, y_pos + top_shift), (x_pos + bottom_shift, y_pos + bottom_shift), 8)
                    pygame.draw.line(screen, color, (x_pos + top_shift, y_pos + bottom_shift), (x_pos + bottom_shift, y_pos + top_shift), 8)
                elif markers[row][col] == -1:
                    color = o_color if (row, col) not in o_list[:1] or len(o_list) < 3 else '#808080'
                    pygame.draw.circle(screen, color, (x_pos + cell_size // 2, y_pos + cell_size // 2), (cell_size // 2) - 20, 10)


    def draw_players_score():
        p1_font = pygame.font.SysFont(None, 40)
        p1_color = theme["p1_color"]
        p2_font = pygame.font.SysFont(None, 40)
        p2_color = theme["p2_color"]
        if player == -1:
            p1_font, p2_font = p2_font, p1_font
            p1_colour, p2_colour = p2_color, p1_color

        p1_img = p1_font.render('Player X: ' + str(player1_score), True, p1_color)
        p1_rect = p1_img.get_rect(center=(screen_width // 3, grid_size + offset * 2))
        screen.blit(p1_img, p1_rect)

        p2_img = p2_font.render('Player O: ' + str(player2_score), True, p2_color)
        p2_rect = p2_img.get_rect(center=(screen_width - screen_width // 3, grid_size + offset * 2))
        screen.blit(p2_img, p2_rect)

        esc_font = pygame.font.SysFont(None, 30)
        esc_img = esc_font.render("Esc - menu", True, font_color)
        ecs_rect = esc_img.get_rect(center=(60, 20))
        screen.blit(esc_img, ecs_rect)


    def check_winner():
        nonlocal winner, game_over, player1_score, player2_score, winner_line

        # Check rows
        for row in range(3):
            if sum(markers[row]) == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 1), (row, 2)]
                return
            elif sum(markers[row]) == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 1), (row, 2)]
                return

        # Check columns
        for col in range(3):
            col_sum = markers[0][col] + markers[1][col] + markers[2][col]
            if col_sum == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(0, col), (1, col), (2, col)]
                return
            elif col_sum == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(0, col), (1, col), (2, col)]
                return

        # Check diagonals
        diag1 = markers[0][0] + markers[1][1] + markers[2][2]
        diag2 = markers[0][2] + markers[1][1] + markers[2][0]

        if diag1 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 0), (1, 1), (2, 2)]
        elif diag1 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 0), (1, 1), (2, 2)]
        elif diag2 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 2), (1, 1), (2, 0)]
        elif diag2 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 2), (1, 1), (2, 0)]

        # Check for a tie
        if all([marker for row in markers for marker in row]):
            winner = -1
            game_over = True


    def draw_winner_text(winner):
        if winner == -1:
            win_text = 'Tie!'
        else:
            win_text = f'Player {"X" if winner == 1 else "O"} wins!'

        text = font.render(win_text, True, font_color)
        text_rect = text.get_rect(center=(screen_width // 2, grid_size + offset + ((screen_height - (grid_size + offset)) // 2)))
        pa_font = pygame.font.SysFont(None, 60, bold=True, italic=True)
        play_again_img = pa_font.render("Press SPACE to play again", True, font_color)
        play_again_rect = play_again_img.get_rect(center=(screen_width // 2, text_rect.bottom + offset))
        screen.blit(text, text_rect)
        screen.blit(play_again_img, play_again_rect)


    def highlight_winner_line(winner_line):
        if not winner_line:
            return
        # Start and end points based on the grid
        start_pos = winner_line[0]
        end_pos = winner_line[-1]

        # Convert grid positions to pixel positions
        start_px = (start_pos[1] * cell_size + cell_size // 2 + offset, start_pos[0] * cell_size + cell_size // 2 + offset)
        end_px = (end_pos[1] * cell_size + cell_size // 2 + offset, end_pos[0] * cell_size + cell_size // 2 + offset)

        pygame.draw.line(screen, highlight_color, start_px, end_px, 10)

    def bot_move():
        # Function to simulate a move and check if it forms a winning line with the last 3 moves
        def is_winning_move(r, c, player_marker):
            # Place the move temporarily
            temp_markers = [row[:] for row in markers]
            temp_markers[r][c] = player_marker
            # Remove the oldest move
            if player_marker == 1:
                if len(x_list) == 3:
                    row, col = x_list[0]
                    temp_markers[row][col] = 0
            else:
                if len(o_list) == 3:
                    row, col = o_list[0]
                    temp_markers[row][col] = 0

            # Check rows, columns, and diagonals but only count the last 3 of the same marker
            def check_line(segment):
                count = 0
                for mark in segment:
                    if mark == player_marker:
                        count += 1
                        if count == 3:
                            return True
                    else:
                        count = 0
                return False

            # Check row
            if check_line(temp_markers[r]):
                return True

            # Check column
            if check_line([temp_markers[i][c] for i in range(3)]):
                return True

            # Check diagonal (if applicable)
            if r == c and check_line([temp_markers[i][i] for i in range(3)]):
                return True

            # Check anti-diagonal (if applicable)
            if r + c == 2 and check_line([temp_markers[i][2 - i] for i in range(3)]):
                return True

            return False

        # Try to find a winning move for the bot or block the opponent's winning move
        for player_marker in [-1, 1]:
            for row in range(3):
                for col in range(3):
                    if markers[row][col] == 0:
                        if is_winning_move(row, col, player_marker):
                            return row, col

        # No winning or blocking move, choose a random empty cell
        empty_cells = [(r, c) for r in range(3) for c in range(3) if markers[r][c] == 0]
        if empty_cells:
            row, col = random.choice(empty_cells)
            return row, col

    def get_cell_from_click(pos):
        x, y = pos
        if offset <= x <= offset + grid_size and offset <= y <= offset + grid_size:
            col = (x - offset) // cell_size
            row = (y - offset) // cell_size
            return int(row), int(col)
        return None, None


    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game
                    click_sound.play()
                    markers = [[0 for _ in range(3)] for _ in range(3)]
                    x_list = []
                    o_list = []
                    winner = 0
                    game_over = False
                    winner_line = None
                    player = 1
            else:
                if not game_over and ((play_with_bot and player == 1) or not play_with_bot):
                    if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                        clicked = True
                    if event.type == pygame.MOUSEBUTTONUP and clicked:
                        clicked = False
                        pos = pygame.mouse.get_pos()
                        row, col = get_cell_from_click(pos)
                        if row is not None and col is not None and markers[row][col] == 0:
                            click_sound.play()
                            markers[row][col] = player
                            if player == 1:
                                x_list.append((row, col))
                                if len(x_list) == 4:
                                    y_rem, x_rem = x_list.pop(0)
                                    markers[y_rem][x_rem] = 0
                            else:
                                o_list.append((row, col))
                                if len(o_list) == 4:
                                    y_rem, x_rem = o_list.pop(0)
                                    markers[y_rem][x_rem] = 0
                            player *= -1
                            check_winner()


                            if not game_over and play_with_bot and player == -1:
                                pygame.time.set_timer(pygame.USEREVENT, 1000)

        # Bot reaction move
        if play_with_bot and player == -1 and not game_over:
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Turn off the timer
                row, col = bot_move()
                markers[row][col] = -1
                o_list.append((row, col))
                if len(o_list) == 4:
                    y_rem, x_rem = o_list.pop(0)
                    markers[y_rem][x_rem] = 0
                check_winner()
                player *= -1

        screen.fill(bg_color)
        draw_grid()
        draw_xo()
        draw_players_score()

        if game_over:
            draw_winner_text(winner)
            if winner_line:
                highlight_winner_line(winner_line)

        pygame.display.flip()

def run_game_mode_tetris(theme, play_with_bot=False):

    # Constants
    screen_width, screen_height = 600, 800
    grid_size = 500
    offset = (screen_width - grid_size) // 2
    cell_size = grid_size // 3
    font = pygame.font.Font(None, 40)

    # Theme Colors
    bg_color = theme["background_color"]
    font_color = theme["font_color"]
    grid_color = theme["grid_color"]
    x_color = theme["x_color"]
    o_color = theme["o_color"]
    highlight_color = theme["highlight_color"]

    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption('TicTacToe')

    # Initialize the markers
    markers = [[0 for _ in range(3)] for _ in range(3)]
    clicked = False
    player = 1
    player1_score, player2_score = 0, 0
    game_over = False
    winner = 0
    winner_line = None  # To store the coordinates of the winning line

    drop_in_progress = False
    drop_column = None
    drop_row = None
    drop_y = 0
    drop_speed = 5
    drop_frame_delay = 5

    def draw_grid():
        screen.fill(bg_color)
        for x in range(1, 3):
            pygame.draw.line(screen, grid_color, (x * cell_size + offset, offset), (x * cell_size + offset, grid_size + offset), 8)
            pygame.draw.line(screen, grid_color, (offset, x * cell_size + offset), (grid_size + offset, x * cell_size + offset), 8)

    def draw_xo():
        top_shift = round(cell_size * 0.15)
        bottom_shift = round(cell_size * 0.85)
        for row in range(3):
            for col in range(3):
                x_pos = col * cell_size + offset
                y_pos = row * cell_size + offset
                if markers[row][col] == 1:
                    pygame.draw.line(screen, x_color, (x_pos + top_shift, y_pos + top_shift), (x_pos + bottom_shift, y_pos + bottom_shift), 8)
                    pygame.draw.line(screen, x_color, (x_pos + top_shift, y_pos + bottom_shift), (x_pos + bottom_shift, y_pos + top_shift), 8)
                elif markers[row][col] == -1:
                    pygame.draw.circle(screen, o_color, (x_pos + cell_size // 2, y_pos + cell_size // 2), (cell_size // 2) - 20, 10)

    def draw_players_score():
        p1_font = pygame.font.SysFont(None, 40)
        p1_color = theme["p1_color"]
        p2_font = pygame.font.SysFont(None, 40)
        p2_color = theme["p2_color"]
        if player == -1:
            p1_font, p2_font = p2_font, p1_font
            p1_color, p2_color = p2_color, p1_color

        p1_img = p1_font.render('Player X: ' + str(player1_score), True, p1_color)
        p1_rect = p1_img.get_rect(center=(screen_width // 3, grid_size + offset * 2))
        screen.blit(p1_img, p1_rect)

        p2_img = p2_font.render('Player O: ' + str(player2_score), True, p2_color)
        p2_rect = p2_img.get_rect(center=(screen_width - screen_width // 3, grid_size + offset * 2))
        screen.blit(p2_img, p2_rect)

        esc_font = pygame.font.SysFont(None, 30)
        esc_img = esc_font.render("Esc - menu", True, font_color)
        ecs_rect = esc_img.get_rect(center=(60, 20))
        screen.blit(esc_img, ecs_rect)

    def check_winner():
        nonlocal winner, game_over, player1_score, player2_score, winner_line

        # Check rows
        for row in range(3):
            if sum(markers[row]) == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 2)]
                return
            elif sum(markers[row]) == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(row, 0), (row, 2)]
                return

        # Check columns
        for col in range(3):
            col_sum = markers[0][col] + markers[1][col] + markers[2][col]
            if col_sum == 3:
                winner = 1
                player1_score += 1
                game_over = True
                winner_line = [(0, col), (2, col)]
                return
            elif col_sum == -3:
                winner = 2
                player2_score += 1
                game_over = True
                winner_line = [(0, col), (2, col)]
                return

        # Check diagonals
        diag1 = markers[0][0] + markers[1][1] + markers[2][2]
        diag2 = markers[0][2] + markers[1][1] + markers[2][0]

        if diag1 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 0), (2, 2)]
        elif diag1 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 0), (2, 2)]
        elif diag2 == 3:
            winner = 1
            player1_score += 1
            game_over = True
            winner_line = [(0, 2), (2, 0)]
        elif diag2 == -3:
            winner = 2
            player2_score += 1
            game_over = True
            winner_line = [(0, 2), (2, 0)]

        # Check for a tie
        if all(marker != 0 for row in markers for marker in row) and winner == 0:
            winner = -1
            game_over = True

    def draw_winner_text(winner):
        if winner == -1:
            win_text = 'Tie!'
        else:
            win_text = f'Player {"X" if winner == 1 else "O"} wins!'

        text = font.render(win_text, True, font_color)
        text_rect = text.get_rect(center=(screen_width // 2, grid_size + offset + ((screen_height - (grid_size + offset)) // 2)))
        pa_font = pygame.font.SysFont(None, 60, bold=True, italic=True)
        play_again_img = pa_font.render("Press SPACE to play again", True, font_color)
        play_again_rect = play_again_img.get_rect(center=(screen_width // 2, text_rect.bottom + offset))
        screen.blit(text, text_rect)
        screen.blit(play_again_img, play_again_rect)


    def highlight_winner_line(winner_line):
        if not winner_line:
            return
        # Start and end points based on the grid
        start_pos = winner_line[0]
        end_pos = winner_line[1]

        # Convert grid positions to pixel positions
        start_px = (start_pos[1] * cell_size + cell_size // 2 + offset, start_pos[0] * cell_size + cell_size // 2 + offset)
        end_px = (end_pos[1] * cell_size + cell_size // 2 + offset, end_pos[0] * cell_size + cell_size // 2 + offset)

        pygame.draw.line(screen, highlight_color, start_px, end_px, 10)

    def bot_move():
        # Number of rows and columns in the Tic-tac-toe grid
        rows, columns = 3, 3

        # Check if placing a piece in a specific column can result in a win
        def can_win_next(player_marker, column):
            # Simulate dropping the piece in the given column
            for row in range(rows-1, -1, -1):
                if markers[row][column] == 0:
                    markers[row][column] = player_marker
                    # Check if this move wins the game
                    if check_winner_simulated(markers, player_marker):
                        markers[row][column] = 0
                        return True
                    markers[row][column] = 0
                    break
            return False

        # Function to check if there's a winner on a simulated board
        def check_winner_simulated(board, player_marker):
            # Check rows
            for row in range(rows):
                if all(board[row][col] == player_marker for col in range(columns)):
                    return True
            # Check columns
            for col in range(columns):
                if all(board[row][col] == player_marker for row in range(rows)):
                    return True
            # Check diagonals
            if all(board[i][i] == player_marker for i in range(rows)):
                return True
            if all(board[i][columns-1-i] == player_marker for i in range(rows)):
                return True
            return False

        # Try to find a winning move for the bot
        for col in range(columns):
            if can_win_next(-1, col):
                return col

        # Try to block the opponent's winning move
        for col in range(columns):
            if can_win_next(1, col):
                return col

        # Prefer the center column if it's empty
        center_column = columns // 2
        if markers[0][center_column] == 0:
            return center_column

        # Choose a random column from the available ones
        empty_columns = [col for col in range(columns) if markers[0][col] == 0]
        return random.choice(empty_columns) if empty_columns else None

    def drop_piece(column, player):
        nonlocal drop_in_progress, drop_column, drop_row, drop_y
        for row in reversed(range(3)):
            if markers[row][column] == 0:
                drop_in_progress = True
                drop_column = column
                drop_row = row
                drop_y = 0
                return True
        return False


    def draw_dropping_piece(column, y, player):
        x_pos = column * cell_size + offset
        if player == 1:
            pygame.draw.line(screen, x_color, (x_pos + round(cell_size * 0.15), y + offset + round(cell_size * 0.15)),
                             (x_pos + round(cell_size * 0.85), y + offset + round(cell_size * 0.85)), 8)
            pygame.draw.line(screen, x_color, (x_pos + round(cell_size * 0.15), y + offset + round(cell_size * 0.85)),
                             (x_pos + round(cell_size * 0.85), y + offset + round(cell_size * 0.15)), 8)
        else:
            pygame.draw.circle(screen, o_color, (column * cell_size + offset + (cell_size // 2), y + offset + (cell_size // 2)), cell_size * 0.4, 10)

    run = True
    frame_count = 0

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            if game_over:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game
                    click_sound.play()
                    markers = [[0 for _ in range(3)] for _ in range(3)]
                    winner = 0
                    game_over = False
                    winner_line = None
                    player = 1
            else:
                if not game_over and ((play_with_bot and player == 1) or not play_with_bot) and not drop_in_progress:
                    if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                        clicked = True
                    if event.type == pygame.MOUSEBUTTONUP and clicked:
                        clicked = False
                        row, col = pygame.mouse.get_pos()
                        if (row > grid_size + offset or row < offset) or (col > grid_size + offset or col < offset):
                            continue
                        cell_row = (row - offset) // cell_size
                        if drop_piece(cell_row, player):
                            click_sound.play()

                            if not game_over and play_with_bot and player == 1:
                                pygame.time.set_timer(pygame.USEREVENT, 1000)

        if drop_in_progress:
            if frame_count % drop_frame_delay == 0:
                if drop_y < (drop_row * cell_size):
                    drop_y += drop_speed
                else:
                    markers[drop_row][drop_column] = player
                    player *= -1
                    drop_in_progress = False
                    check_winner()

        # Bot reaction move
        if play_with_bot and player == -1 and not game_over and not drop_in_progress:
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Turn off the timer
                drop_piece(bot_move(), player)
                check_winner()

        screen.fill(bg_color)
        draw_grid()
        draw_xo()
        draw_players_score()

        if drop_in_progress:
            draw_dropping_piece(drop_column, drop_y, player)

        if game_over:
            draw_winner_text(winner)
            if winner_line:
                highlight_winner_line(winner_line)

        pygame.display.flip()
        frame_count += 1
        frame_count %= 10000

def run_game_mode_ultimate(theme, play_with_bot=False):

    # Constants
    screen_width, screen_height = 600, 800
    cell_size = 60
    small_grid_size = cell_size * 3
    big_grid_size = small_grid_size * 3
    offset = (screen_width - big_grid_size) // 2
    font = pygame.font.Font(None, 40)

    # Theme Colors
    bg_color = theme["background_color"]
    font_color = theme["font_color"]
    grid_color = theme["grid_color"]
    x_color = theme["x_color"]
    o_color = theme["o_color"]
    highlight_color = theme["highlight_color"]

    # Initialize the markers
    markers = [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]
    big_markers = [[0 for _ in range(3)] for _ in range(3)]
    clicked = False
    player = 1
    player1_score, player2_score = 0, 0
    game_over = False
    active_board = None
    winner = 0

    def draw_grid():
        screen.fill(bg_color)
        # Draw the big grid
        for x in range(1, 3):
            pygame.draw.line(screen, grid_color, (x * small_grid_size + offset, offset), (x * small_grid_size + offset, big_grid_size + offset), 8)
            pygame.draw.line(screen, grid_color, (offset, x * small_grid_size + offset), (big_grid_size + offset, x * small_grid_size + offset), 8)
        # Draw the small grids
        for big_row in range(3):
            for big_col in range(3):
                for x in range(1, 3):
                    pygame.draw.line(screen, grid_color, (x * cell_size + big_col * small_grid_size + offset, big_row * small_grid_size + offset),
                                     (x * cell_size + big_col * small_grid_size + offset, (big_row + 1) * small_grid_size + offset), 4)
                    pygame.draw.line(screen, grid_color, (big_col * small_grid_size + offset, x * cell_size + big_row * small_grid_size + offset),
                                     ((big_col + 1) * small_grid_size + offset, x * cell_size + big_row * small_grid_size + offset), 4)

    def draw_xo():
        for big_row in range(3):
            for big_col in range(3):
                for small_row in range(3):
                    for small_col in range(3):
                        marker = markers[big_row][big_col][small_row][small_col]
                        x_pos = big_col * small_grid_size + small_col * cell_size + offset
                        y_pos = big_row * small_grid_size + small_row * cell_size + offset
                        if marker == 1:
                            pygame.draw.line(screen, x_color, (x_pos + 10, y_pos + 10), (x_pos + cell_size - 10, y_pos + cell_size - 10), 6)
                            pygame.draw.line(screen, x_color, (x_pos + 10, y_pos + cell_size - 10), (x_pos + cell_size - 10, y_pos + 10), 6)
                        elif marker == -1:
                            pygame.draw.circle(screen, o_color, (x_pos + cell_size // 2, y_pos + cell_size // 2), (cell_size // 2) - 10, 6)

    def draw_big_xo():
        for row in range(3):
            for col in range(3):
                marker = big_markers[row][col]
                x_pos = col * small_grid_size + offset
                y_pos = row * small_grid_size + offset
                if marker == 1:
                    pygame.draw.line(screen, x_color, (x_pos + 10, y_pos + 10), (x_pos + small_grid_size - 10, y_pos + small_grid_size - 10), 15)
                    pygame.draw.line(screen, x_color, (x_pos + 10, y_pos + small_grid_size - 10), (x_pos + small_grid_size - 10, y_pos + 10), 15)
                elif marker == -1:
                    pygame.draw.circle(screen, o_color, (x_pos + small_grid_size // 2, y_pos + small_grid_size // 2), (small_grid_size // 2) - 10, 15)

    def draw_players_score():
        p1_font = pygame.font.SysFont(None, 40)
        p1_color = theme["p1_color"]
        p2_font = pygame.font.SysFont(None, 40)
        p2_color = theme["p2_color"]
        if player == -1:
            p1_font, p2_font = p2_font, p1_font
            p1_color, p2_color = p2_color, p1_color

        p1_img = p1_font.render('Player X: ' + str(player1_score), True, p1_color)
        p1_rect = p1_img.get_rect(center=(screen_width // 3, big_grid_size + offset * 2))
        screen.blit(p1_img, p1_rect)

        p2_img = p2_font.render('Player O: ' + str(player2_score), True, p2_color)
        p2_rect = p2_img.get_rect(center=(screen_width - screen_width // 3, big_grid_size + offset * 2))
        screen.blit(p2_img, p2_rect)

        esc_font = pygame.font.SysFont(None, 30)
        esc_img = esc_font.render("Esc - menu", True, font_color)
        ecs_rect = esc_img.get_rect(center=(60, 15))
        screen.blit(esc_img, ecs_rect)

    def check_small_winner(big_row, big_col):
        small_board = markers[big_row][big_col]
        for row in range(3):
            if sum(small_board[row]) == 3:
                big_markers[big_row][big_col] = 1
                return True
            elif sum(small_board[row]) == -3:
                big_markers[big_row][big_col] = -1
                return True
        for col in range(3):
            if small_board[0][col] + small_board[1][col] + small_board[2][col] == 3:
                big_markers[big_row][big_col] = 1
                return True
            elif small_board[0][col] + small_board[1][col] + small_board[2][col] == -3:
                big_markers[big_row][big_col] = -1
                return True
        if small_board[0][0] + small_board[1][1] + small_board[2][2] == 3 or small_board[0][2] + small_board[1][1] + small_board[2][0] == 3:
            big_markers[big_row][big_col] = 1
            return True
        if small_board[0][0] + small_board[1][1] + small_board[2][2] == -3 or small_board[0][2] + small_board[1][1] + small_board[2][0] == -3:
            big_markers[big_row][big_col] = -1
            return True
        if all([marker for row in small_board for marker in row]):
            big_markers[big_row][big_col] = -2
            return False

    def check_big_winner():
        nonlocal player1_score, player2_score
        for row in range(3):
            if sum(big_markers[row]) == 3:
                player1_score += 1
                return 1
            elif sum(big_markers[row]) == -3:
                player2_score += 1
                return -1
        for col in range(3):
            if big_markers[0][col] + big_markers[1][col] + big_markers[2][col] == 3:
                player1_score += 1
                return 1
            elif big_markers[0][col] + big_markers[1][col] + big_markers[2][col] == -3:
                player2_score += 1
                return -1
        if big_markers[0][0] + big_markers[1][1] + big_markers[2][2] == 3 or big_markers[0][2] + big_markers[1][1] + big_markers[2][0] == 3:
            player1_score += 1
            return 1
        if big_markers[0][0] + big_markers[1][1] + big_markers[2][2] == -3 or big_markers[0][2] + big_markers[1][1] + big_markers[2][0] == -3:
            player2_score += 1
            return -1
        if all([marker != 0 for row in big_markers for marker in row]):
            return -2
        return 0

    def draw_winner_text(winner):
        if winner == -2:
            win_text = 'Tie!'
        else:
            win_text = f'Player {"X" if winner == 1 else "O"} wins!'

        text = font.render(win_text, True, font_color)
        text_rect = text.get_rect(center=(screen_width // 2, big_grid_size + ((screen_height - big_grid_size) // 2)))
        pa_font = pygame.font.SysFont(None, 60, bold=True, italic=True)
        play_again_img = pa_font.render("Press SPACE to play again", True, font_color)
        play_again_rect = play_again_img.get_rect(center=(screen_width // 2, text_rect.bottom + (screen_height - text_rect.bottom) // 2))
        screen.blit(text, text_rect)
        screen.blit(play_again_img, play_again_rect)

    def draw_active_board():
        if active_board is not None and big_markers[active_board[0]][active_board[1]] == 0:
            big_row, big_col = active_board
            x_pos = big_col * small_grid_size + offset
            y_pos = big_row * small_grid_size + offset
            pygame.draw.rect(screen, highlight_color, (x_pos, y_pos, small_grid_size, small_grid_size), 8)

    def bot_move():
        def check_small_winner(sim_markers, big_row, big_col, mark):
            # Check if a move results in a win in a small board
            for row in range(3):
                if all(sim_markers[big_row][big_col][row][col] == mark for col in range(3)):
                    return True
                if all(sim_markers[big_row][big_col][col][row] == mark for col in range(3)):
                    return True
            if all(sim_markers[big_row][big_col][i][i] == mark for i in range(3)):
                return True
            if all(sim_markers[big_row][big_col][i][2 - i] == mark for i in range(3)):
                return True
            return False

        def find_winning_move():
            # Check if there's a move that leads to an immediate small board win on the active board
            big_row, big_col = active_board
            if big_markers[big_row][big_col] == 0:
                for small_row in range(3):
                    for small_col in range(3):
                        if markers[big_row][big_col][small_row][small_col] == 0:
                            # Simulate the move
                            markers[big_row][big_col][small_row][small_col] = player
                            if check_small_winner(markers, big_row, big_col, player):
                                markers[big_row][big_col][small_row][small_col] = 0
                                return big_row, big_col, small_row, small_col
                            # Undo the move
                            markers[big_row][big_col][small_row][small_col] = 0
            return None

        def find_blocking_move():
            # Check if the opponent has a winning move and block it on the active board
            opponent = -player
            big_row, big_col = active_board
            if big_markers[big_row][big_col] == 0:
                for small_row in range(3):
                    for small_col in range(3):
                        if markers[big_row][big_col][small_row][small_col] == 0:
                            # Simulate the move for the opponent
                            markers[big_row][big_col][small_row][small_col] = opponent
                            if check_small_winner(markers, big_row, big_col, opponent):
                                markers[big_row][big_col][small_row][small_col] = 0
                                return big_row, big_col, small_row, small_col
                            # Undo the move
                            markers[big_row][big_col][small_row][small_col] = 0
            return None

        def strategic_move():
            big_row, big_col = active_board
            if big_markers[big_row][big_col] == 0:
                # List of preferred moves: corners, then edges
                preferred_moves = [(0, 0), (0, 2), (2, 0), (2, 2), (0, 1), (1, 0), (1, 2), (2, 1)]
                random.shuffle(preferred_moves)
                # Try to take a strategic move avoiding the center initially
                for move in preferred_moves:
                    small_row, small_col = move
                    if markers[big_row][big_col][small_row][small_col] == 0:
                        if not check_small_winner(markers, small_row, small_col, 1) and (small_col != big_col and small_row != big_row):
                            return big_row, big_col, small_row, small_col

                random.shuffle(preferred_moves)
                for move in preferred_moves:
                    small_row, small_col = move
                    if markers[big_row][big_col][small_row][small_col] == 0:
                        return big_row, big_col, small_row, small_col


                # Consider the center if no other good move is found
                center = (1, 1)
                if markers[big_row][big_col][center[0]][center[1]] == 0:
                    return big_row, big_col, center[0], center[1]

                # If all strategic positions are taken, choose the first available move
                for small_row in range(3):
                    for small_col in range(3):
                        if markers[big_row][big_col][small_row][small_col] == 0:
                            return big_row, big_col, small_row, small_col

            # Fallback if no strategic moves are possible
            for br in range(3):
                for bc in range(3):
                    if big_markers[br][bc] == 0:
                        for sr in range(3):
                            for sc in range(3):
                                if markers[br][bc][sr][sc] == 0:
                                    return br, bc, sr, sc

            return None

        # Look for an immediate winning move
        move = find_winning_move()
        if move:
            return move

        # Look for a blocking move
        move = find_blocking_move()
        if move:
            return move

        # Otherwise, follow the strategic move advice
        return strategic_move()

    def get_active_board_from_click(pos):
        nonlocal active_board
        x, y = pos
        if (x < offset or x > offset + big_grid_size) or (y < offset or y > offset + big_grid_size):
            return None
        big_col = (x - offset) // small_grid_size
        big_row = (y - offset) // small_grid_size

        # Allow playing on any board if the active board is won or a tie
        if active_board is None or big_markers[active_board[0]][active_board[1]] != 0:
            return big_row, big_col
        elif (big_row, big_col) == active_board:
            return big_row, big_col
        return None

    def get_cell_from_click(pos, big_row, big_col):
        x, y = pos
        small_x = (x - offset - big_col * small_grid_size) // cell_size
        small_y = (y - offset - big_row * small_grid_size) // cell_size
        return small_y, small_x

    run = True

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                click_sound.play()
                main_menu()
            if winner:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    # Reset game
                    click_sound.play()
                    markers = [[[[0 for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)]
                    big_markers = [[0 for _ in range(3)] for _ in range(3)]
                    clicked = False
                    player = 1
                    game_over = False
                    active_board = None
                    winner = 0
            else:
                if not game_over and ((play_with_bot and player == 1) or not play_with_bot):
                    if event.type == pygame.MOUSEBUTTONDOWN and not clicked:
                        clicked = True
                    if event.type == pygame.MOUSEBUTTONUP and clicked:
                        clicked = False
                        pos = pygame.mouse.get_pos()
                        new_active_board = get_active_board_from_click(pos)
                        if new_active_board is not None:
                            big_row, big_col = new_active_board
                            if big_markers[big_row][big_col] == 0:
                                small_row, small_col = get_cell_from_click(pos, big_row, big_col)
                                if markers[big_row][big_col][small_row][small_col] == 0:
                                    click_sound.play()
                                    markers[big_row][big_col][small_row][small_col] = player
                                    player *= -1
                                    check_small_winner(big_row, big_col)
                                    winner = check_big_winner()
                                    active_board = (small_row, small_col)
                                    if not game_over and play_with_bot and player == -1:
                                        pygame.time.set_timer(pygame.USEREVENT, 1000)
                            else:
                                active_board = None
                        else:
                            if active_board is None or big_markers[active_board[0]][active_board[1]] != 0:
                                active_board = new_active_board



        # Bot reaction move
        if play_with_bot and player == -1 and not winner:
            if event.type == pygame.USEREVENT:
                pygame.time.set_timer(pygame.USEREVENT, 0)  # Turn off the timer
                big_row, big_col, small_row, small_col = bot_move()
                markers[big_row][big_col][small_row][small_col] = player
                player *= -1
                check_small_winner(big_row, big_col)
                winner = check_big_winner()
                active_board = (small_row, small_col)

        screen.fill(bg_color)
        draw_grid()
        draw_xo()
        draw_big_xo()
        draw_players_score()
        draw_active_board()

        if winner:
            draw_winner_text(winner)

        pygame.display.flip()

# Start with the main menu
main_menu()