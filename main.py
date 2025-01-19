import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
HEX_RADIUS = 50  # Radius of hexagons
PLAYER_SCALE = 0.8  # Scaling factor for the player's hexagon (80% of HEX_RADIUS)
PLAYER_RADIUS = HEX_RADIUS * PLAYER_SCALE  # Player's hexagon size
FPS = 60

# Colors
COLOR_BG = (30, 30, 30)
COLOR_HEX = (100, 100, 200)  # Regular hexagon map color
COLOR_PLAYER = (0, 0, 255)  # Blue color for the player
COLOR_COIN = (255, 215, 0)
COLOR_ENEMY = (255, 0, 0)  # Red color for enemies (goblin tiles)
COLOR_TEXT = (255, 255, 255)
COLOR_TIME = (255, 215, 0)

# Screen Setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hexagon Grid Game")
clock = pygame.time.Clock()

# Fonts
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

# Helper Functions
def hex_to_pixel(q, r, size):
    """Convert axial hex coordinates to pixel coordinates."""
    x = size * 3/2 * q
    y = size * math.sqrt(3) * (r + q / 2)
    return x + SCREEN_WIDTH // 2, y + SCREEN_HEIGHT // 2

def draw_hexagon(surface, color, center, size, width=0):
    """Draw a hexagon at a given center point."""
    points = []
    for i in range(6):
        angle = math.radians(60 * i)
        x = center[0] + size * math.cos(angle)
        y = center[1] + size * math.sin(angle)
        points.append((x, y))
    pygame.draw.polygon(surface, color, points, width)

# Game Objects
class HexGrid:
    def __init__(self, radius):
        self.radius = radius
        self.hexes = {}  # Store hexes using axial coordinates (q, r)
        self.generate_grid()

    def generate_grid(self):
        """Generate a hex grid with correct spacing to avoid overlap."""
        margin = HEX_RADIUS * 2  # Safe margin from screen edges
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if -q - r in range(-self.radius, self.radius + 1):
                    center = hex_to_pixel(q, r, HEX_RADIUS)
                    if (
                        margin < center[0] < SCREEN_WIDTH - margin and
                        margin < center[1] < SCREEN_HEIGHT - margin
                    ):
                        self.hexes[(q, r)] = None  # None means empty for now

    def draw(self, surface):
        """Draw the entire grid."""
        for (q, r) in self.hexes.keys():
            center = hex_to_pixel(q, r, HEX_RADIUS)
            draw_hexagon(surface, COLOR_HEX, center, HEX_RADIUS, 2)

class Player:
    def __init__(self, q, r):
        self.q = q  # Player's hex coordinates (q, r)
        self.r = r

    def move(self, dq, dr):
        """Move the player to a new hex if within grid boundaries."""
        new_q = self.q + dq
        new_r = self.r + dr
        if (new_q, new_r) in grid.hexes:  # Only move if within the grid
            self.q = new_q
            self.r = new_r

    def draw(self, surface):
        """Draw the player as a blue hexagon."""
        center = hex_to_pixel(self.q, self.r, HEX_RADIUS)
        draw_hexagon(surface, COLOR_PLAYER, center, PLAYER_RADIUS)

