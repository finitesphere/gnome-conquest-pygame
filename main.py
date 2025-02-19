import pygame
import math
import random

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
HEX_RADIUS = 50
PLAYER_SCALE = 0.8
PLAYER_RADIUS = HEX_RADIUS * PLAYER_SCALE
FPS = 60

COLOR_BG = (30, 30, 30)
COLOR_HEX = (100, 100, 200)
COLOR_PLAYER = (0, 0, 255)
COLOR_COIN = (255, 215, 0)
COLOR_ENEMY = (255, 0, 0)
COLOR_TEXT = (255, 255, 255)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hexagon Grid Game")
clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 48)

def hex_to_pixel(q, r, size):
    x = size * 3/2 * q + SCREEN_WIDTH // 2
    y = size * math.sqrt(3) * (r + q / 2) + SCREEN_HEIGHT // 2
    return x, y

def draw_hexagon(surface, color, center, size, width=0):
    points = [(center[0] + size * math.cos(math.radians(60 * i)),
               center[1] + size * math.sin(math.radians(60 * i))) for i in range(6)]
    pygame.draw.polygon(surface, color, points, width)

class HexGrid:
    def __init__(self, radius):
        self.radius = radius
        self.hexes = {}
        self.generate_grid()

    def generate_grid(self):
        margin = HEX_RADIUS * 2
        for q in range(-self.radius, self.radius + 1):
            for r in range(-self.radius, self.radius + 1):
                if -q - r in range(-self.radius, self.radius + 1):
                    center = hex_to_pixel(q, r, HEX_RADIUS)
                    if margin < center[0] < SCREEN_WIDTH - margin and margin < center[1] < SCREEN_HEIGHT - margin:
                        self.hexes[(q, r)] = None

    def draw(self, surface):
        for (q, r) in self.hexes.keys():
            draw_hexagon(surface, COLOR_HEX, hex_to_pixel(q, r, HEX_RADIUS), HEX_RADIUS, 2)

class Player:
    def __init__(self, q, r):
        self.q, self.r = q, r

    def move(self, dq, dr):
        if (self.q + dq, self.r + dr) in grid.hexes:
            self.q += dq
            self.r += dr

    def draw(self, surface):
        draw_hexagon(surface, COLOR_PLAYER, hex_to_pixel(self.q, self.r, HEX_RADIUS), PLAYER_RADIUS)

class Coin:
    def __init__(self, q, r):
        self.q, self.r = q, r

    def draw(self, surface):
        draw_hexagon(surface, COLOR_COIN, hex_to_pixel(self.q, self.r, HEX_RADIUS), HEX_RADIUS // 2)

class Enemy:
    def __init__(self, q, r):
        self.q, self.r = q, r

    def draw(self, surface):
        draw_hexagon(surface, COLOR_ENEMY, hex_to_pixel(self.q, self.r, HEX_RADIUS), HEX_RADIUS, 2)

def start_screen():
    start_text = large_font.render("Gnome Conquest: Pygame Edition", True, COLOR_TEXT)
    start_button_text = font.render("Start", True, COLOR_TEXT)
    quit_button_text = font.render("Quit", True, COLOR_TEXT)

    while True:
        screen.fill(COLOR_BG)
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
                    return
                elif quit_button_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60)).collidepoint(mouse_pos):
                    pygame.quit()
                    exit()

def main():
    global grid
    grid = HexGrid(5)
    player = Player(0, 0)
    coins, enemies = [], []

    for _ in range(3):
        while True:
            q, r = random.randint(-grid.radius, grid.radius), random.randint(-grid.radius, grid.radius)
            if (q, r) in grid.hexes and (q, r) != (0, 0):
                enemies.append(Enemy(q, r))
                break

    for _ in range(3):
        while True:
            q, r = random.randint(-grid.radius, grid.radius), random.randint(-grid.radius, grid.radius)
            if (q, r) in grid.hexes and (q, r) != (0, 0) and (q, r) not in [(e.q, e.r) for e in enemies]:
                coins.append(Coin(q, r))
                break

    collected_coins = 0
    start_time = pygame.time.get_ticks()
    best_time, game_over = None, False

    while True:
        screen.fill(COLOR_BG)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            elif event.type == pygame.KEYDOWN:
                if not game_over:
                    moves = {pygame.K_w: (0, -1), pygame.K_e: (1, -1), pygame.K_a: (-1, 0),
                             pygame.K_d: (1, 0), pygame.K_s: (0, 1), pygame.K_z: (-1, 1), pygame.K_x: (1, 1)}
                    if event.key in moves:
                        player.move(*moves[event.key])
                elif event.key == pygame.K_r:
                    return main()

        if not game_over:
            for coin in coins[:]:
                if (player.q, player.r) == (coin.q, coin.r):
                    coins.remove(coin)
                    collected_coins += 1

            if any((player.q, player.r) == (e.q, e.r) for e in enemies):
                game_over = True
                best_time = None

            if collected_coins >= 3:
                game_over = True
                elapsed_time = (pygame.time.get_ticks() - start_time) / 1000
                best_time = min(best_time, elapsed_time) if best_time else elapsed_time

        grid.draw(screen)
        player.draw(screen)
        for coin in coins:
            coin.draw(screen)
        for enemy in enemies:
            enemy.draw(screen)

        coin_text = font.render(f"Coins: {collected_coins}/3", True, COLOR_TEXT)
        screen.blit(coin_text, (SCREEN_WIDTH - coin_text.get_width() - 20, SCREEN_HEIGHT - coin_text.get_height() - 20))

        if game_over:
            game_over_text = large_font.render("Game Over!", True, COLOR_TEXT)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))

            if collected_coins >= 3:
                win_text = font.render(f"You win! Time: {best_time:.2f} seconds", True, COLOR_TEXT)
                screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
            else:
                retry_text = font.render("Press 'R' to retry", True, COLOR_TEXT)
                screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()
        clock.tick(FPS)

start_screen()
main()
