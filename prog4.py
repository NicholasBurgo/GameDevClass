import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
PADDLE_WIDTH = 30
PADDLE_HEIGHT = 150
BALL_SIZE = 20
BULLET_SIZE = 8
PADDLE_SPEED = 7
BALL_SPEED = 6
BULLET_SPEED = 15
BULLET_ACCUMULATION_RATE = 1.0  # bullets per second
PADDLE_REGEN_TIME = 10.0  # seconds

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 100, 100)
BLUE = (100, 150, 255)
YELLOW = (255, 255, 100)
GREEN = (100, 255, 100)
PURPLE = (200, 100, 255)
ORANGE = (255, 150, 50)


class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction  # 1 for right, -1 for left
        self.speed = BULLET_SPEED
        self.active = True

    def update(self):
        self.x += self.direction * self.speed

    def draw(self, screen):
        if self.active:
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), BULLET_SIZE)


class Paddle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.color = color
        self.speed = PADDLE_SPEED
        self.bullets = 0
        self.max_bullets = 0
        self.last_bullet_time = 0
        self.last_hit_time = 0
        self.original_height = PADDLE_HEIGHT

    def update(self, current_time):
        # Accumulate bullets over time
        if current_time - self.last_bullet_time >= 1.0:
            self.bullets += 1
            self.last_bullet_time = current_time

        # Regenerate paddle size if not hit for 10 seconds
        if current_time - self.last_hit_time >= PADDLE_REGEN_TIME:
            if self.height < self.original_height:
                self.height = min(self.original_height, self.height + 2)

    def move_up(self):
        # Calculate speed based on paddle size - smaller paddles move faster
        speed_multiplier = self.original_height / self.height
        current_speed = self.speed * speed_multiplier
        self.y = max(0, self.y - current_speed)

    def move_down(self):
        # Calculate speed based on paddle size - smaller paddles move faster
        speed_multiplier = self.original_height / self.height
        current_speed = self.speed * speed_multiplier
        self.y = min(WINDOW_HEIGHT - self.height, self.y + current_speed)

    def shoot(self, bullets_list):
        if self.bullets > 0:
            bullet_x = self.x + self.width if self.x < WINDOW_WIDTH // 2 else self.x
            bullet_y = self.y + self.height // 2
            direction = 1 if self.x < WINDOW_WIDTH // 2 else -1
            bullets_list.append(Bullet(bullet_x, bullet_y, direction))
            self.bullets -= 1

    def get_hit(self):
        self.height = max(20, self.height - 20)  # Shrink by 20 pixels, minimum 20
        self.last_hit_time = pygame.time.get_ticks() / 1000.0

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        # Draw bullet count
        font = pygame.font.Font(None, 30)
        bullet_text = font.render(f"Bullets: {self.bullets}", True, WHITE)
        if self.x < WINDOW_WIDTH // 2:
            screen.blit(bullet_text, (10, 10))
        else:
            screen.blit(bullet_text, (WINDOW_WIDTH - 150, 10))