class Coin:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def draw(self, surface):
        """Draw the coin as a yellow hexagon."""
        center = hex_to_pixel(self.q, self.r, HEX_RADIUS)
        draw_hexagon(surface, COLOR_COIN, center, HEX_RADIUS // 2)  # Smaller hexagon for coins

class Enemy:
    def __init__(self, q, r):
        self.q = q
        self.r = r

    def draw(self, surface):
        """Draw the enemy as a red hexagon with an outline."""
        center = hex_to_pixel(self.q, self.r, HEX_RADIUS)
        draw_hexagon(surface, COLOR_ENEMY, center, HEX_RADIUS, 2)  # Outline with width 2

# Game Logic
def start_screen():
    """Display the start screen with options to start or quit."""
    start_text = large_font.render("Gnome Conquest: Pygame Edition", True, COLOR_TEXT)
    start_button_text = font.render("Start", True, COLOR_TEXT)
    quit_button_text = font.render("Quit", True, COLOR_TEXT)

    # Main game loop for the start screen
    while True:
        screen.fill(COLOR_BG)

        # Draw start screen elements
        screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(start_button_text, (SCREEN_WIDTH // 2 - start_button_text.get_width() // 2, SCREEN_HEIGHT // 2))
        screen.blit(quit_button_text, (SCREEN_WIDTH // 2 - quit_button_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if start_button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)).collidepoint(mouse_pos):
                    return  # Start the game
                elif quit_button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)).collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

def main():
    global grid  # Make grid accessible
    running = True
    grid = HexGrid(5)  # Create a hex grid with radius 5
    player = Player(0, 0)  # Start the player at the center
    coins = []
    enemies = []

    # Spawn 3 random enemies (goblin tiles)
    for _ in range(3):
        while True:
            q = random.randint(-grid.radius, grid.radius)
            r = random.randint(-grid.radius, grid.radius)
            if (q, r) in grid.hexes and (q, r) != (0, 0):  # Avoid player's starting position
                enemies.append(Enemy(q, r))
                break

    # Spawn 3 random coins, ensuring they don't overlap with enemies or the player
    for _ in range(3):
        while True:
            q = random.randint(-grid.radius, grid.radius)
            r = random.randint(-grid.radius, grid.radius)
            if (q, r) in grid.hexes and (q, r) != (0, 0):  # Avoid player's starting position
                # Ensure the coin doesn't spawn on an enemy's position
                if (q, r) not in [(enemy.q, enemy.r) for enemy in enemies]:
                    coins.append(Coin(q, r))
                    break

    collected_coins = 0  # Track the number of coins collected
    start_time = pygame.time.get_ticks()  # Start timer
    best_time = None  # Track best time
    game_over = False

    while running:
        screen.fill(COLOR_BG)

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if not game_over:  # Only allow movement if the game isn't over
                    if event.key == pygame.K_w:
                        player.move(0, -1)
                    elif event.key == pygame.K_e:
                        player.move(1, -1)
                    elif event.key == pygame.K_a:
                        player.move(-1, 0)
                    elif event.key == pygame.K_d:
                        player.move(1, 0)
                    elif event.key == pygame.K_s:
                        player.move(0, 1)
                    elif event.key == pygame.K_z:
                        player.move(-1, 1)
                    elif event.key == pygame.K_x:
                        player.move(1, 1)
                elif event.key == pygame.K_r:  # Replay
                    return main()

        if not game_over:
            # Check if the player collects any coins
            for coin in coins[:]:
                if (player.q, player.r) == (coin.q, coin.r):
                    coins.remove(coin)
                    collected_coins += 1

            # Check if the player collides with an enemy
            for enemy in enemies:
                if (player.q, player.r) == (enemy.q, enemy.r):
                    game_over = True
                    best_time = None  # No best time since the player lost

            # Check win condition
            if collected_coins >= 3:
                game_over = True
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                if best_time is None or elapsed_time < best_time:
                    best_time = elapsed_time

        # Draw Grid, Player, Coins, and Enemies
        grid.draw(screen)
        player.draw(screen)
        for coin in coins:
            coin.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        # Display collected coins
        coin_text = font.render(f"Coins: {collected_coins}/3", True, COLOR_TEXT)
        screen.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 20, SCREEN_HEIGHT - coin_text.get_height() - 20))

        # If the game is over, display time
        if game_over:
            game_over_text = large_font.render("Game Over!", True, COLOR_TEXT)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

            if collected_coins >= 3:
                win_time_text = font.render(f"You win! Time: {best_time:.2f} seconds", True, COLOR_TEXT)
                screen.blit(win_time_text, (SCREEN_WIDTH // 2 - win_time_text.get_width() // 2, SCREEN_HEIGHT // 2))
            else:
                retry_text = font.render("Press 'R' to retry", True, COLOR_TEXT)
                screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()
        clock.tick(FPS)

# Run the game
start_screen()  # Show start screen before the game starts
main()  # Start the main game loop
