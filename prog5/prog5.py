import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
STAR_COUNT = 100
STAR_SPEED = 2

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
CYAN = (0, 255, 255)
BLUE = (100, 150, 255)

class Star:
    def __init__(self):
        self.x = random.randint(0, WINDOW_WIDTH)
        self.y = random.randint(0, WINDOW_HEIGHT)
        # All stars move in the same direction (toward top-left)
        self.angle = -135 * (math.pi / 180)  # 135 degrees = up-left direction
        self.base_speed = random.uniform(STAR_SPEED * 0.5, STAR_SPEED * 1.5)
        self.speed = self.base_speed
        self.size = random.randint(1, 3)
        self.brightness = random.randint(150, 255)
        
    def update(self, speed_multiplier=1.0):
        # Apply speed multiplier for transitions
        current_speed = self.base_speed * speed_multiplier
        self.x += math.cos(self.angle) * current_speed
        self.y += math.sin(self.angle) * current_speed
        
        # Wrap around screen
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
            
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class AstroSlayerGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("ASTRO SLAYER")
        self.clock = pygame.time.Clock()
        # Load different fonts for title and button
        # Title font - pixelated retro gaming style
        # Create pixelated font by using a small font scaled up
        try:
            # Try to find a pixel/monospace font and scale it
            base_font = pygame.font.Font(pygame.font.match_font('courier', bold=True), 30)
            self.font_title = base_font
            self.use_pixel_scale = True
        except:
            try:
                base_font = pygame.font.SysFont('arial', 30, bold=True)
                self.font_title = base_font
                self.use_pixel_scale = True
            except:
                self.font_title = pygame.font.Font(None, 120)
                self.use_pixel_scale = False
        
        # Button font - pixelated like title
        try:
            button_base = pygame.font.Font(pygame.font.match_font('courier', bold=True), 15)
            self.font_button_small = button_base
            self.use_button_pixel = True
        except:
            try:
                button_base = pygame.font.SysFont('arial', 15, bold=True)
                self.font_button_small = button_base
                self.use_button_pixel = True
            except:
                self.font_button_small = pygame.font.Font(None, 60)
                self.use_button_pixel = False
        
        # Initialize stars
        self.stars = [Star() for _ in range(STAR_COUNT)]
        
        self.title_time = 0  # For animation
        self.transition_state = "none"  # none, speeding_up, fast, slowing_down, ready
        self.transition_timer = 0
        self.starfield_speed = 1.0
        
    def draw_starfield(self, speed_multiplier=1.0):
        # Update and draw all stars
        for star in self.stars:
            star.update(speed_multiplier)
            star.draw(self.screen)
            
    def draw_title(self):
        self.title_time += 1
        title_text = "ASTRO SLAYER"
        
        # Flashing effect - flash every 60 frames (about 1 second at 60fps)
        flash_on = (self.title_time // 60) % 2 == 0
        
        # Helper function to render and scale text for pixelation
        def render_pixelated_text(text, color):
            if self.use_pixel_scale:
                # Render small and scale up for pixelation
                small_text = self.font_title.render(text, True, color)
                # Scale up by 5x for more pixelated retro effect
                pixelated = pygame.transform.scale(small_text, 
                                                   (small_text.get_width() * 5, 
                                                    small_text.get_height() * 5))
                # Apply smooth=False for true blocky pixels
                return pixelated
            else:
                return self.font_title.render(text, True, color)
        
        # Create text with retro gaming outline effect
        if flash_on:
            # Bright flash effect with glow
            for i in range(10):
                offset = 1 + i
                # Red glow
                shadow = render_pixelated_text(title_text, 
                                               (255, 100 // (i+1), 
                                                0))
                shadow_rect = shadow.get_rect(center=(WINDOW_WIDTH // 2 + offset, 
                                                       250 + offset))
                self.screen.blit(shadow, shadow_rect)
                
                # Cyan glow
                cyan_glow = render_pixelated_text(title_text, 
                                                  (0, 255 // (i+1), 
                                                   255 // (i+1)))
                cyan_rect = cyan_glow.get_rect(center=(WINDOW_WIDTH // 2 - offset, 
                                                        250 - offset))
                self.screen.blit(cyan_glow, cyan_rect)
            
            # Main title text - bright white
            main_title = render_pixelated_text(title_text, (255, 255, 255))
        else:
            # Normal state - white text with black outline for retro effect
            # Draw black outline in all directions
            for dx in range(-4, 5, 2):
                for dy in range(-4, 5, 2):
                    if dx != 0 or dy != 0:
                        outline = render_pixelated_text(title_text, (0, 0, 0))
                        outline_rect = outline.get_rect(center=(WINDOW_WIDTH // 2 + dx, 
                                                                 250 + dy))
                        self.screen.blit(outline, outline_rect)
            
            # Main title text - white
            main_title = render_pixelated_text(title_text, (255, 255, 255))
        
        main_rect = main_title.get_rect(center=(WINDOW_WIDTH // 2, 250))
        self.screen.blit(main_title, main_rect)
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Draw starfield with speed multiplier
        self.draw_starfield(self.starfield_speed)
        
        # Draw title only if not in transition
        if self.transition_state == "none":
            self.draw_title()
        
        # Calculate flash state for button pulsing
        flash_on = (self.title_time // 60) % 2 == 0
        
        # Draw Play button only if not in transition
        if self.transition_state == "none":
            mouse_pos = pygame.mouse.get_pos()
            play_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 + 150, 300, 80)
            
            # Button pulsing effect synchronized with title flash
            if flash_on:
                # Bright pulsing state - match title flash colors
                if play_rect.collidepoint(mouse_pos):
                    border_color = (255, 255, 255)  # Bright white when pulsing and hovered
                    text_color = WHITE
                else:
                    border_color = (255, 200, 0)  # Orange/gold to match title glow
                    text_color = WHITE
            else:
                # Normal state - match title default colors
                if play_rect.collidepoint(mouse_pos):
                    border_color = WHITE
                    text_color = WHITE
                else:
                    border_color = WHITE  # White like title default
                    text_color = WHITE
            
            # Draw button with pulsing effect - TRANSPARENT CENTER, JUST RING
            if flash_on:
                # Draw glow effect when flashing (outer rings) - match title colors
                for i in range(8):
                    glow_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150 - i, WINDOW_HEIGHT // 2 + 150 - i, 
                                            300 + i*2, 80 + i*2)
                    # Red glow
                    red_glow = pygame.Rect(WINDOW_WIDTH // 2 - 150 - i, WINDOW_HEIGHT // 2 + 150 - i, 
                                            300 + i*2, 80 + i*2)
                    red_color = (255 // (i+2), 100 // (i+2), 0)
                    pygame.draw.rect(self.screen, red_color, red_glow, width=2, border_radius=15)
                    
                    # Cyan glow
                    cyan_glow = pygame.Rect(WINDOW_WIDTH // 2 - 150 + i, WINDOW_HEIGHT // 2 + 150 + i, 
                                            300 + i*2, 80 + i*2)
                    cyan_color = (0, 255 // (i+2), 255 // (i+2))
                    pygame.draw.rect(self.screen, cyan_color, cyan_glow, width=2, border_radius=15)
            
            # Draw only the border ring (transparent center)
            # Add black outline when not flashing (like title)
            if not flash_on:
                # Draw black outline in all directions for retro effect
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        if dx != 0 or dy != 0:
                            outline_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150 + dx, WINDOW_HEIGHT // 2 + 150 + dy, 
                                                       300, 80)
                            pygame.draw.rect(self.screen, (0, 0, 0), outline_rect, width=8, border_radius=15)
            
            pygame.draw.rect(self.screen, border_color, play_rect, width=8, border_radius=15)
            
            # Render pixelated button text (1980s style)
            if self.use_button_pixel:
                small_text = self.font_button_small.render("PLAY", True, text_color)
                # Scale up by 5x for blocky pixelated effect
                pixelated_text = pygame.transform.scale(small_text, 
                                                         (small_text.get_width() * 5, 
                                                          small_text.get_height() * 5))
                play_text = pixelated_text
            else:
                play_text = self.font_button_small.render("PLAY", True, text_color)
            
            play_text_rect = play_text.get_rect(center=play_rect.center)
            self.screen.blit(play_text, play_text_rect)
            
            return play_rect
        else:
            return None
        
    def run(self):
        running = True
        state = "menu"
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and self.transition_state == "none":
                    play_rect = self.draw_menu()
                    if play_rect and play_rect.collidepoint(event.pos):
                        # Start transition
                        self.transition_state = "speeding_up"
                        self.transition_timer = 0
                        self.starfield_speed = 1.0
                        print("Transition Started!")
                        
            # Handle transition states
            if self.transition_state == "speeding_up":
                # Speed up for 30 frames (0.5 seconds)
                self.transition_timer += 1
                if self.transition_timer < 30:
                    self.starfield_speed = 1.0 + (self.transition_timer / 30) * 9.0  # Speed up to 10x
                else:
                    self.transition_state = "fast"
                    self.transition_timer = 0
                    
            elif self.transition_state == "fast":
                # Stay fast for 240 frames (4 seconds)
                self.transition_timer += 1
                self.starfield_speed = 10.0
                if self.transition_timer >= 240:
                    self.transition_state = "slowing_down"
                    self.transition_timer = 0
                    
            elif self.transition_state == "slowing_down":
                # Slow down over 60 frames (1 second)
                self.transition_timer += 1
                if self.transition_timer < 60:
                    progress = self.transition_timer / 60
                    self.starfield_speed = 10.0 - (progress * 9.0)  # Slow from 10x to 1x
                else:
                    self.transition_state = "ready"
                    self.starfield_speed = 1.0
                    print("Ready for game logic!")
                    # Here you would add the actual game logic
                        
            # Draw based on current state
            if state == "menu":
                self.draw_menu()
            else:
                # Drawing game screen
                self.screen.fill(BLACK)
                self.draw_starfield()
                
                game_text = self.font_medium.render("Game In Progress...", True, WHITE)
                game_rect = game_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
                self.screen.blit(game_text, game_rect)
            
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = AstroSlayerGame()
    game.run()
