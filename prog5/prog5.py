import pygame
import random
import math
import sys
import os

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 2100
WINDOW_HEIGHT = 1350
STAR_COUNT = 150  # Balanced star count
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

class Bullet:
    def __init__(self, x, y, angle, damage=30):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = 15
        self.radius = 3
        self.active = True
        self.lifetime = 120  # Frames before bullet despawns
        self.damage = damage  # Bullet damage
        
    def update(self):
        if not self.active:
            return
            
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            
        # Wrap around screen edges
        if self.x < 0:
            self.x = WINDOW_WIDTH
        elif self.x > WINDOW_WIDTH:
            self.x = 0
        if self.y < 0:
            self.y = WINDOW_HEIGHT
        elif self.y > WINDOW_HEIGHT:
            self.y = 0
            
    def draw(self, screen):
        if self.active:
            # Draw bullet - larger and brighter if charged
            if self.damage > 30:
                # Charged shot - bigger and more vibrant
                size_multiplier = 1 + (self.damage / 150) * 4  # Max 5x size
                radius = int(self.radius * size_multiplier)
                # Bright cyan/blue for charged shots
                color_intensity = min(255, 100 + int(self.damage / 150 * 155))
                pygame.draw.circle(screen, (0, color_intensity, 255), (int(self.x), int(self.y)), radius)
                pygame.draw.circle(screen, (200, 255, 255), (int(self.x), int(self.y)), int(radius * 0.7))
                pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), int(radius * 0.4))
            else:
                # Regular shot
                pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 1)

class Beam:
    def __init__(self, x, y, angle, damage=150):
        self.start_x = x
        self.start_y = y
        self.angle = angle
        self.damage = damage
        self.active = True
        self.lifetime = 15  # Beam lasts for 15 frames (0.25 seconds at 60 FPS)
        self.length = 2000  # Beam extends 2000 pixels (covers entire screen)
        self.width = 40  # Beam width
        self.hit_targets = set()  # Track what we've already hit to avoid multiple hits
        
    def update(self):
        if not self.active:
            return
            
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            
    def get_end_point(self):
        """Get the end point of the beam"""
        end_x = self.start_x + math.cos(self.angle) * self.length
        end_y = self.start_y + math.sin(self.angle) * self.length
        return (end_x, end_y)
    
    def check_collision_point(self, point_x, point_y, radius):
        """Check if a point (with radius) collides with the beam"""
        # Calculate distance from point to beam line
        end_x, end_y = self.get_end_point()
        
        # Vector from start to end
        dx = end_x - self.start_x
        dy = end_y - self.start_y
        
        # Vector from start to point
        px = point_x - self.start_x
        py = point_y - self.start_y
        
        # Project point onto beam line
        dot = px * dx + py * dy
        length_sq = dx * dx + dy * dy
        
        if length_sq == 0:
            # Beam has zero length
            dist = math.sqrt(px * px + py * py)
            return dist < (radius + self.width / 2)
        
        t = max(0, min(1, dot / length_sq))
        closest_x = self.start_x + t * dx
        closest_y = self.start_y + t * dy
        
        # Distance from point to closest point on beam
        dist_x = point_x - closest_x
        dist_y = point_y - closest_y
        dist = math.sqrt(dist_x * dist_x + dist_y * dist_y)
        
        # Check if within beam width + target radius
        return dist < (radius + self.width / 2)
    
    def draw(self, screen):
        if not self.active:
            return
            
        end_x, end_y = self.get_end_point()
        
        # Draw beam with gradient layers - outer to inner
        # Outer glow - pale blue
        for i in range(4):
            alpha_factor = 0.3 - (i * 0.05)
            width_factor = 1.0 + (i * 0.3)
            color = (int(100 * alpha_factor), int(200 * alpha_factor), int(255 * alpha_factor))
            width = int(self.width * width_factor)
            pygame.draw.line(screen, color,
                           (int(self.start_x), int(self.start_y)),
                           (int(end_x), int(end_y)),
                           width=max(1, width))
        
        # Core beam - bright cyan/white
        core_colors = [
            ((0, 255, 255), 12),   # Bright cyan core
            ((100, 255, 255), 16),  # Light cyan
            ((200, 255, 255), 20),  # Pale cyan
            ((255, 255, 255), 24),  # White outer
        ]
        
        for color, width in core_colors:
            pygame.draw.line(screen, color,
                           (int(self.start_x), int(self.start_y)),
                           (int(end_x), int(end_y)),
                           width=width)