class Ball:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.vx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vy = random.uniform(-BALL_SPEED, BALL_SPEED)
        self.size = BALL_SIZE
        self.color = WHITE

    def update(self):
        self.x += self.vx
        self.y += self.vy

        # Bounce off top and bottom walls
        if self.y <= 0 or self.y >= WINDOW_HEIGHT - self.size:
            self.vy = -self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def reset(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2
        self.vx = random.choice([-BALL_SPEED, BALL_SPEED])
        self.vy = random.uniform(-BALL_SPEED, BALL_SPEED)


class PongShooterGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("PONG SHOOTER - The Ultimate Battle!")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, 80)
        self.font_medium = pygame.font.Font(None, 50)
        self.font_small = pygame.font.Font(None, 35)
        self.reset_game()
        self.state = "menu"  # menu, playing, game_over
        self.mode = None

    def reset_game(self):
        self.left_paddle = Paddle(50, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, RED)
        self.right_paddle = Paddle(WINDOW_WIDTH - 80, WINDOW_HEIGHT // 2 - PADDLE_HEIGHT // 2, BLUE)
        self.ball = Ball()
        self.bullets = []
        self.left_score = 0
        self.right_score = 0
        self.start_time = pygame.time.get_ticks() / 1000.0

    def draw_menu(self):
        self.screen.fill(BLACK)

        # Title
        title = self.font_large.render("PONG SHOOTER!", True, YELLOW)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(title, title_rect)

        # Buttons
        mouse_pos = pygame.mouse.get_pos()

        # Player vs Player button
        pvp_rect = pygame.Rect(400, 400, 300, 80)
        pvp_color = PURPLE if pvp_rect.collidepoint(mouse_pos) else BLUE
        pygame.draw.rect(self.screen, pvp_color, pvp_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, pvp_rect, 3, border_radius=10)
        pvp_text = self.font_medium.render("Player vs Player", True, WHITE)
        pvp_text_rect = pvp_text.get_rect(center=pvp_rect.center)
        self.screen.blit(pvp_text, pvp_text_rect)

        # Player vs Computer button
        pvc_rect = pygame.Rect(700, 400, 300, 80)
        pvc_color = PURPLE if pvc_rect.collidepoint(mouse_pos) else RED
        pygame.draw.rect(self.screen, pvc_color, pvc_rect, border_radius=10)
        pygame.draw.rect(self.screen, WHITE, pvc_rect, 3, border_radius=10)
        pvc_text = self.font_medium.render("Player vs Computer", True, WHITE)
        pvc_text_rect = pvc_text.get_rect(center=pvc_rect.center)
        self.screen.blit(pvc_text, pvc_text_rect)

        return pvp_rect, pvc_rect

    def draw_game(self):
        self.screen.fill(BLACK)

        # Draw center line
        for i in range(0, WINDOW_HEIGHT, 20):
            pygame.draw.rect(self.screen, WHITE, (WINDOW_WIDTH // 2 - 2, i, 4, 10))

        # Draw paddles
        self.left_paddle.draw(self.screen)
        self.right_paddle.draw(self.screen)

        # Draw ball
        self.ball.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw scores
        left_score_text = self.font_large.render(str(self.left_score), True, RED)
        right_score_text = self.font_large.render(str(self.right_score), True, BLUE)
        self.screen.blit(left_score_text, (WINDOW_WIDTH // 4, 50))
        self.screen.blit(right_score_text, (3 * WINDOW_WIDTH // 4, 50))

        # Draw game over screen
        if self.state == "game_over":
            winner_text = "LEFT PLAYER WINS!" if self.left_score > self.right_score else "RIGHT PLAYER WINS!"
            winner_color = RED if self.left_score > self.right_score else BLUE
            game_over_text = self.font_large.render(winner_text, True, winner_color)
            game_over_rect = game_over_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(game_over_text, game_over_rect)

            restart_text = self.font_medium.render("Press R to restart or ESC for menu", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

    def handle_collisions(self):
        # Ball-paddle collisions
        ball_rect = pygame.Rect(self.ball.x - self.ball.size, self.ball.y - self.ball.size,
                                self.ball.size * 2, self.ball.size * 2)

        # Left paddle
        left_paddle_rect = pygame.Rect(self.left_paddle.x, self.left_paddle.y,
                                       self.left_paddle.width, self.left_paddle.height)
        if ball_rect.colliderect(left_paddle_rect) and self.ball.vx < 0:
            self.ball.vx = -self.ball.vx
            # Add some spin based on where ball hits paddle
            hit_pos = (self.ball.y - self.left_paddle.y) / self.left_paddle.height
            self.ball.vy = (hit_pos - 0.5) * 8

        # Right paddle
        right_paddle_rect = pygame.Rect(self.right_paddle.x, self.right_paddle.y,
                                        self.right_paddle.width, self.right_paddle.height)
        if ball_rect.colliderect(right_paddle_rect) and self.ball.vx > 0:
            self.ball.vx = -self.ball.vx
            # Add some spin based on where ball hits paddle
            hit_pos = (self.ball.y - self.right_paddle.y) / self.right_paddle.height
            self.ball.vy = (hit_pos - 0.5) * 8

        # Ball-wall collisions (scoring)
        if self.ball.x < 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.x > WINDOW_WIDTH:
            self.left_score += 1
            self.ball.reset()

        # Bullet-ball collisions
        for bullet in self.bullets[:]:
            if bullet.active:
                bullet_rect = pygame.Rect(bullet.x - BULLET_SIZE, bullet.y - BULLET_SIZE,
                                          BULLET_SIZE * 2, BULLET_SIZE * 2)
                if ball_rect.colliderect(bullet_rect):
                    # Transfer momentum: bullet is 1/10 weight but 3x speed
                    momentum_transfer = 0.3  # Simplified calculation
                    self.ball.vx += bullet.direction * momentum_transfer * bullet.speed
                    self.ball.vy += random.uniform(-2, 2)  # Add some randomness
                    bullet.active = False
                    self.bullets.remove(bullet)

        # Bullet-paddle collisions
        for bullet in self.bullets[:]:
            if bullet.active:
                bullet_rect = pygame.Rect(bullet.x - BULLET_SIZE, bullet.y - BULLET_SIZE,
                                          BULLET_SIZE * 2, BULLET_SIZE * 2)
                # Left paddle
                if bullet_rect.colliderect(left_paddle_rect) and bullet.direction < 0:
                    self.left_paddle.get_hit()
                    bullet.active = False
                    self.bullets.remove(bullet)

                # Right paddle
                if bullet_rect.colliderect(right_paddle_rect) and bullet.direction > 0:
                    self.right_paddle.get_hit()
                    bullet.active = False
                    self.bullets.remove(bullet)

        # Remove inactive bullets
        self.bullets = [bullet for bullet in self.bullets if bullet.active and
                        0 <= bullet.x <= WINDOW_WIDTH]

    def computer_ai(self):
        # Simple AI for right paddle
        if self.mode == 2:  # Player vs Computer
            # Move towards ball
            ball_center = self.ball.y
            paddle_center = self.right_paddle.y + self.right_paddle.height // 2
            if ball_center < paddle_center - 20:
                self.right_paddle.move_up()
            elif ball_center > paddle_center + 20:
                self.right_paddle.move_down()

            # Shoot occasionally (not too often)
            if random.random() < 0.01 and self.right_paddle.bullets > 0:
                self.right_paddle.shoot(self.bullets)

    def update(self):
        if self.state == "playing":
            current_time = pygame.time.get_ticks() / 1000.0

            # Update paddles
            self.left_paddle.update(current_time)
            self.right_paddle.update(current_time)

            # Update ball
            self.ball.update()

            # Update bullets
            for bullet in self.bullets:
                bullet.update()

            # Handle collisions
            self.handle_collisions()

            # Computer AI
            self.computer_ai()

            # Check for game over (first to 5 points)
            if self.left_score >= 5 or self.right_score >= 5:
                self.state = "game_over"

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.state == "playing":
                            self.state = "menu"
                        elif self.state == "game_over":
                            self.state = "menu"

                    if event.key == pygame.K_r and self.state == "game_over":
                        self.reset_game()
                        self.state = "playing"

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.state == "menu":
                        pvp_rect, pvc_rect = self.draw_menu()
                        if pvp_rect.collidepoint(event.pos):
                            self.mode = 1
                            self.state = "playing"
                            self.reset_game()
                        elif pvc_rect.collidepoint(event.pos):
                            self.mode = 2
                            self.state = "playing"
                            self.reset_game()

            # Handle input
            if self.state == "playing":
                keys = pygame.key.get_pressed()

                # Left paddle (WASD)
                if keys[pygame.K_w]:
                    self.left_paddle.move_up()
                if keys[pygame.K_s]:
                    self.left_paddle.move_down()
                if keys[pygame.K_SPACE]:
                    self.left_paddle.shoot(self.bullets)

                # Right paddle (Arrow keys)
                if keys[pygame.K_UP]:
                    self.right_paddle.move_up()
                if keys[pygame.K_DOWN]:
                    self.right_paddle.move_down()
                if keys[pygame.K_RETURN]:
                    self.right_paddle.shoot(self.bullets)

            self.update()

            # Draw
            if self.state == "menu":
                self.draw_menu()
            else:
                self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = PongShooterGame()
    game.run()