class Asteroid:
    def __init__(self, x=None, y=None, size=None):
        # Random size if not specified
        if size is None:
            size = random.choice(["large", "medium", "small"])
            
        self.size = size
        if size == "large":
            self.radius = 100
            self.speed = random.uniform(1, 2)
            self.value = 100
        elif size == "medium":
            self.radius = 60
            self.speed = random.uniform(2, 3)
            self.value = 50
        else:
            self.radius = 30
            self.speed = random.uniform(3, 4)
            self.value = 20
            
        # Random position if not specified
        if x is None or y is None:
            # Spawn on edges of screen
            side = random.choice(["top", "bottom", "left", "right"])
            if side == "top":
                self.x = random.randint(0, WINDOW_WIDTH)
                self.y = 0
            elif side == "bottom":
                self.x = random.randint(0, WINDOW_WIDTH)
                self.y = WINDOW_HEIGHT
            elif side == "left":
                self.x = 0
                self.y = random.randint(0, WINDOW_HEIGHT)
            else:
                self.x = WINDOW_WIDTH
                self.y = random.randint(0, WINDOW_HEIGHT)
        else:
            self.x = x
            self.y = y
            
        # Random velocity direction
        angle = random.uniform(0, 2 * math.pi)
        self.vel_x = math.cos(angle) * self.speed
        self.vel_y = math.sin(angle) * self.speed
        
        # Load asteroid image
        image_paths = ["prog5/Assets/Astroid.png", "Assets/Astroid.png"]
        self.base_image = None
        self.image = None
        
        for path in image_paths:
            try:
                self.base_image = pygame.image.load(path).convert_alpha()
                # Scale image based on asteroid size
                image_size = int(self.radius * 2)
                self.base_image = pygame.transform.scale(self.base_image, (image_size, image_size))
                break
            except:
                continue
        
        # Rotation for asteroids
        self.rotation_angle = 0
        self.rotation_speed = random.uniform(0.02, 0.05)
        
        # For drawing polygon shape (fallback if image not loaded)
        self.vertices = []
        self.generate_shape()
        
        self.active = True
        self.id = id(self)  # Unique ID for collision tracking
        
    def generate_shape(self):
        # Generate random irregular polygon shape
        num_vertices = 8
        self.vertices = []
        for i in range(num_vertices):
            angle = (2 * math.pi / num_vertices) * i
            # Vary radius for irregular shape
            radius_var = self.radius * random.uniform(0.7, 1.0)
            vx = self.x + math.cos(angle) * radius_var
            vy = self.y + math.sin(angle) * radius_var
            self.vertices.append((vx, vy))
    
    def update(self):
        if not self.active:
            return
            
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Wrap around screen edges
        if self.x < -self.radius:
            self.x = WINDOW_WIDTH + self.radius
        elif self.x > WINDOW_WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = WINDOW_HEIGHT + self.radius
        elif self.y > WINDOW_HEIGHT + self.radius:
            self.y = -self.radius
            
        # Update rotation
        if self.base_image:
            self.rotation_angle += self.rotation_speed
            if self.rotation_angle >= 2 * math.pi:
                self.rotation_angle -= 2 * math.pi
            
        # Update vertices positions (fallback for polygon drawing)
        for i, (vx, vy) in enumerate(self.vertices):
            angle = (2 * math.pi / len(self.vertices)) * i
            radius_var = self.radius * random.uniform(0.7, 1.0)
            self.vertices[i] = (self.x + math.cos(angle) * radius_var, 
                               self.y + math.sin(angle) * radius_var)
    
    def collide_with(self, other):
        """Check collision with another asteroid or bullet"""
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        return distance < (self.radius + other.radius)
    
    def bounce(self, other):
        """Bounce off another asteroid"""
        if not isinstance(other, Asteroid):
            return
            
        # Calculate collision normal
        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance == 0:
            return
            
        # Normalize
        nx = dx / distance
        ny = dy / distance
        
        # Separate asteroids to prevent overlap
        overlap = (self.radius + other.radius) - distance
        if overlap > 0:
            self.x += nx * overlap * 0.5
            self.y += ny * overlap * 0.5
            other.x -= nx * overlap * 0.5
            other.y -= ny * overlap * 0.5
        
        # Calculate relative velocity
        dvx = self.vel_x - other.vel_x
        dvy = self.vel_y - other.vel_y
        
        # Calculate impulse
        impulse = 2 * (dvx * nx + dvy * ny) / 2.0  # Divide by 2 for average mass
        
        # Apply impulse
        self.vel_x -= impulse * nx
        self.vel_y -= impulse * ny
        other.vel_x += impulse * nx
        other.vel_y += impulse * ny
    
    def draw(self, screen):
        if not self.active:
            return
        
        # Draw image if loaded
        if self.base_image:
            # Rotate the image
            rotated_image = pygame.transform.rotate(self.base_image, math.degrees(-self.rotation_angle))
            
            # Get the rect and center it on the asteroid position
            rect = rotated_image.get_rect()
            screen.blit(rotated_image, (int(self.x - rect.width // 2), int(self.y - rect.height // 2)))
        else:
            # Fallback: Draw irregular polygon if image not loaded
            pygame.draw.polygon(screen, (128, 128, 128), self.vertices)
            pygame.draw.polygon(screen, WHITE, self.vertices, width=2)
            
            # Draw center dot
            pygame.draw.circle(screen, (200, 200, 200), (int(self.x), int(self.y)), 3)

class Player:
    def __init__(self):
        self.x = WINDOW_WIDTH // 2
        self.y = WINDOW_HEIGHT // 2  # Center position
        self.target_y = int(WINDOW_HEIGHT * 0.40)
        self.radius = 30
        self.color = (100, 200, 255)  # Cyan-blue color
        self.active = False
        self.phase = "moving"  # moving, stopping, centered
        self.stop_timer = 0
        self.base_speed = 1.5
        self.stop_start_x = WINDOW_WIDTH // 2
        self.stop_start_y = WINDOW_HEIGHT // 2
        
        # Spaceship physics
        self.vel_x = 0
        self.vel_y = 0
        self.angle = -math.pi / 2  # Start pointing up
        self.angular_velocity = 0
        self.max_speed = 8
        self.acceleration = 0.15
        self.friction = 0.98
        self.rotation_speed = 0.08
        
        # Shooting
        self.bullets = []
        self.beams = []  # Beams for fully charged shots
        self.shoot_cooldown = 0
        self.max_shoot_cooldown = 10
        
        # Charged shot system
        self.is_charging = False
        self.charge_time = 0.0  # Time spent charging in seconds
        self.max_charge_time = 5.0  # Max charge time (5 seconds)
        self.charged_damage = 30  # Base damage
        self.max_charged_damage = 150  # Max damage
        self.space_pressed_last_frame = False  # Track space key state
        
        # Shooting cooldown system
        self.shoot_cooldown_timer = 0  # Cooldown timer in frames
        self.shoot_cooldown_duration = 30  # 0.5 second cooldown at 60 FPS
        
        # Health system - 3 hearts
        self.max_hearts = 3
        self.hearts = 3
        self.invulnerable = False
        self.invulnerability_timer = 0
        self.invulnerability_duration = 60  # 1 second at 60 FPS
        
        # Heart regeneration system
        self.heart_regen_timer = 0.0  # Timer in seconds
        self.heart_regen_time = 25.0  # Time needed to regenerate 1 heart (25 seconds)
        
        # Teleport boost system
        self.boost_distance = 200.0
        self.max_teleport_charges = 2
        self.teleport_charges = [180, 180]  # Individual cooldown timers (180 = fully charged, 0 = empty)
        self.teleport_cooldown_frames = 180  # Cooldown duration
        self.shift_pressed_last_frame = False
        
        # Load sounds
        self.warp_sound = None
        warp_paths = ["prog5/Assets/Sounds/warp.wav", "Assets/Sounds/warp.wav"]
        for path in warp_paths:
            try:
                self.warp_sound = pygame.mixer.Sound(path)
                break
            except:
                continue
                
        self.laser_sound = None
        laser_paths = ["prog5/Assets/Sounds/laserShoot.wav", "Assets/Sounds/laserShoot.wav"]
        for path in laser_paths:
            try:
                self.laser_sound = pygame.mixer.Sound(path)
                break
            except:
                continue
        
    def start(self):
        # Start from off screen in the same direction stars come from (bottom-right)
        self.x = WINDOW_WIDTH + 100  # Start from right side off-screen
        self.y = WINDOW_HEIGHT + 100  # Start from bottom off-screen
        self.active = True
        self.phase = "moving"
        self.stop_timer = 0
        
    def update(self, speed_multiplier=1.0, transition_state="none"):
        if not self.active:
            return
            
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2  # Center of screen
        
        # Start stopping when stars begin slowing down
        if self.phase == "moving" and transition_state == "slowing_down":
            self.phase = "stopping"
            self.stop_timer = 0
        
        if self.phase == "moving":
            # Move straight toward center
            # Use consistent speed, less affected by speed_multiplier to avoid weird movement
            current_speed = self.base_speed * (1.0 + (speed_multiplier - 1.0) * 0.2)
            
            # Calculate angle directly toward center
            dx = center_x - self.x
            dy = center_y - self.y
            dist_to_center = math.sqrt(dx**2 + dy**2)
            
            # Move directly toward center
            if dist_to_center > 0:
                angle = math.atan2(dy, dx)
                self.x += math.cos(angle) * current_speed
                self.y += math.sin(angle) * current_speed
                
        elif self.phase == "stopping":
            # Gradually slow down and center
            self.stop_timer += 1
            
            # Save the starting position when first entering stopping phase
            if self.stop_timer == 1:
                self.stop_start_x = self.x
                self.stop_start_y = self.y
            
            if self.stop_timer < 60:  # Over 1 second
                # Ease into center (smooth interpolation)
                progress = self.stop_timer / 60
                # Ease-out interpolation for smooth deceleration
                ease_progress = 1 - (1 - progress) ** 3
                self.x = self.stop_start_x * (1 - ease_progress) + center_x * ease_progress
                self.y = self.stop_start_y * (1 - ease_progress) + center_y * ease_progress
            else:
                # Fully centered
                self.x = center_x
                self.y = center_y
                self.phase = "centered"
        
        elif self.phase == "centered":
            # Stay locked at center position (unless player is controlling)
            # This will be handled by handle_movement method
            pass
                
    def handle_movement(self, keys, game_over=False):
        """Handle spaceship movement with WASD keys and space for shooting"""
        if not self.active or self.phase != "centered" or game_over:
            return
        
        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerability_timer -= 1
            if self.invulnerability_timer <= 0:
                self.invulnerable = False
        
        # Update shooting cooldown timer
        if self.shoot_cooldown_timer > 0:
            self.shoot_cooldown_timer -= 1
        
        # Update heart regeneration timer
        # Only regenerate if not at max hearts
        if self.hearts < self.max_hearts:
            # Assume 60 FPS - add 1/60 seconds per frame
            self.heart_regen_timer += 1.0 / 60.0
            
            # Check if enough time has passed to regenerate a heart
            if self.heart_regen_timer >= self.heart_regen_time:
                self.hearts += 1
                self.heart_regen_timer = 0.0  # Reset timer
        else:
            # At max hearts, reset timer
            self.heart_regen_timer = 0.0
        
        # A/D keys change heading
        if keys[pygame.K_a]:
            self.angle -= self.rotation_speed
        if keys[pygame.K_d]:
            self.angle += self.rotation_speed
        
        # W/S keys accelerate/decelerate
        if keys[pygame.K_w]:
            # Accelerate in the direction we're facing
            self.vel_x += math.cos(self.angle) * self.acceleration
            self.vel_y += math.sin(self.angle) * self.acceleration
        elif keys[pygame.K_s]:
            # Decelerate (reverse thrust)
            self.vel_x -= math.cos(self.angle) * self.acceleration * 0.5
            self.vel_y -= math.sin(self.angle) * self.acceleration * 0.5
        
        # Apply friction
        self.vel_x *= self.friction
        self.vel_y *= self.friction
        
        # Limit max speed
        speed = math.sqrt(self.vel_x**2 + self.vel_y**2)
        if speed > self.max_speed:
            self.vel_x = (self.vel_x / speed) * self.max_speed
            self.vel_y = (self.vel_y / speed) * self.max_speed
        
        # Update position
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Wrap around screen edges
        if self.x < -self.radius:
            self.x = WINDOW_WIDTH + self.radius
        elif self.x > WINDOW_WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = WINDOW_HEIGHT + self.radius
        elif self.y > WINDOW_HEIGHT + self.radius:
            self.y = -self.radius
        
        # Handle charged shooting (space key)
        space_currently_pressed = keys[pygame.K_SPACE]
        
        if space_currently_pressed:
            if not self.is_charging:
                # Start charging
                self.is_charging = True
                self.charge_time = 0.0
            
            # Increment charge time
            self.charge_time += 1/60.0  # 60 FPS
            if self.charge_time > self.max_charge_time:
                self.charge_time = self.max_charge_time
        else:
            # Space released - fire if we were charging and space was pressed last frame
            if self.is_charging and self.space_pressed_last_frame:
                # Check if cooldown has expired
                if self.shoot_cooldown_timer <= 0:
                    # Calculate damage based on charge time
                    charge_progress = min(self.charge_time / self.max_charge_time, 1.0)
                    damage = int(self.charged_damage + (self.max_charged_damage - self.charged_damage) * charge_progress)
                    
                    # Check if fully charged (95% or more charge = beam)
                    is_fully_charged = charge_progress >= 0.95
                    
                    if is_fully_charged:
                        # Create beam at ship's nose
                        beam_x = self.x + math.cos(self.angle) * (self.radius + 5)
                        beam_y = self.y + math.sin(self.angle) * (self.radius + 5)
                        new_beam = Beam(beam_x, beam_y, self.angle, damage)
                        self.beams.append(new_beam)
                        
                        # Apply recoil/knockback to player - push backwards
                        recoil_force = 8.0  # Strong recoil for fully charged beam
                        self.vel_x -= math.cos(self.angle) * recoil_force
                        self.vel_y -= math.sin(self.angle) * recoil_force
                    else:
                        # Create bullet at ship's nose
                        bullet_x = self.x + math.cos(self.angle) * (self.radius + 5)
                        bullet_y = self.y + math.sin(self.angle) * (self.radius + 5)
                        new_bullet = Bullet(bullet_x, bullet_y, self.angle, damage)
                        self.bullets.append(new_bullet)
                    
                    # Start cooldown timer
                    self.shoot_cooldown_timer = self.shoot_cooldown_duration
                    
                    # Play laser sound if available
                    if self.laser_sound:
                        self.laser_sound.play()
            
            # Reset charging
            self.is_charging = False
            self.charge_time = 0.0
        
        # Update space state for next frame
        self.space_pressed_last_frame = space_currently_pressed
        
        # Handle teleport boost (shift key)
        # Update individual charge timers (recharge each charge independently)
        for i in range(len(self.teleport_charges)):
            if self.teleport_charges[i] < self.teleport_cooldown_frames:
                self.teleport_charges[i] += 1
        
        # Check if shift is currently pressed
        shift_currently_pressed = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # Handle shift key teleport boost - only when first pressed and charges available
        if shift_currently_pressed and not self.shift_pressed_last_frame:
            # Check if any charge is available (fully charged)
            available_charge_index = -1
            for i in range(len(self.teleport_charges)):
                if self.teleport_charges[i] >= self.teleport_cooldown_frames:
                    available_charge_index = i
                    break
            
            if available_charge_index >= 0:
                # Boost in the direction ship is facing
                boost_dx = math.cos(self.angle) * self.boost_distance
                boost_dy = math.sin(self.angle) * self.boost_distance
                
                # Play warp sound if available
                if self.warp_sound:
                    self.warp_sound.play()
                
                # Apply teleport boost
                self.x += boost_dx
                self.y += boost_dy
                
                # Reset the used charge (start cooldown)
                self.teleport_charges[available_charge_index] = 0
        
        # Update shift state for next frame
        self.shift_pressed_last_frame = shift_currently_pressed
        
        # Update bullets
        for bullet in self.bullets:
            bullet.update()
        
        # Remove inactive bullets
        self.bullets = [b for b in self.bullets if b.active]
        
        # Update beams
        for beam in self.beams:
            beam.update()
        
        # Remove inactive beams
        self.beams = [b for b in self.beams if b.active]
    
    def take_damage(self):
        """Take damage and become invulnerable briefly"""
        if not self.invulnerable:
            self.hearts -= 1
            self.invulnerable = True
            self.invulnerability_timer = self.invulnerability_duration
            # Reset heart regeneration timer when taking damage
            self.heart_regen_timer = 0.0
            return True
        return False
    
    def is_dead(self):
        """Check if player is dead"""
        return self.hearts <= 0
            
    def draw_hearts(self, screen):
        """Draw hearts in top left corner"""
        heart_size = 50
        spacing = 10
        start_x = 20
        start_y = 20
        
        for i in range(self.max_hearts):
            x = start_x + i * (heart_size + spacing)
            y = start_y
            
            # Calculate fill progress
            if i < self.hearts:
                fill_progress = 1.0
            elif i == self.hearts and self.hearts < self.max_hearts:
                fill_progress = self.heart_regen_timer / self.heart_regen_time
            else:
                fill_progress = 0.0
            
            # Always draw empty heart outline first (like teleport charges)
            outline_color = (100, 100, 100)
            pygame.draw.circle(screen, outline_color, (x, y + 10), 10, width=2)
            pygame.draw.circle(screen, outline_color, (x + 20, y + 10), 10, width=2)
            outline_points = [(x, y + 15), (x + 10, y + 35), (x + 20, y + 15)]
            pygame.draw.polygon(screen, outline_color, outline_points, width=2)
            
            # Draw filled portion based on progress
            if fill_progress > 0:
                # Calculate how much to shrink the filled heart based on progress
                # When progress is 0, fill_radius = 0 (empty)
                # When progress is 1, fill_radius = full (10)
                fill_scale = fill_progress
                
                if fill_scale >= 1.0:
                    # Fully filled
                    pygame.draw.circle(screen, (255, 0, 0), (x, y + 10), 10)
                    pygame.draw.circle(screen, (255, 0, 0), (x + 20, y + 10), 10)
                    filled_points = [(x, y + 15), (x + 10, y + 35), (x + 20, y + 15)]
                    pygame.draw.polygon(screen, (255, 0, 0), filled_points)
                else:
                    # Partially filled - draw scaled down version
                    fill_radius = int(10 * fill_scale)
                    fill_height = int(25 * fill_scale)  # Height of triangle portion
                    if fill_radius > 0:
                        # Blend color from gray to red based on progress
                        red_intensity = int(100 + fill_progress * 155)
                        blue_intensity = int(100 - fill_progress * 100)
                        green_intensity = int(100 - fill_progress * 100)
                        fill_color = (red_intensity, green_intensity, blue_intensity)
                        
                        pygame.draw.circle(screen, fill_color, (x, y + 10), fill_radius)
                        pygame.draw.circle(screen, fill_color, (x + 20, y + 10), fill_radius)
                        # Bottom triangle portion (scaled)
                        filled_points = [(x, y + 15), (x + 10, y + 15 + fill_height), (x + 20, y + 15)]
                        if fill_height > 0:
                            pygame.draw.polygon(screen, fill_color, filled_points)
    
    def draw(self, screen):
        if self.active and self.phase == "centered":
            # Flash when invulnerable
            if self.invulnerable and (self.invulnerability_timer // 10) % 2 == 0:
                return  # Skip drawing on alternating frames
            
            # Draw spaceship as triangle pointing in direction of travel
            # Calculate three points of triangle
            front_x = self.x + math.cos(self.angle) * self.radius
            front_y = self.y + math.sin(self.angle) * self.radius
            
            back_left_x = self.x + math.cos(self.angle + math.pi - 0.5) * self.radius * 0.7
            back_left_y = self.y + math.sin(self.angle + math.pi - 0.5) * self.radius * 0.7
            
            back_right_x = self.x + math.cos(self.angle + math.pi + 0.5) * self.radius * 0.7
            back_right_y = self.y + math.sin(self.angle + math.pi + 0.5) * self.radius * 0.7
            
            points = [
                (int(front_x), int(front_y)),
                (int(back_left_x), int(back_left_y)),
                (int(back_right_x), int(back_right_y))
            ]
            
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.polygon(screen, WHITE, points, width=2)
            
            # Draw charge indicator when charging - at the front of the ship where bullet fires
            if self.is_charging:
                charge_progress = min(self.charge_time / self.max_charge_time, 1.0)
                # Calculate position at ship's nose
                charge_x = self.x + math.cos(self.angle) * (self.radius + 10)
                charge_y = self.y + math.sin(self.angle) * (self.radius + 10)
                
                # Check if fully charged (ready for beam) - add pulsing effect
                is_fully_charged = charge_progress >= 0.95
                
                if is_fully_charged:
                    # Pulsing animation when ready for beam
                    pulse_time = pygame.time.get_ticks() / 1000.0  # Time in seconds
                    pulse = math.sin(pulse_time * 8.0) * 0.3 + 1.0  # Pulse between 0.7 and 1.3
                    base_radius = 20  # Base radius for fully charged
                    charge_radius = int(base_radius * pulse)
                    # Bright cyan when fully charged
                    r = 0
                    g = 255
                    b = 255
                else:
                    # Smaller expanding circle
                    charge_radius = int(5 + charge_progress * 15)  # 5 to 20 pixels
                    # Color changes from yellow to bright cyan as it charges
                    r = int(255 - charge_progress * 155)
                    g = int(255 - charge_progress * 55)
                    b = 255
                
                # Draw outer circle
                pygame.draw.circle(screen, (r, g, b), (int(charge_x), int(charge_y)), charge_radius, width=2)
                
                # Draw inner pulse - more intense when fully charged
                if charge_progress > 0.3:
                    if is_fully_charged:
                        # Strong pulsing inner circle when ready for beam
                        inner_pulse = math.sin(pulse_time * 10.0) * 0.4 + 1.0  # Faster pulse
                        inner_radius = int(charge_radius * 0.7 * inner_pulse)
                        # Bright white core when pulsing
                        pygame.draw.circle(screen, (255, 255, 255), (int(charge_x), int(charge_y)), inner_radius)
                        # Extra glow ring
                        pygame.draw.circle(screen, (0, 255, 255), (int(charge_x), int(charge_y)), inner_radius + 3, width=1)
                    else:
                        inner_radius = int(charge_radius * 0.6)
                        pygame.draw.circle(screen, (0, 255, 255), (int(charge_x), int(charge_y)), inner_radius, width=1)
        elif self.active:
            # Draw simple circle during transitions
            # Flash when invulnerable
            if self.invulnerable and (self.invulnerability_timer // 10) % 2 == 0:
                return  # Skip drawing on alternating frames
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius, width=2)
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
        
        # Draw beams (fully charged shots)
        for beam in self.beams:
            beam.draw(screen)
            
class Snail:
    def __init__(self):
        # Simple image loading - try a few paths
        image_paths = ["prog5/Assets/Snail.gif", "Assets/Snail.gif"]
        self.image = None
        
        for path in image_paths:
            try:
                self.image = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (150, 240))
                break
            except:
                continue
        
        # Start off screen at bottom-right
        self.x = WINDOW_WIDTH + 100
        self.y = WINDOW_HEIGHT - 90
        self.speed = 0.75
        self.angle = -135 * (math.pi / 180)  # Same direction as stars
        self.active = False
        
    def update(self, speed_multiplier=1.0):
        if self.active:
            # Move diagonally
            self.x += math.cos(self.angle) * self.speed * speed_multiplier
            self.y += math.sin(self.angle) * self.speed * speed_multiplier
            
            # Stop when off screen
            if self.x < -200 or self.y < -200:
                self.active = False
                
    def start(self):
        self.active = True
        self.x = WINDOW_WIDTH + 100
        self.y = WINDOW_HEIGHT - 90
        
    def draw(self, screen):
        if self.active and self.image:
            image_surface = self.image.copy()
            image_surface.set_alpha(180)  # Semi-transparent
            screen.blit(image_surface, (int(self.x), int(self.y)))
        elif self.active:
            # Draw simple placeholder
            pygame.draw.ellipse(screen, (255, 255, 100), 
                               (int(self.x + 15), int(self.y + 60), 90, 150))

class Laser:
    def __init__(self, is_vertical, position):
        self.warning = True
        self.warning_timer = 1.0  # Warning phase duration
        self.active_timer = 2.0  # Active phase duration
        self.vertical = is_vertical
        self.position = position  # Position along the axis
        self.shoot_sound_played = False  # Track if shoot sound has been played
        self.just_became_active = False  # Track if laser just transitioned to active
        
        if is_vertical:
            # Vertical laser
            self.x = position
            self.y = 0
            self.width = 6 if self.warning else 40  # Thinner when warning
            self.height = WINDOW_HEIGHT
            self.center_x = position
        else:
            # Horizontal laser
            self.x = 0
            self.y = position
            self.width = WINDOW_WIDTH
            self.height = 6 if self.warning else 40  # Thinner when warning
            self.center_y = position
            
        self.active = True
        
    def update(self):
        if not self.active:
            return
            
        if self.warning:
            # In warning phase
            self.warning_timer -= 1/60  # Assuming 60 FPS
            if self.warning_timer <= 0:
                self.warning = False
                # Make laser thicker when active
                if self.vertical:
                    self.width = 40
                    self.x = self.center_x - self.width // 2
                else:
                    self.height = 40
                    self.y = self.center_y - self.height // 2
                # Mark that it just became active (for sound playing)
                self.just_became_active = True
        else:
            # In active phase
            self.active_timer -= 1/60
            if self.active_timer <= 0:
                self.active = False
                
    def draw(self, screen):
        if not self.active:
            return
            
        # Orange color #fbaa1f
        ORANGE_CENTER = (251, 170, 31)
        ORANGE_WARNING = (251, 170, 31, 180)  # Add alpha value for transparency
        ORANGE_ACTIVE = (251, 170, 31, 200)   # Add alpha value for transparency
        
        if self.warning:
            # Draw warning laser with gradient
            # Create a surface with per-pixel alpha
            laser_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw gradient from black edges to orange center
            # For vertical lasers, gradient along width; for horizontal, along height
            if self.vertical:
                # Vertical laser - gradient along width
                for i in range(self.width):
                    dist_from_center = abs(i - self.width / 2) / (self.width / 2) if self.width > 0 else 0
                    if dist_from_center < 0.5:
                        factor = 1.0 - (dist_from_center * 1.5)
                        factor = max(0.3, min(1.0, factor))
                        r = int(251 * factor)
                        g = int(170 * factor)
                        b = int(31 * factor)
                        color = (r, g, b, 180)
                    else:
                        color = (0, 0, 0, 180)
                    pygame.draw.line(laser_surface, color, (i, 0), (i, self.height))
            else:
                # Horizontal laser - gradient along height
                for i in range(self.height):
                    dist_from_center = abs(i - self.height / 2) / (self.height / 2) if self.height > 0 else 0
                    if dist_from_center < 0.5:
                        factor = 1.0 - (dist_from_center * 1.5)
                        factor = max(0.3, min(1.0, factor))
                        r = int(251 * factor)
                        g = int(170 * factor)
                        b = int(31 * factor)
                        color = (r, g, b, 180)
                    else:
                        color = (0, 0, 0, 180)
                    pygame.draw.line(laser_surface, color, (0, i), (self.width, i))
            
            screen.blit(laser_surface, (self.x, self.y))
        else:
            # Draw active laser with gradient
            # Create a surface with per-pixel alpha
            laser_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            
            # Draw gradient from black edges to orange center
            # For vertical lasers, gradient along width; for horizontal, along height
            if self.vertical:
                # Vertical laser - gradient along width
                for i in range(self.width):
                    dist_from_center = abs(i - self.width / 2) / (self.width / 2) if self.width > 0 else 0
                    if dist_from_center < 0.5:
                        factor = 1.0 - (dist_from_center * 1.5)
                        factor = max(0.3, min(1.0, factor))
                        r = int(251 * factor)
                        g = int(170 * factor)
                        b = int(31 * factor)
                        color = (r, g, b, 200)
                    else:
                        color = (0, 0, 0, 200)
                    pygame.draw.line(laser_surface, color, (i, 0), (i, self.height))
            else:
                # Horizontal laser - gradient along height
                for i in range(self.height):
                    dist_from_center = abs(i - self.height / 2) / (self.height / 2) if self.height > 0 else 0
                    if dist_from_center < 0.5:
                        factor = 1.0 - (dist_from_center * 1.5)
                        factor = max(0.3, min(1.0, factor))
                        r = int(251 * factor)
                        g = int(170 * factor)
                        b = int(31 * factor)
                        color = (r, g, b, 200)
                    else:
                        color = (0, 0, 0, 200)
                    pygame.draw.line(laser_surface, color, (0, i), (self.width, i))
            
            screen.blit(laser_surface, (self.x, self.y))
            
    def check_collision(self, player):
        """Check if laser collides with player"""
        if self.warning or not self.active:
            return False
            
        # Get player bounds
        player_left = player.x - player.radius
        player_right = player.x + player.radius
        player_top = player.y - player.radius
        player_bottom = player.y + player.radius
        
        if self.vertical:
            # Check collision with vertical laser
            laser_left = self.x
            laser_right = self.x + self.width
            return not (player_right < laser_left or player_left > laser_right)
        else:
            # Check collision with horizontal laser
            laser_top = self.y
            laser_bottom = self.y + self.height
            return not (player_bottom < laser_top or player_top > laser_bottom)

class PowerBall:
    def __init__(self, start_x, start_y, target_x, target_y, side):
        """side: 'left' or 'right' - determines arc direction"""
        self.start_x = start_x
        self.start_y = start_y
        self.target_x = target_x
        self.target_y = target_y
        self.side = side
        self.x = start_x
        self.y = start_y
        
        # Arc trajectory
        self.t = 0  # Progress along arc (0 to 1)
        self.speed = 0.01  # How fast to travel the arc (slower for better gameplay)
        
        # Calculate arc height
        mid_x = (start_x + target_x) / 2
        arc_height = 200 if side == 'left' else -200  # Offset for arc
        self.arc_center_x = mid_x
        self.arc_height = arc_height
        
        self.radius = 20
        self.active = True
        self.exploded = False
        self.explosion_sound_played = False
        self.explosion_frames = 0  # For drawing explosion effect
        self.lifetime_timer = 0  # Fail-safe timer (3 seconds = 180 frames at 60fps)
        
        # Try to load powerball image
        self.image = None
        image_paths = ["prog5/Assets/PowerBall.png", "Assets/PowerBall.png"]
        for path in image_paths:
            try:
                self.image = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (40, 40))
                break
            except:
                continue
    
    def update(self):
        # Continue updating explosion animation even after powerball is inactive
        if self.exploded:
            # Still increment explosion frames for animation
            self.explosion_frames += 1
            return
        
        if not self.active:
            return
        
        # Increment fail-safe timer
        self.lifetime_timer += 1
        
        # Fail-safe: expire after 3 seconds (180 frames at 60fps)
        if self.lifetime_timer >= 180:
            self.active = False
            self.exploded = True
            return
            
        self.t += self.speed
        
        if self.t >= 1.0:
            # Reached destination - explode
            self.active = False
            self.exploded = True
            return
        
        # Calculate position along arc using quadratic Bezier
        t = self.t
        self.x = (1 - t)**2 * self.start_x + 2 * (1 - t) * t * self.arc_center_x + t**2 * self.target_x
        self.y = (1 - t)**2 * self.start_y + 2 * (1 - t) * t * (self.start_y + self.arc_height) + t**2 * self.target_y
    
    def draw(self, screen):
        if not self.active and not self.exploded:
            return
        
        # Draw explosion effect if exploded
        if self.exploded:
            if self.explosion_frames < 20:  # Show explosion for 20 frames
                # Draw expanding explosion circles
                explosion_radius = int(self.radius + self.explosion_frames * 5)
                # Outer ring
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), explosion_radius, width=2)
                # Inner circles
                for i in range(3):
                    pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), explosion_radius - i * 15)
            return
            
        if self.image:
            image_rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(self.image, image_rect)
        else:
            # Draw placeholder if image didn't load
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius, width=2)
    
    def check_collision_with_player(self, player):
        """Check if powerball hits player"""
        if not self.active or not player.active or player.invulnerable:
            return False
            
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        
        return distance < (self.radius + player.radius)
    
    def check_explosion_collision_with_player(self, player):
        """Check if player is within explosion radius"""
        if self.exploded or not player.active or player.invulnerable:
            return False
            
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        
        explosion_radius = 100  # Explosion radius
        return distance < (explosion_radius + player.radius)

class Boss:
    def __init__(self):
        # Try to load boss images
        image_paths_t = ["prog5/Assets/BossT.png", "Assets/BossT.png"]
        image_paths_m = ["prog5/Assets/BossM.png", "Assets/BossM.png"]
        self.image = None  # Talking/normal boss
        self.image_mad = None  # Charging/mad boss
        
        for path in image_paths_t:
            try:
                self.image = pygame.image.load(path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (300, 300))
                print(f"Loaded boss image from: {path}")
                break
            except:
                continue
                
        for path in image_paths_m:
            try:
                self.image_mad = pygame.image.load(path).convert_alpha()
                self.image_mad = pygame.transform.scale(self.image_mad, (300, 300))
                print(f"Loaded boss mad image from: {path}")
                break
            except:
                continue
        
        # Position in center-top of screen
        self.x = WINDOW_WIDTH // 2
        self.y = 200
        self.active = False
        
        # Health system
        self.max_health = 1000
        self.health = 1000
        self.phase = 1  # Current phase
        
        # Laser system for boss fight
        self.lasers = []
        self.boss_fight_start_time = 0
        self.laser_spawn_interval = 2.5  # Spawn laser every 2.5 seconds
        
        # PowerBall system
        self.powerballs = []
        self.powerball_wave = 0  # Track which wave (0-2, 3 waves total)
        self.last_powerball_wave_time = 0
        self.is_launching_powerballs = False  # Track when boss shows mad sprite for powerball launch
        self.powerball_launch_timer = 0  # Timer for powerball launch mad sprite
        
        # Phase 1 AI: Laser shooting (10s) -> Wander (1s) -> Chase player (10s) -> PowerBall (10s) -> repeat
        self.phase1_mode = "shooting"  # "shooting" or "wandering" or "chasing" or "powerball"
        self.phase1_mode_timer = 0
        self.phase1_mode_start_time = 0
        self.chase_speed = 2.5
        
        # Charge attack system
        self.is_charging = False
        self.charge_timer = 0
        self.charge_duration = 30  # 0.5 second at 60 FPS
        self.charge_launch_speed = 15  # Fast speed for launching
        self.target_x = 0
        self.target_y = 0
        self.charge_direction_x = 0
        self.charge_direction_y = 0
        self.is_launching = False
        self.launch_timer = 0  # Track how long boss has been launching
        self.last_charge_time = 0  # Track when last charge started
        
        # Wandering behavior during shooting phase
        self.wander_direction = random.uniform(0, 2 * math.pi)
        self.wander_speed = 1.5
        self.wander_timer = 0
        self.wander_change_interval = random.randint(60, 120)  # Change direction every 1-2 seconds
        
        # Collision with player
        self.collision_radius = 100  # Boss hitbox radius
        self._intro_complete = False  # Track if intro dialogue is done
        
        # Load charge sounds
        self.charge_up_sound = None
        charge_up_paths = ["prog5/Assets/Sounds/BossChargeUp.wav", "Assets/Sounds/BossChargeUp.wav",
                          "prog5/Assets/Sounds/BossChargeUp.mp3", "Assets/Sounds/BossChargeUp.mp3"]
        for path in charge_up_paths:
            try:
                self.charge_up_sound = pygame.mixer.Sound(path)
                print(f"Loaded boss charge up sound from: {path}")
                break
            except:
                continue
        
        self.charge_sound = None
        charge_paths = ["prog5/Assets/Sounds/BossCharge.wav", "Assets/Sounds/BossCharge.wav",
                       "prog5/Assets/Sounds/Boss Charge.wav", "Assets/Sounds/Boss Charge.wav",
                       "prog5/Assets/Sounds/BossCharge.mp3", "Assets/Sounds/BossCharge.mp3"]
        for path in charge_paths:
            try:
                self.charge_sound = pygame.mixer.Sound(path)
                print(f"Loaded boss charge sound from: {path}")
                break
            except:
                continue
        
        # Load boss laser indicator sound for warning
        self.laser_indicator_sound = None
        laser_indicator_paths = ["prog5/Assets/Sounds/BattleLaser.wav", "Assets/Sounds/BattleLaser.wav"]
        for path in laser_indicator_paths:
            try:
                self.laser_indicator_sound = pygame.mixer.Sound(path)
                print(f"Loaded boss laser indicator sound from: {path}")
                break
            except:
                continue
        
        # Load boss laser shoot sound for when laser activates
        self.laser_shoot_sound = None
        laser_shoot_paths = ["prog5/Assets/Sounds/LaserBattleShoot.wav", "Assets/Sounds/LaserBattleShoot.wav"]
        for path in laser_shoot_paths:
            try:
                self.laser_shoot_sound = pygame.mixer.Sound(path)
                print(f"Loaded boss laser shoot sound from: {path}")
                break
            except:
                continue
        
        # Load boss projectile sound for powerballs
        self.projectile_sound = None
        projectile_paths = ["prog5/Assets/Sounds/BossLaser.wav", "Assets/Sounds/BossLaser.wav"]
        for path in projectile_paths:
            try:
                self.projectile_sound = pygame.mixer.Sound(path)
                print(f"Loaded boss projectile sound (powerballs) from: {path}")
                break
            except:
                continue
        
    def start(self):
        self.active = True
        self.x = WINDOW_WIDTH // 2
        self.y = 200
        self.lasers = []
        self.boss_fight_start_time = pygame.time.get_ticks() / 1000.0
        self.phase1_mode = "shooting"
        self.phase1_mode_start_time = pygame.time.get_ticks() / 1000.0
        self.health = self.max_health
        self._intro_complete = False  # Reset intro completion flag
        self.is_charging = False
        self.is_launching = False
        self.charge_timer = 0
        self.launch_timer = 0
        self.powerball_wave = 0
        self.last_powerball_wave_time = 0
        self.last_charge_time = -10  # Start with negative so first charge can happen quickly
        self.is_launching_powerballs = False  # Reset powerball launch state
        self.powerball_launch_timer = 0  # Reset powerball launch timer
        
    def spawn_laser(self):
        """Spawn a random laser"""
        is_vertical = random.random() < 0.5  # 50% chance vertical
        if is_vertical:
            position = random.randint(100, WINDOW_WIDTH - 100)  # Random x position
        else:
            position = random.randint(200, WINDOW_HEIGHT - 100)  # Random y position
        
        # Play laser indicator sound when spawning warning
        if self.laser_indicator_sound:
            self.laser_indicator_sound.play()
            
        self.lasers.append(Laser(is_vertical, position))
        
    def update(self, is_talking=False, player=None, frozen=False):
        if not self.active or frozen:
            return
            
        current_time = pygame.time.get_ticks() / 1000.0
        
        # Calculate health percentage
        health_percentage = self.health / self.max_health if self.max_health > 0 else 1.0
        
        # Speed multiplier based on health: 2x faster at 25% health
        speed_multiplier = 2.0 if health_percentage <= 0.25 else 1.0
        
        # Only update during boss fight (not during talking)
        # Boss doesn't move or shoot until dialogue is done
        if not is_talking:
            # Phase 1 AI: Switch between shooting and chasing
            if self.phase == 1:
                # Reset phase start time when dialogue ends (only once)
                if not self._intro_complete:
                    self.phase1_mode_start_time = current_time
                    self._intro_complete = True
                # Check time elapsed in current mode
                time_in_mode = current_time - self.phase1_mode_start_time
                
                if self.phase1_mode == "shooting":
                    # Shooting mode: Wander aimlessly
                    self.wander_timer += 1
                    
                    # Move in current wander direction
                    self.x += math.cos(self.wander_direction) * self.wander_speed * speed_multiplier
                    self.y += math.sin(self.wander_direction) * self.wander_speed * speed_multiplier
                    
                    # Check boundaries and bounce off walls
                    boss_radius = 150
                    min_x = boss_radius
                    max_x = WINDOW_WIDTH - boss_radius
                    min_y = boss_radius
                    max_y = WINDOW_HEIGHT // 2 + 50
                    
                    # Bounce off walls
                    if self.x < min_x or self.x > max_x:
                        self.wander_direction = math.pi - self.wander_direction
                        self.x = max(min_x, min(max_x, self.x))
                    
                    if self.y < min_y or self.y > max_y:
                        self.wander_direction = -self.wander_direction
                        self.y = max(min_y, min(max_y, self.y))
                    
                    # Change wandering direction periodically (after bouncing or randomly)
                    if self.wander_timer >= self.wander_change_interval:
                        self.wander_direction = random.uniform(0, 2 * math.pi)
                        self.wander_timer = 0
                        self.wander_change_interval = random.randint(90, 150)
                    
                    # At 50% health or below, always have lasers spawning and skip to chase/powerball cycle
                    # Shooting mode: 10 seconds (unless health <= 50%)
                    if health_percentage <= 0.5:
                        # Skip wandering and shooting modes, go straight to chasing
                        if time_in_mode > 2.0:  # Short window for lasers to spawn
                            # Switch to chasing mode
                            self.phase1_mode = "chasing"
                            self.phase1_mode_start_time = current_time
                            self.wander_timer = 0
                            # Keep lasers active (don't clear them)
                            self.last_charge_time = -10
                    elif time_in_mode > 10.0:
                        # Switch to wandering mode
                        self.phase1_mode = "wandering"
                        self.phase1_mode_start_time = current_time
                        self.wander_timer = 0
                        # Clear all lasers when switching modes
                        self.lasers = []
                    
                    # Spawn lasers during shooting mode
                    # At 50% health or below, always keep spawning lasers
                    if health_percentage <= 0.5:
                        # Always keep lasers spawning when below 50%
                        time_for_next_laser = 1.0 + len(self.lasers) * self.laser_spawn_interval * 0.6  # More frequent
                        if time_in_mode >= time_for_next_laser and len(self.lasers) < 15:  # More lasers at once
                            self.spawn_laser()
                    elif time_in_mode > 3.0:  # Start spawning after 3 seconds
                        time_for_next_laser = 3.0 + len(self.lasers) * self.laser_spawn_interval
                        if time_in_mode >= time_for_next_laser and len(self.lasers) < 10:
                            self.spawn_laser()
                            
                elif self.phase1_mode == "wandering":
                    # Wandering mode: 1 second - boss wanders around after shooting
                    self.wander_timer += 1
                    
                    # Move in current wander direction
                    self.x += math.cos(self.wander_direction) * self.wander_speed * speed_multiplier
                    self.y += math.sin(self.wander_direction) * self.wander_speed * speed_multiplier
                    
                    # Check boundaries and bounce off walls
                    boss_radius = 150
                    min_x = boss_radius
                    max_x = WINDOW_WIDTH - boss_radius
                    min_y = boss_radius
                    max_y = WINDOW_HEIGHT // 2 + 50
                    
                    # Bounce off walls
                    if self.x < min_x or self.x > max_x:
                        self.wander_direction = math.pi - self.wander_direction
                        self.x = max(min_x, min(max_x, self.x))
                    
                    if self.y < min_y or self.y > max_y:
                        self.wander_direction = -self.wander_direction
                        self.y = max(min_y, min(max_y, self.y))
                    
                    # Change wandering direction periodically (after bouncing or randomly)
                    if self.wander_timer >= self.wander_change_interval:
                        self.wander_direction = random.uniform(0, 2 * math.pi)
                        self.wander_timer = 0
                        self.wander_change_interval = random.randint(30, 60)
                    
                    # Wandering mode: 1 second
                    if time_in_mode > 1.0:
                        # Switch to chasing mode
                        self.phase1_mode = "chasing"
                        self.phase1_mode_start_time = current_time
                        self.wander_timer = 0
                        self.last_charge_time = -10  # Reset charge timer for chase mode
                            
                elif self.phase1_mode == "chasing":
                    # At 50% health, chase for shorter duration (5 seconds) to cycle faster
                    chase_duration = 5.0 if health_percentage <= 0.5 else 10.0
                    
                    # Chasing mode: 10 seconds (or 5 seconds if health <= 50%), then switch to powerball mode
                    if time_in_mode > chase_duration:
                        # Switch to powerball mode
                        self.phase1_mode = "powerball"
                        self.phase1_mode_start_time = current_time
                        self.is_charging = False
                        self.is_launching = False
                        self.charge_timer = 0
                        self.powerball_wave = 0
                        self.last_powerball_wave_time = 0
                        self.wander_timer = 0  # Reset wander timer for powerball phase
                        self.wander_direction = random.uniform(0, 2 * math.pi)  # Pick a new wander direction
                    
                    # Charging attack behavior
                    if not self.is_charging and not self.is_launching:
                        # Move toward player before charging
                        if player:
                            dx = player.x - self.x
                            dy = player.y - self.y
                            distance = math.sqrt(dx**2 + dy**2)
                            
                            if distance > 0:
                                # Normalize direction
                                move_x = dx / distance
                                move_y = dy / distance
                                
                                # Move toward player
                                self.x += move_x * self.chase_speed * speed_multiplier
                                self.y += move_y * self.chase_speed * speed_multiplier
                                
                                # Keep boss within bounds (allow to go further down when chasing)
                                self.x = max(150, min(WINDOW_WIDTH - 150, self.x))
                                self.y = max(150, min(int(WINDOW_HEIGHT * 0.85), self.y))
                        
                        # Start charging every 3 seconds after initially moving for 1 second
                        time_since_last_charge = time_in_mode - self.last_charge_time
                        if time_in_mode > 1.0 and time_since_last_charge >= 3.0:
                            self.is_charging = True
                            self.charge_timer = 0
                            self.last_charge_time = time_in_mode
                            
                            # Play charge up sound
                            if self.charge_up_sound:
                                self.charge_up_sound.play()
                            # Store target from current position (where boss stopped)
                            if player:
                                self.target_x = player.x
                                self.target_y = player.y
                            else:
                                self.target_x = WINDOW_WIDTH // 2
                                self.target_y = WINDOW_HEIGHT // 2
                            
                            # Calculate charge direction
                            dx = self.target_x - self.x
                            dy = self.target_y - self.y
                            distance = math.sqrt(dx**2 + dy**2)
                            
                            # Only set charge direction if distance is meaningful
                            if distance > 10:
                                self.charge_direction_x = dx / distance
                                self.charge_direction_y = dy / distance
                            else:
                                # Too close to player, pick a random direction to still charge
                                random_angle = random.uniform(0, 2 * math.pi)
                                self.charge_direction_x = math.cos(random_angle)
                                self.charge_direction_y = math.sin(random_angle)
                    
                    # Spawn lasers during chase mode when health is <= 50%
                    if health_percentage <= 0.5:
                        time_for_next_laser = 1.0 + len(self.lasers) * self.laser_spawn_interval * 0.6  # More frequent
                        if time_in_mode >= time_for_next_laser and len(self.lasers) < 15:  # More lasers at once
                            self.spawn_laser()
                    
                    if self.is_charging:
                        # Charging state: boss stops and shows mad sprite
                        self.charge_timer += 1
                        if self.charge_timer >= self.charge_duration:
                            # Finished charging, start launching
                            self.is_charging = False
                            self.is_launching = True
                            self.charge_timer = 0
                            self.launch_timer = 0
                            
                            # Play charge sound (lunge/attack)
                            if self.charge_sound:
                                self.charge_sound.play()
                    
                    elif self.is_launching:
                        # Launching state: boss moves fast toward target
                        self.x += self.charge_direction_x * self.charge_launch_speed * speed_multiplier
                        self.y += self.charge_direction_y * self.charge_launch_speed * speed_multiplier
                        
                        # Keep boss within bounds (allow to go further down when charging)
                        self.x = max(150, min(WINDOW_WIDTH - 150, self.x))
                        self.y = max(150, min(int(WINDOW_HEIGHT * 0.85), self.y))
                        
                        # Check if passed target or hit boundary or launched for minimum time
                        dist_to_target = math.sqrt((self.x - self.target_x)**2 + (self.y - self.target_y)**2)
                        self.launch_timer += 1
                        
                        # Stop if passed target (overshot) or launched for at least 1 second
                        has_passed_target = (self.charge_direction_x * (self.x - self.target_x) + 
                                           self.charge_direction_y * (self.y - self.target_y)) > 0
                        
                        if has_passed_target or self.launch_timer >= 60 or self.x < 100 or self.x > WINDOW_WIDTH - 100 or self.y < 100 or self.y > int(WINDOW_HEIGHT * 0.85):
                            # Stop launching
                            self.is_launching = False
                            self.launch_timer = 0
                
                elif self.phase1_mode == "powerball":
                    # At 50% health, powerball for shorter duration (5 seconds) to cycle faster
                    powerball_duration = 5.0 if health_percentage <= 0.5 else 10.0
                    
                    # PowerBall phase: Summon powerballs that arc to player's last location
                    # 10 seconds total (or 5 seconds if health <= 50%)
                    if time_in_mode > powerball_duration:
                        # At 50% health, cycle back to chasing mode instead of shooting
                        if health_percentage <= 0.5:
                            # Switch back to chasing mode (keep lasers active)
                            self.phase1_mode = "chasing"
                            self.phase1_mode_start_time = current_time
                            self.last_charge_time = -10
                        else:
                            # Switch back to shooting mode
                            self.phase1_mode = "shooting"
                            self.phase1_mode_start_time = current_time
                        
                        self.powerball_wave = 0
                        self.last_powerball_wave_time = 0
                        # Force clear all powerballs and reset charging states
                        for pb in self.powerballs:
                            pb.active = False
                            pb.exploded = True  # Mark as exploded so they clean up properly
                            pb.explosion_frames = 20  # Set to max so they don't draw anymore
                        self.powerballs = []
                        self.is_charging = False
                        self.is_launching = False
                        self.charge_timer = 0
                        self.launch_timer = 0
                    
                    # Wandering behavior during powerball phase
                    self.wander_timer += 1
                    
                    # Check boundaries first - only constrain movement if boss would go out of bounds
                    boss_radius = 150
                    min_x = boss_radius
                    max_x = WINDOW_WIDTH - boss_radius
                    min_y = boss_radius
                    # Don't restrict max_y - let boss stay where it is and shoot from there
                    
                    # Calculate where boss would move
                    next_x = self.x + math.cos(self.wander_direction) * self.wander_speed * speed_multiplier
                    next_y = self.y + math.sin(self.wander_direction) * self.wander_speed * speed_multiplier
                    
                    # Only apply movement and bounce if it would go out of bounds, otherwise just move
                    if next_x < min_x or next_x > max_x:
                        self.wander_direction = math.pi - self.wander_direction
                        # Only clamp if it actually goes out of bounds
                        if self.x < min_x:
                            self.x = min_x
                        elif self.x > max_x:
                            self.x = max_x
                        else:
                            # Boss is still in bounds, just reverse direction for next frame
                            self.x += math.cos(self.wander_direction) * self.wander_speed * speed_multiplier
                    else:
                        self.x = next_x
                    
                    # Only check bottom boundary for Y, not top (let boss be anywhere vertically)
                    if next_y < min_y:
                        self.wander_direction = -self.wander_direction
                        if self.y < min_y:
                            self.y = min_y
                        else:
                            # Boss is still in bounds, just reverse direction for next frame
                            self.y += math.sin(self.wander_direction) * self.wander_speed * speed_multiplier
                    else:
                        self.y = next_y
                    
                    # Change wandering direction periodically (after bouncing or randomly)
                    if self.wander_timer >= self.wander_change_interval:
                        self.wander_direction = random.uniform(0, 2 * math.pi)
                        self.wander_timer = 0
                        self.wander_change_interval = random.randint(30, 60)
                    
                    # Spawn lasers during powerball mode when health is <= 50%
                    if health_percentage <= 0.5:
                        time_for_next_laser = 1.0 + len(self.lasers) * self.laser_spawn_interval * 0.6  # More frequent
                        if time_in_mode >= time_for_next_laser and len(self.lasers) < 15:  # More lasers at once
                            self.spawn_laser()
                    
                    # Spawn powerballs continuously throughout the phase (but stop 1 second before phase ends)
                    spawn_cutoff = powerball_duration - 1.0  # Stop spawning 1 second before phase ends
                    if player and time_in_mode < spawn_cutoff:
                        # Check if it's time to spawn the next wave (every 1 second: spawn immediately, then wander for 1 sec)
                        wave_spawn_interval = 1.0  # 1 second between each spawn
                        
                        if time_in_mode - self.last_powerball_wave_time >= wave_spawn_interval:
                            # Get target location at spawn time
                            target_x = player.x
                            target_y = player.y
                            
                            # Play projectile sound when spawning powerballs
                            if self.projectile_sound:
                                self.projectile_sound.play()
                            
                            # Spawn a pair of powerballs (one left arc, one right arc)
                            self.powerballs.append(PowerBall(self.x, self.y, target_x, target_y, 'left'))
                            self.powerballs.append(PowerBall(self.x, self.y, target_x, target_y, 'right'))
                            
                            self.powerball_wave += 1  # Keep track of wave count but don't limit it
                            self.last_powerball_wave_time = time_in_mode
                            
                            # Show mad sprite for 0.5 seconds when launching powerballs
                            self.is_launching_powerballs = True
                            self.powerball_launch_timer = 0
                    
                    # Update powerball launch timer
                    if self.is_launching_powerballs:
                        self.powerball_launch_timer += 1
                        # Show mad sprite for 0.5 seconds (30 frames at 60 FPS)
                        if self.powerball_launch_timer >= 30:
                            self.is_launching_powerballs = False
                    
                    # Update powerballs
                    for powerball in self.powerballs:
                        powerball.update()
                    
                    # Remove inactive powerballs (keep active ones or ones still showing explosion animation)
                    self.powerballs = [pb for pb in self.powerballs if pb.active or (pb.exploded and pb.explosion_frames < 20)]
        
        # Update powerballs regardless of phase (in case any are left behind)
        for powerball in self.powerballs:
            powerball.update()
        
        # Clean up powerballs regardless of phase
        self.powerballs = [pb for pb in self.powerballs if pb.active or (pb.exploded and pb.explosion_frames < 20)]
        
        # Update all lasers
        for laser in self.lasers:
            laser.update()
            
            # Check if laser just became active and play shoot sound
            if laser.just_became_active and not laser.shoot_sound_played:
                if self.laser_shoot_sound:
                    self.laser_shoot_sound.play()
                laser.just_became_active = False
                laser.shoot_sound_played = True
            
        # Remove inactive lasers
        self.lasers = [l for l in self.lasers if l.active]
    
    def check_collision_with_player(self, player):
        """Check if boss collides with player"""
        if not self.active or not player.active:
            return False
            
        dx = self.x - player.x
        dy = self.y - player.y
        distance = math.sqrt(dx**2 + dy**2)
        
        # Check if within collision radius
        return distance < (self.collision_radius + player.radius)
        
    def draw_health_bar(self, screen):
        """Draw boss health bar at the top of the screen"""
        if not self.active:
            return
            
        bar_width = 600
        bar_height = 40
        bar_x = (WINDOW_WIDTH - bar_width) // 2
        bar_y = 20
        
        # Draw background (black with white border)
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), width=3)
        
        # Draw health bar (red to green gradient)
        health_percentage = self.health / self.max_health
        health_width = int(bar_width * health_percentage)
        
        if health_percentage > 0:
            # Color: red -> yellow -> green based on health
            if health_percentage > 0.5:
                # Green to yellow
                green_amount = int(255 * (health_percentage - 0.5) * 2)
                health_color = (255 - green_amount, 255, 0)
            else:
                # Yellow to red
                red_amount = int(255 * (health_percentage * 2))
                health_color = (255, red_amount, 0)
                
            pygame.draw.rect(screen, health_color, (bar_x + 3, bar_y + 3, health_width - 6, bar_height - 6))
        
        # Draw health text
        try:
            font = pygame.font.Font(None, 32)
            health_text = f"{int(self.health)} / {int(self.max_health)}"
            text_surface = font.render(health_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
            screen.blit(text_surface, text_rect)
        except:
            pass
        
    def draw(self, screen, rotation=0, scale=1.0):
        if self.active:
            # Draw all lasers
            for laser in self.lasers:
                laser.draw(screen)
            
            # Draw all powerballs
            for powerball in self.powerballs:
                powerball.draw(screen)
                
            # Show mad sprite when charging, launching, or launching powerballs
            if self.is_charging or self.is_launching or self.is_launching_powerballs:
                if self.image_mad:
                    image_rect = self.image_mad.get_rect(center=(self.x, self.y))
                    screen.blit(self.image_mad, image_rect)
                else:
                    # Draw placeholder if image didn't load
                    pygame.draw.circle(screen, RED, (self.x, self.y), 100)
                    pygame.draw.circle(screen, WHITE, (self.x, self.y), 100, width=3)
            else:
                if self.image:
                    if rotation != 0 or scale != 1.0:
                        # Apply rotation and scale for defeat animation
                        rotated_image = pygame.transform.rotate(self.image, rotation)
                        rotated_image = pygame.transform.scale(rotated_image, 
                                                               (int(rotated_image.get_width() * scale), 
                                                                int(rotated_image.get_height() * scale)))
                        image_rect = rotated_image.get_rect(center=(self.x, self.y))
                        screen.blit(rotated_image, image_rect)
                    else:
                        image_rect = self.image.get_rect(center=(self.x, self.y))
                        screen.blit(self.image, image_rect)
                else:
                    # Draw placeholder if image didn't load
                    pygame.draw.circle(screen, RED, (self.x, self.y), 100)
                    pygame.draw.circle(screen, WHITE, (self.x, self.y), 100, width=3)

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
        
        # Initialize snail
        self.snail = Snail()
        
        # Initialize player
        self.player = Player()
        
        # Initialize boss
        self.boss = Boss()
        
        # Asteroid configuration - ADJUST THIS TO CHANGE NUMBER OF ASTEROIDS
        self.NUM_ASTEROIDS = 5  # Change this number to adjust asteroid count
        
        # Initialize asteroids
        self.asteroids = []
        
        # Game state
        self.score = 0
        self.game_over = False
        self.boss_intro_shown = False
        self.boss_intro_timer = 0
        self.boss_intro_active = False
        self.boss_flash_timer = 0  # Flash of light effect
        self.boss_music_played = False  # Track if battle music has been played
        self.boss_talking_sound = None  # Talking sound effect
        self.boss_talking_channel = None  # Channel for talking sound
        self.boss_typed_text = ""  # Currently displayed text
        self.boss_full_text = "Witness the rebirth of the void."  # Full dialogue
        self.boss_typing_index = 0  # Current character index
        self.boss_typing_timer = 0  # Timer for typing delay
        self.boss_talking_sound_played = False  # Track if talking sound has been played
        
        # Boss defeat/victory sequence
        self.boss_defeated = False  # Track if boss has been defeated
        self.boss_defeat_sequence = None  # "dialogue", "spinning", "victory"
        self.boss_defeat_timer = 0  # Timer for defeat sequence
        self.boss_defeat_text = "Oh no"  # Defeat dialogue text
        self.boss_defeat_typed_text = ""  # Currently displayed defeat text
        self.boss_defeat_typing_index = 0  # Current character index for defeat dialogue
        self.boss_defeat_typing_timer = 0  # Timer for defeat typing delay
        self.boss_rotation = 0  # Boss rotation angle for spinning animation
        self.victory_shown = False  # Track if victory screen has been shown
        self.boss_points_awarded = False  # Track if 500 points have been awarded for boss defeat
        
        # Pre-boss typing text
        self.pre_boss_text_active = False  # Track if showing pre-boss text
        self.pre_boss_typed_text = ""  # Currently displayed text
        self.pre_boss_full_text = "something's wrong..."  # Synonyms text
        self.pre_boss_typing_index = 0  # Current character index
        self.pre_boss_typing_timer = 0  # Timer for typing delay
        self.pre_boss_text_display_timer = 0  # Timer for how long text stays after typing completes
        
        # Load select sound for Play button
        self.select_sound = None
        select_paths = ["prog5/Assets/Sounds/Select.wav", "Assets/Sounds/Select.wav", "prog5/Assets/Sounds/select.wav", "Assets/Sounds/select.wav"]
        for path in select_paths:
            try:
                self.select_sound = pygame.mixer.Sound(path)
                print(f"Select sound loaded from: {path}")
                break
            except Exception as e:
                print(f"Could not load select sound from {path}: {e}")
                continue
        
        # Load countdown sound for countdown changes
        self.countdown_sound = None
        countdown_paths = ["prog5/Assets/Sounds/Countdown.wav", "Assets/Sounds/Countdown.wav"]
        for path in countdown_paths:
            try:
                self.countdown_sound = pygame.mixer.Sound(path)
                print(f"Countdown sound loaded from: {path}")
                break
            except Exception as e:
                print(f"Could not load countdown sound from {path}: {e}")
                continue
        
        # Load and play opening music
        opening_paths = ["prog5/Assets/Sounds/Opening.mp3", "Assets/Sounds/Opening.mp3"]
        for path in opening_paths:
            try:
                pygame.mixer.music.load(path)
                pygame.mixer.music.play()
                print(f"Opening music loaded from: {path}")
                break
            except Exception as e:
                print(f"Could not load opening music from {path}: {e}")
                continue
        
        # Load ingame music path (will play when game starts)
        self.ingame_music_path = None
        ingame_paths = ["prog5/Assets/Sounds/Ingame.mp3", "Assets/Sounds/Ingame.mp3"]
        for path in ingame_paths:
            if os.path.exists(path):
                self.ingame_music_path = path
                print(f"Ingame music found at: {path}")
                break
        
        # Load battle music path (will play when boss appears)
        self.battle_music_path = None
        battle_paths = ["prog5/Assets/Sounds/Battle.mp3", "Assets/Sounds/Battle.mp3"]
        for path in battle_paths:
            if os.path.exists(path):
                self.battle_music_path = path
                print(f"Battle music found at: {path}")
                break
        
        # Load boss talking sound
        talking_sound_paths = ["prog5/Assets/Sounds/TalkingBoss.mp3", "Assets/Sounds/TalkingBoss.mp3", 
                               "prog5/Assets/Sounds/TalkingBoss.wav", "Assets/Sounds/TalkingBoss.wav"]
        for path in talking_sound_paths:
            try:
                self.boss_talking_sound = pygame.mixer.Sound(path)
                print(f"Loaded talking boss sound from: {path}")
                break
            except:
                continue
        
        self.title_time = 0  # For animation
        self.transition_state = "none"  # none, speeding_up, fast, slowing_down, ready
        self.transition_timer = 0
        self.starfield_speed = 1.0
        self.countdown_timer = 360  # Total transition time: 360 frames (6 seconds) with 0.5s delay before countdown starts
        self.prev_countdown_text = None  # Track previous countdown text to detect changes
        
    def draw_starfield(self, speed_multiplier=1.0):
        # Update and draw all stars
        for star in self.stars:
            star.update(speed_multiplier)
            star.draw(self.screen)
        
        # Update and draw snail with speed multiplier
        self.snail.update(speed_multiplier)
        self.snail.draw(self.screen)
        
        # Update and draw player - pass transition state so it knows when to stop
        self.player.update(speed_multiplier, self.transition_state)
        self.player.draw(self.screen)
    
    def spawn_asteroids(self):
        """Initialize asteroids"""
        self.asteroids = []
        for _ in range(self.NUM_ASTEROIDS):
            self.asteroids.append(Asteroid())
    
    def update_game(self):
        """Update game logic - asteroids, collisions, scoring"""
        if not self.player.active or self.player.phase != "centered" or self.game_over:
            return
        
        # Don't update if pre-boss text or boss intro is active
        if self.pre_boss_text_active:
            # Handle pre-boss text typing animation
            if self.pre_boss_typing_index < len(self.pre_boss_full_text):
                self.pre_boss_typing_timer += 1
                # Type a new character every 3 frames (adjust for speed)
                if self.pre_boss_typing_timer >= 3:
                    self.pre_boss_typing_timer = 0
                    self.pre_boss_typed_text += self.pre_boss_full_text[self.pre_boss_typing_index]
                    self.pre_boss_typing_index += 1
            else:
                # Typing complete, count down 3 seconds (180 frames at 60fps)
                self.pre_boss_text_display_timer += 1
                if self.pre_boss_text_display_timer >= 180:  # 3 seconds
                    # Now trigger actual boss intro
                    self.pre_boss_text_active = False
                    self.boss_intro_active = True
                    self.boss_intro_shown = True
                    self.boss_intro_timer = 180  # 3 seconds at 60fps
                    self.boss_flash_timer = 30  # Flash effect duration (0.5 seconds at 60fps)
                    self.boss_music_played = False  # Reset flag for music
                    self.boss.start()
                    
                    # Teleport player back to center for boss fight
                    self.player.x = WINDOW_WIDTH // 2
                    self.player.y = WINDOW_HEIGHT // 2
                    self.player.vel_x = 0
                    self.player.vel_y = 0
            return  # Skip other updates during pre-boss text animation
        
        # Don't update if boss intro is active
        if self.boss_intro_active:
            self.boss_intro_timer -= 1
            if self.boss_flash_timer > 0:
                self.boss_flash_timer -= 1
                # Play battle music after flash ends
                if self.boss_flash_timer == 0 and not self.boss_music_played:
                    self.boss_music_played = True
                    if self.battle_music_path:
                        try:
                            pygame.mixer.music.stop()
                            pygame.mixer.music.load(self.battle_music_path)
                            pygame.mixer.music.play(-1)  # Loop indefinitely
                            print(f"Battle music started: {self.battle_music_path}")
                        except Exception as e:
                            print(f"Could not play battle music: {e}")
            
            # Handle typing animation after flash
            if self.boss_flash_timer == 0 and self.boss_typing_index < len(self.boss_full_text):
                # Play talking sound once when typing starts
                if not self.boss_talking_sound_played and self.boss_talking_sound:
                    try:
                        self.boss_talking_channel = self.boss_talking_sound.play()
                        self.boss_talking_sound_played = True
                    except:
                        pass
                
                # Lower music volume while typing
                if self.boss_talking_channel and self.boss_talking_channel.get_busy():
                    pygame.mixer.music.set_volume(0.3)  # Lower music when talking
                else:
                    pygame.mixer.music.set_volume(1.0)  # Full volume when not talking
                
                self.boss_typing_timer += 1
                # Type a new character every 3 frames (adjust for speed)
                if self.boss_typing_timer >= 3:
                    self.boss_typing_timer = 0
                    self.boss_typed_text += self.boss_full_text[self.boss_typing_index]
                    self.boss_typing_index += 1
                    
                    # Stop talking sound when typing is complete
                    if self.boss_typing_index >= len(self.boss_full_text):
                        if self.boss_talking_channel and self.boss_talking_channel.get_busy():
                            self.boss_talking_channel.stop()
            
            elif self.boss_flash_timer == 0:
                # Not typing - stop talking sound if still playing and keep music at full volume
                if self.boss_talking_channel and self.boss_talking_channel.get_busy():
                    self.boss_talking_channel.stop()
                pygame.mixer.music.set_volume(1.0)
            
            if self.boss_intro_timer <= 0:
                self.boss_intro_active = False
            return  # Don't update anything else during intro
        
        # Update asteroids
        for asteroid in self.asteroids:
            asteroid.update()
        
        # Check asteroid-asteroid collisions
        for i in range(len(self.asteroids)):
            for j in range(i + 1, len(self.asteroids)):
                if self.asteroids[i].active and self.asteroids[j].active:
                    if self.asteroids[i].collide_with(self.asteroids[j]):
                        self.asteroids[i].bounce(self.asteroids[j])
        
        # Check bullet-asteroid collisions
        for bullet in self.player.bullets:
            if not bullet.active:
                continue
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                if asteroid.active and asteroid.collide_with(bullet):
                    # Destroy both bullet and asteroid
                    bullet.active = False
                    asteroid.active = False
                    
                    # Add score based on asteroid size
                    self.score += asteroid.value
                    
                    # Create smaller asteroids if this was a large or medium asteroid
                    if asteroid.size == "large":
                        # Create 2 medium asteroids at the destroyed asteroid's position
                        for _ in range(2):
                            new_asteroid = Asteroid(asteroid.x, asteroid.y, "medium")
                            self.asteroids.append(new_asteroid)
                    elif asteroid.size == "medium":
                        # Create 2 small asteroids at destroyed asteroid's position
                        for _ in range(2):
                            new_asteroid = Asteroid(asteroid.x, asteroid.y, "small")
                            self.asteroids.append(new_asteroid)
                    
                    break  # Bullet destroyed, move to next bullet
        
        # Check beam-asteroid collisions
        for beam in self.player.beams:
            if not beam.active:
                continue
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                if asteroid.active and asteroid.id not in beam.hit_targets:
                    if beam.check_collision_point(asteroid.x, asteroid.y, asteroid.radius):
                        # Mark asteroid as hit (beam can hit multiple targets)
                        beam.hit_targets.add(asteroid.id)
                        # Destroy asteroid
                        asteroid.active = False
                        
                        # Add score based on asteroid size
                        self.score += asteroid.value
                        
                        # Create smaller asteroids if this was a large or medium asteroid
                        if asteroid.size == "large":
                            # Create 2 medium asteroids at the destroyed asteroid's position
                            for _ in range(2):
                                new_asteroid = Asteroid(asteroid.x, asteroid.y, "medium")
                                self.asteroids.append(new_asteroid)
                        elif asteroid.size == "medium":
                            # Create 2 small asteroids at destroyed asteroid's position
                            for _ in range(2):
                                new_asteroid = Asteroid(asteroid.x, asteroid.y, "small")
                                self.asteroids.append(new_asteroid)
        
        # Remove inactive asteroids
        self.asteroids = [a for a in self.asteroids if a.active]
        
        # Check if all asteroids are destroyed and trigger pre-boss text
        if len(self.asteroids) == 0 and not self.boss_intro_shown and not self.boss_intro_active and not self.pre_boss_text_active:
            self.pre_boss_text_active = True
            self.pre_boss_typed_text = ""
            self.pre_boss_typing_index = 0
            self.pre_boss_typing_timer = 0
            self.pre_boss_text_display_timer = 0
            
            # Fade out ingame music when last meteoroid is destroyed
            pygame.mixer.music.fadeout(3000)  # Fade out over 3 seconds
        
        # Check ship-asteroid collisions
        if not self.game_over:
            for asteroid in self.asteroids:
                if asteroid.active and asteroid.collide_with(self.player):
                    # Ship takes damage from asteroid!
                    if self.player.take_damage():
                        # Play explosion sound
                        explosion_paths = ["prog5/Assets/Sounds/explosion1.wav", 
                                          "Assets/Sounds/explosion1.wav"]
                        for path in explosion_paths:
                            try:
                                explosion_sound = pygame.mixer.Sound(path)
                                explosion_sound.play()
                                break
                            except:
                                continue
                    # Check if player is dead
                    if self.player.is_dead():
                        self.game_over = True
                    break
        
        # Check ship-laser collisions during boss fight
        if not self.game_over and self.boss.active and not self.boss_intro_active:
            for laser in self.boss.lasers:
                if laser.check_collision(self.player):
                    # Ship takes damage from laser!
                    if self.player.take_damage():
                        # Play explosion sound
                        explosion_paths = ["prog5/Assets/Sounds/explosion1.wav", 
                                          "Assets/Sounds/explosion1.wav"]
                        for path in explosion_paths:
                            try:
                                explosion_sound = pygame.mixer.Sound(path)
                                explosion_sound.play()
                                break
                            except:
                                continue
                    # Check if player is dead
                    if self.player.is_dead():
                        self.game_over = True
                    break
        
        # Check bullet-boss collisions (bullets do 20 damage)
        if not self.game_over and self.boss.active and not self.boss_intro_active:
            for bullet in self.player.bullets:
                if not bullet.active:
                    continue
                # Check if bullet hits boss
                dx = bullet.x - self.boss.x
                dy = bullet.y - self.boss.y
                distance = math.sqrt(dx**2 + dy**2)
                boss_radius = 150  # Boss hitbox radius
                
                if distance < (boss_radius + bullet.radius):
                    # Bullet hits boss - deal damage based on charge
                    bullet.active = False
                    self.boss.health -= bullet.damage
                    if self.boss.health < 0:
                        self.boss.health = 0
                        
                        # Trigger boss defeat sequence if not already triggered
                        if not self.boss_defeated and self.boss.active:
                            self.boss_defeated = True
                            self.boss_defeat_sequence = "dialogue"
                            self.boss_defeat_timer = 0
                            self.boss_defeat_typed_text = ""
                            self.boss_defeat_typing_index = 0
                            # Clear all boss attacks
                            self.boss.lasers = []
                            self.boss.powerballs = []
                            self.boss.is_charging = False
                            self.boss.is_launching = False
                            # Stop boss from moving
                            self.boss._defeat_frozen = True
        
        # Check beam-boss collisions
        if not self.game_over and self.boss.active and not self.boss_intro_active:
            boss_radius = 150  # Boss hitbox radius
            boss_id = id(self.boss)
            for beam in self.player.beams:
                if not beam.active:
                    continue
                # Check if beam hits boss (only once per beam)
                if boss_id not in beam.hit_targets:
                    if beam.check_collision_point(self.boss.x, self.boss.y, boss_radius):
                        # Beam hits boss - deal damage
                        beam.hit_targets.add(boss_id)
                        self.boss.health -= beam.damage
                        if self.boss.health < 0:
                            self.boss.health = 0
                            
                            # Trigger boss defeat sequence if not already triggered
                            if not self.boss_defeated and self.boss.active:
                                self.boss_defeated = True
                                self.boss_defeat_sequence = "dialogue"
                                self.boss_defeat_timer = 0
                                self.boss_defeat_typed_text = ""
                                self.boss_defeat_typing_index = 0
                                # Clear all boss attacks
                                self.boss.lasers = []
                                self.boss.powerballs = []
                                self.boss.is_charging = False
                                self.boss.is_launching = False
                                # Stop boss from moving
                                self.boss._defeat_frozen = True
        
        # Check powerball collisions with player
        if not self.game_over and self.boss.active and not self.boss_intro_active:
            for powerball in self.boss.powerballs:
                # Check active powerball collision
                if powerball.check_collision_with_player(self.player):
                    # Player takes damage from powerball
                    if self.player.take_damage():
                        # Play explosion sound
                        explosion_paths = ["prog5/Assets/Sounds/explosion1.wav", 
                                          "Assets/Sounds/explosion1.wav"]
                        for path in explosion_paths:
                            try:
                                explosion_sound = pygame.mixer.Sound(path)
                                explosion_sound.play()
                                break
                            except:
                                continue
                    # Check if player is dead
                    if self.player.is_dead():
                        self.game_over = True
                    powerball.active = False
                    powerball.exploded = True
                
                # Check explosion collision and play sound only once
                if powerball.exploded and not powerball.explosion_sound_played:
                    # Play explosion sound once when it first explodes
                    explosion_paths = ["prog5/Assets/Sounds/explosion1.wav", 
                                      "Assets/Sounds/explosion1.wav"]
                    for path in explosion_paths:
                        try:
                            explosion_sound = pygame.mixer.Sound(path)
                            explosion_sound.play()
                            break
                        except:
                            continue
                    powerball.explosion_sound_played = True
                    
                    # Check if player is in explosion radius
                    if powerball.check_explosion_collision_with_player(self.player):
                        if self.player.take_damage():
                            # Damage sound already played above
                            pass
                        if self.player.is_dead():
                            self.game_over = True
        
        # Check boss collision with player during boss fight
        if not self.game_over and self.boss.active and not self.boss_intro_active:
            if self.boss.check_collision_with_player(self.player):
                # Player takes damage from touching boss
                if self.player.take_damage():
                    # Play explosion sound
                    explosion_paths = ["prog5/Assets/Sounds/explosion1.wav", 
                                      "Assets/Sounds/explosion1.wav"]
                    for path in explosion_paths:
                        try:
                            explosion_sound = pygame.mixer.Sound(path)
                            explosion_sound.play()
                            break
                        except:
                            continue
                # Check if player is dead
                if self.player.is_dead():
                    self.game_over = True
    
    def draw_asteroids(self):
        """Draw all asteroids"""
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
    
    def draw_score(self):
        """Draw the score on screen (right side)"""
        score_text = f"SCORE: {self.score}"
        try:
            # Create pixelated text by rendering at small size then scaling up
            small_font = pygame.font.Font(None, 12)  # Small font for pixelation
            small_surface = small_font.render(score_text, True, WHITE)
            # Scale up 6x to create pixelated effect (12 * 6 = 72)
            text_surface = pygame.transform.scale(small_surface, 
                                                   (small_surface.get_width() * 6, 
                                                    small_surface.get_height() * 6))
            # Position on right side
            text_x = WINDOW_WIDTH - text_surface.get_width() - 50
            self.screen.blit(text_surface, (text_x, 50))
        except:
            pass
    
    def draw_teleport_charges(self):
        """Draw teleport charges as blue circles below hearts"""
        if not self.player.active or self.player.phase != "centered":
            return
            
        # Calculate position below hearts (hearts are at y=20, height ~45)
        indicator_y = 75  # Below the hearts
        start_x = 20  # Same x position as hearts start
        circle_spacing = 35  # Space between charge circles
        circle_radius = 15
        
        # Draw up to 2 teleport charges
        for i in range(len(self.player.teleport_charges)):
            x = start_x + i * circle_spacing
            center = (x + circle_radius, indicator_y)
            
            charge_timer = self.player.teleport_charges[i]
            max_cooldown = self.player.teleport_cooldown_frames
            
            # Check if charge is fully charged
            if charge_timer >= max_cooldown:
                # Filled blue circle (available charge)
                pygame.draw.circle(self.screen, (0, 150, 255), center, circle_radius)
                pygame.draw.circle(self.screen, (0, 200, 255), center, circle_radius, width=2)
            else:
                # Recharging - draw partial fill based on progress
                progress = charge_timer / max_cooldown
                
                # Draw empty background
                pygame.draw.circle(self.screen, (30, 30, 30), center, circle_radius)
                pygame.draw.circle(self.screen, (80, 80, 80), center, circle_radius, width=2)
                
                # Draw partial fill if there's progress
                if progress > 0:
                    # Calculate how much of the circle to fill
                    fill_radius = int(circle_radius * progress)
                    if fill_radius > 0:
                        # Draw filled portion - gradient from gray to blue
                        blue_intensity = int(50 + progress * 205)
                        pygame.draw.circle(self.screen, (0, 100, blue_intensity), center, fill_radius)
    
    def handle_boss_defeat_sequence(self):
        """Handle the boss defeat sequence: dialogue -> spinning -> victory"""
        if self.boss_defeat_sequence == "dialogue":
            # Type out "Oh no" dialogue
            self.boss_defeat_typing_timer += 1
            if self.boss_defeat_typing_timer >= 8:  # Typing speed
                if self.boss_defeat_typing_index < len(self.boss_defeat_text):
                    self.boss_defeat_typed_text += self.boss_defeat_text[self.boss_defeat_typing_index]
                    self.boss_defeat_typing_index += 1
                    self.boss_defeat_typing_timer = 0
            
            # After typing completes and shown for 1.5 seconds, move to spinning
            if self.boss_defeat_typing_index >= len(self.boss_defeat_text):
                self.boss_defeat_timer += 1
                if self.boss_defeat_timer >= 90:  # 1.5 seconds at 60 FPS
                    self.boss_defeat_sequence = "spinning"
                    self.boss_defeat_timer = 0
                    self.boss_rotation = 0
        
        elif self.boss_defeat_sequence == "spinning":
            # Spin the boss into the void
            self.boss_rotation += 0.3  # Spin speed
            # Shrink the boss as it spins
            self.boss_defeat_timer += 1
            
            # After 2 seconds of spinning, show victory screen
            if self.boss_defeat_timer >= 120:  # 2 seconds at 60 FPS
                self.boss_defeat_sequence = "victory"
                self.boss_defeat_timer = 0
                self.victory_shown = True
                # Award 500 points when transitioning to victory (only once)
                if not self.boss_points_awarded:
                    self.score += 500
                    self.boss_points_awarded = True
        
        elif self.boss_defeat_sequence == "victory":
            # Show victory screen for 3 seconds, then return to asteroid area
            self.boss_defeat_timer += 1
            if self.boss_defeat_timer >= 180:  # 3 seconds at 60 FPS
                # Reset boss state
                self.boss.active = False
                self.boss.start()  # Reset boss health and state
                
                # Reset all boss-related flags
                self.boss_defeated = False
                self.boss_defeat_sequence = None
                self.boss_defeat_timer = 0
                self.boss_defeat_typed_text = ""
                self.boss_defeat_typing_index = 0
                self.boss_defeat_typing_timer = 0
                self.boss_rotation = 0
                self.victory_shown = False
                self.boss_points_awarded = False
                
                # Reset boss intro flags
                self.boss_intro_shown = False
                self.boss_intro_active = False
                self.boss_intro_timer = 0
                self.boss_flash_timer = 0
                self.boss_music_played = False
                self.boss_typed_text = ""
                self.boss_typing_index = 0
                self.boss_typing_timer = 0
                self.boss_talking_sound_played = False
                
                # Reset pre-boss text flags
                self.pre_boss_text_active = False
                self.pre_boss_typed_text = ""
                self.pre_boss_typing_index = 0
                self.pre_boss_typing_timer = 0
                self.pre_boss_text_display_timer = 0
                
                # Spawn new asteroids
                self.spawn_asteroids()
                
                # Fade out battle music and start ingame music
                pygame.mixer.music.fadeout(1000)  # Fade out battle music over 1 second
                # Load and play ingame music after fadeout
                if self.ingame_music_path:
                    try:
                        pygame.mixer.music.load(self.ingame_music_path)
                        pygame.mixer.music.play(-1)  # Loop ingame music
                    except Exception as e:
                        print(f"Could not load ingame music: {e}")
    
    def draw_game_over(self):
        """Draw game over message"""
        if not self.game_over:
            return
        
        game_over_text = "GAME OVER DUDE"
        try:
            # Create pixelated text by rendering at small size then scaling up
            # This creates the pixelated effect
            small_font = pygame.font.Font(None, 16)  # Small font for pixelation
            small_surface = small_font.render(game_over_text, True, RED)
            # Scale up 9x to create pixelated effect (16 * 9 = 144)
            text_surface = pygame.transform.scale(small_surface, 
                                                   (small_surface.get_width() * 9, 
                                                    small_surface.get_height() * 9))
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(text_surface, text_rect)
            
            final_score_text = f"FINAL SCORE: {self.score}"
            # Create pixelated text
            small_score_font = pygame.font.Font(None, 12)  # Small font for pixelation
            small_score_surface = small_score_font.render(final_score_text, True, WHITE)
            # Scale up 6x to create pixelated effect (12 * 6 = 72)
            score_surface = pygame.transform.scale(small_score_surface,
                                                     (small_score_surface.get_width() * 6,
                                                      small_score_surface.get_height() * 6))
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            self.screen.blit(score_surface, score_rect)
        except:
            pass
    
    def draw_victory_screen(self):
        """Draw victory message similar to game over"""
        if not self.victory_shown:
            return
        
        victory_text = "VICTORY"
        try:
            # Create pixelated text by rendering at small size then scaling up
            # This creates the pixelated effect
            small_font = pygame.font.Font(None, 16)  # Small font for pixelation
            small_surface = small_font.render(victory_text, True, YELLOW)
            # Scale up 9x to create pixelated effect (16 * 9 = 144)
            text_surface = pygame.transform.scale(small_surface, 
                                                   (small_surface.get_width() * 9, 
                                                    small_surface.get_height() * 9))
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(text_surface, text_rect)
            
            final_score_text = f"FINAL SCORE: {self.score}"
            # Create pixelated text
            small_score_font = pygame.font.Font(None, 12)  # Small font for pixelation
            small_score_surface = small_score_font.render(final_score_text, True, WHITE)
            # Scale up 6x to create pixelated effect (12 * 6 = 72)
            score_surface = pygame.transform.scale(small_score_surface,
                                                     (small_score_surface.get_width() * 6,
                                                      small_score_surface.get_height() * 6))
            score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            self.screen.blit(score_surface, score_rect)
        except:
            pass
    
    def draw_boss_defeat_dialogue(self):
        """Draw boss defeat dialogue"""
        if not self.boss_defeated or self.boss_defeat_sequence != "dialogue":
            return
        
        # Draw semi-transparent black overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Draw dialogue box at bottom
        dialogue_box_y = int(WINDOW_HEIGHT * 0.75)
        dialogue_box_height = int(WINDOW_HEIGHT * 0.25)
        pygame.draw.rect(self.screen, WHITE, (0, dialogue_box_y, WINDOW_WIDTH, dialogue_box_height))
        pygame.draw.rect(self.screen, BLACK, (10, dialogue_box_y + 10, WINDOW_WIDTH - 20, dialogue_box_height - 20))
        
        # Draw typed text
        try:
            font = pygame.font.Font(None, 72)
            text_surface = font.render(self.boss_defeat_typed_text, True, WHITE)
            text_x = 50
            text_y = dialogue_box_y + 50
            self.screen.blit(text_surface, (text_x, text_y))
        except:
            pass
    
    def draw_pre_boss_text(self):
        """Draw pre-boss typing text"""
        if not self.pre_boss_text_active:
            return
        
        # Draw the typing text on screen (centered, large, dramatic)
        try:
            font = pygame.font.Font(None, 96)
            text_surface = font.render(self.pre_boss_typed_text, True, RED)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            
            # Draw with a subtle glow effect
            for i in range(5):
                glow_color = (255 // (i+1), 0, 0)
                glow_surface = font.render(self.pre_boss_typed_text, True, glow_color)
                glow_rect = glow_surface.get_rect(center=(WINDOW_WIDTH // 2 + i, WINDOW_HEIGHT // 2 + i))
                screen_with_alpha = pygame.Surface(glow_surface.get_size(), pygame.SRCALPHA)
                screen_with_alpha.set_alpha(50 // (i+1))
                screen_with_alpha.blit(glow_surface, (0, 0))
                self.screen.blit(screen_with_alpha, glow_rect)
            
            self.screen.blit(text_surface, text_rect)
        except:
            pass
    
    def draw_boss_intro(self):
        """Draw boss intro dialogue with Undertale theme"""
        if not self.boss_intro_active:
            return
        
        # Draw flash of light if flash timer is active
        if self.boss_flash_timer > 0:
            # Draw boss and lasers during flash
            if self.boss.active:
                self.boss.draw(self.screen)
            # Calculate alpha based on remaining time (fade out)
            alpha = int(255 * (self.boss_flash_timer / 30))
            flash = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
            flash.set_alpha(alpha)
            flash.fill(WHITE)
            self.screen.blit(flash, (0, 0))
            return  # Don't draw dialogue during flash
        
        # Draw boss and lasers before overlay
        if self.boss.active:
            self.boss.draw(self.screen)
        
        # Draw semi-transparent black overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Undertale-themed dialogue
        dialogue = [
            "The air grows cold...",
            "Something powerful has appeared.",
            "You feel it watching you.",
            "In this world...",
            "it's kill or BE killed."
        ]
        
        # Check if boss is currently talking (sound is playing)
        is_typing = False
        if self.boss_talking_channel:
            is_typing = self.boss_talking_channel.get_busy()
        
        # Try to render typed text with Undertale-style
        try:
            font = pygame.font.Font(None, 64)
            text_surface = font.render(self.boss_typed_text, True, WHITE)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 100))
            
            # Draw text box
            box_rect = pygame.Rect(WINDOW_WIDTH // 2 - 400, WINDOW_HEIGHT // 2, 800, 200)
            pygame.draw.rect(self.screen, WHITE, box_rect, width=4)
            pygame.draw.rect(self.screen, BLACK, pygame.Rect(box_rect.x + 4, box_rect.y + 4, box_rect.width - 8, box_rect.height - 8))
            
            self.screen.blit(text_surface, text_rect)
            
            # Boss sprite always uses BossT.png
            # Don't update boss during intro - just draw it
        except:
            pass
                            
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
        
    def draw_countdown(self):
        # Helper function to render and scale text for pixelation
        def render_pixelated_text(text, color, scale=8):
            if self.use_pixel_scale:
                # Render small and scale up for pixelation
                small_text = self.font_title.render(text, True, color)
                # Scale up for pixelated retro effect
                pixelated = pygame.transform.scale(small_text, 
                                                   (small_text.get_width() * scale, 
                                                    small_text.get_height() * scale))
                return pixelated
            else:
                return self.font_title.render(text, True, color)
        
        # Determine which text to show based on timer
        # Total: 360 frames (6 seconds). Timeline: 0.5s delay (360-330) -> evenly spaced countdown
        # Countdown: 330 frames split into 4 parts: 82, 82, 82, 84 frames each
        text_to_show = None
        
        if self.countdown_timer > 330:  # 0.5s delay (first 30 frames)
            return  # Don't show anything yet - 0.5 second delay after Play button
        elif self.countdown_timer > 248:  # 3 (82 frames: 330-248)
            text_to_show = "3"
            fade_progress = (self.countdown_timer - 248) / 82.0
        elif self.countdown_timer > 166:  # 2 (82 frames: 248-166)
            text_to_show = "2"
            fade_progress = (self.countdown_timer - 166) / 82.0
        elif self.countdown_timer > 84:  # 1 (82 frames: 166-84)
            text_to_show = "1"
            fade_progress = (self.countdown_timer - 84) / 82.0
        elif self.countdown_timer > 0:  # SURVIVE (84 frames: 84-0)
            text_to_show = "SURVIVE"
            fade_progress = self.countdown_timer / 84.0
        else:
            return  # Don't draw anything if countdown is done
        
        # Play countdown sound when text changes
        if text_to_show != self.prev_countdown_text:
            self.prev_countdown_text = text_to_show
            if self.countdown_sound:
                self.countdown_sound.play()
        
        # Calculate alpha for fading effect (fade last 10% of display duration)
        if fade_progress > 0.9:
            alpha = int(255 * (1.0 - (fade_progress - 0.9) / 0.1))
        else:
            alpha = 255
        
        # Draw text with glow effect
        for i in range(8):
            # Yellow/orange glow for numbers, red/cyan glow for SURVIVE
            if text_to_show in ["3", "2", "1"]:
                glow_color = (255, 200 // (i+1), 0)
            else:  # SURVIVE
                glow_color = (255 // (i+2), 0, 100 // (i+2))
            
            glow = render_pixelated_text(text_to_show, glow_color)
            glow.set_alpha(alpha // (i+1))
            glow_rect = glow.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(glow, glow_rect)
        
        # Main text - bright white
        main_text = render_pixelated_text(text_to_show, WHITE)
        main_text.set_alpha(alpha)
        main_rect = main_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
        self.screen.blit(main_text, main_rect)
        
    def draw_menu(self):
        self.screen.fill(BLACK)
        
        # Draw starfield with speed multiplier
        self.draw_starfield(self.starfield_speed)
        
        # Draw countdown during transition (all states until countdown is done)
        if self.transition_state in ["speeding_up", "fast", "slowing_down"]:
            self.draw_countdown()
        
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
            # Get keyboard state for continuous input
            keys = pygame.key.get_pressed()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    
                if event.type == pygame.MOUSEBUTTONDOWN and self.transition_state == "none":
                    play_rect = self.draw_menu()
                    if play_rect and play_rect.collidepoint(event.pos):
                        # Play select sound if available
                        if self.select_sound:
                            self.select_sound.play()
                            print("Playing select sound!")
                        else:
                            print("Select sound not loaded!")
                        
                        # Stop opening music
                        pygame.mixer.music.stop()
                        
                        # Start transition
                        self.transition_state = "speeding_up"
                        self.transition_timer = 0
                        self.starfield_speed = 1.0
                        self.countdown_timer = 360  # Reset countdown to 6 seconds (with 0.5s delay before countdown starts)
                        self.prev_countdown_text = None  # Reset to ensure sound plays for first countdown
                        self.snail.start()  # Start snail animation
                        print("Transition Started!")
            
            # Handle player movement with WASD keys
            if self.transition_state == "ready":
                self.player.handle_movement(keys, self.game_over)
                
                # Debug key: 'i' to kill all asteroids
                if keys[pygame.K_i]:
                    self.asteroids = []
                    print("Debug: All asteroids destroyed!")
                
                # Update game logic
                self.update_game()
                        
            # Handle transition states
            if self.transition_state == "speeding_up":
                # Speed up for 30 frames (0.5 seconds)
                self.transition_timer += 1
                
                # Update countdown timer
                if self.countdown_timer > 0:
                    self.countdown_timer -= 1
                
                if self.transition_timer < 30:
                    self.starfield_speed = 1.0 + (self.transition_timer / 30) * 9.0  # Speed up to 10x
                else:
                    self.transition_state = "fast"
                    self.transition_timer = 0
                    
            elif self.transition_state == "fast":
                # Stay fast for 270 frames (4.5 seconds) - extended to match countdown duration
                self.transition_timer += 1
                self.starfield_speed = 10.0
                
                # Update countdown timer
                if self.countdown_timer > 0:
                    self.countdown_timer -= 1
                
                # Start player 60 frames (1 second) earlier so it looks slower compared to starfield
                if self.transition_timer == 180 and not self.player.active:
                    self.player.start()
                    
                if self.transition_timer >= 270:
                    self.transition_state = "slowing_down"
                    self.transition_timer = 0
                    
            elif self.transition_state == "slowing_down":
                # Slow down over 60 frames (1 second)
                self.transition_timer += 1
                
                # Update countdown timer
                if self.countdown_timer > 0:
                    self.countdown_timer -= 1
                    
                if self.transition_timer < 60:
                    progress = self.transition_timer / 60
                    self.starfield_speed = 10.0 - (progress * 9.9)  # Slow from 10x to 0.1x
                else:
                    self.transition_state = "ready"
                    self.starfield_speed = 0.1  # Very slow speed - almost stand still
                    
                    # Start ingame music looping
                    if self.ingame_music_path:
                        try:
                            pygame.mixer.music.load(self.ingame_music_path)
                            pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                            print(f"Ingame music started looping: {self.ingame_music_path}")
                        except Exception as e:
                            print(f"Could not play ingame music: {e}")
                    
                    print("Ready for game logic!")
                    # Spawn asteroids when game starts (boss will spawn at score 1000)
                    self.spawn_asteroids()
                    self.boss.active = False  # Don't show boss yet
                    self.score = 0
                    self.game_over = False
                    self.boss_intro_shown = False
                    self.boss_intro_active = False
                    self.boss_intro_timer = 0
                    self.boss_flash_timer = 0
                    self.boss_music_played = False
                    self.boss_typed_text = ""
                    self.boss_typing_index = 0
                    self.boss_typing_timer = 0
                    self.boss_talking_sound_played = False
                    self.boss_talking_channel = None
                    self.pre_boss_text_active = False
                    self.pre_boss_typed_text = ""
                    self.pre_boss_typing_index = 0
                    self.pre_boss_typing_timer = 0
                    self.pre_boss_text_display_timer = 0
                    pygame.mixer.music.set_volume(1.0)  # Reset music volume
                    
                    # Reset player teleport charges
                    self.player.teleport_charges = [180, 180]  # Both fully charged
                        
            # Draw based on current state
            if state == "menu":
                self.draw_menu()
                # Draw asteroids, boss, and score if game is active
                if self.transition_state == "ready":
                    self.draw_asteroids()
                    # Only update/draw boss if it's active (score >= 1000)
                    if self.boss.active:
                        # Handle boss defeat sequence
                        if self.boss_defeated and self.boss_defeat_sequence:
                            self.handle_boss_defeat_sequence()
                            frozen = True
                        else:
                            frozen = False
                        
                        self.boss.update(is_talking=self.boss_intro_active, player=self.player, frozen=frozen)  # Pass whether boss is talking and if frozen
                        
                        # Handle boss drawing based on defeat sequence
                        if self.boss_defeated and self.boss_defeat_sequence == "dialogue":
                            self.boss.draw(self.screen, rotation=0, scale=1.0)
                            self.draw_boss_defeat_dialogue()
                        elif self.boss_defeated and self.boss_defeat_sequence == "spinning":
                            # Calculate shrink scale
                            shrink_progress = self.boss_defeat_timer / 120.0
                            scale = max(0.1, 1.0 - shrink_progress * 0.9)  # Shrink from 1.0 to 0.1
                            self.boss.draw(self.screen, rotation=self.boss_rotation, scale=scale)
                        elif self.boss_defeated and self.boss_defeat_sequence == "victory":
                            self.draw_victory_screen()
                        else:
                            self.boss.draw(self.screen)
                        
                        self.boss.draw_health_bar(self.screen)
                    self.draw_score()
                    # Draw player hearts
                    if self.player.active and self.player.phase == "centered":
                        self.player.draw_hearts(self.screen)
                        self.draw_teleport_charges()
                    # Draw pre-boss text if active
                    if self.pre_boss_text_active:
                        self.draw_pre_boss_text()
                    # Draw boss intro if active
                    if self.boss_intro_active:
                        self.draw_boss_intro()
                    if self.game_over:
                        self.draw_game_over()
            else:
                # Drawing game screen  
                self.screen.fill(BLACK)
                self.draw_starfield(self.starfield_speed)
                
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
