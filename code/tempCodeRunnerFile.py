import pygame
from os.path import join
from random import randint, uniform

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400
        self.mask = pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        if game_over:
            return  # Stop player movement on game over
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites)) 
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center=(randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(midbottom=pos)

    def update(self, dt):
        if game_over:
            return  # Stop laser movement on game over
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups, speed_multiplier):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center=pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5), 1)
        self.speed = randint(400, 500)  # Slower speed than before, but still tough
        self.rotation_speed = randint(40, 80)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center=self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center=pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

def collisions():
    global game_over 

    # Check for player collisions with meteors
    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        global final_score
        final_score = pygame.time.get_ticks() // 1000  # Capture final score at the moment of collision
        game_over = True

    # Check for laser collisions with meteors and destroy only one meteor per laser
    for laser in laser_sprites:
        collided_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_meteors:
            laser.kill()  # Destroy the laser after collision
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)  # Explosion effect for meteor

def display_score():
    # Display current time, which is frozen after game over
    if game_over:
        text_surf = font.render(f"Time: {final_score} s", True, (240, 240, 240))  # Use the frozen score
    else:
        current_time = pygame.time.get_ticks() // 1000
        text_surf = font.render(f"Time: {current_time} s", True, (240, 240, 240))
    
    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)

def display_game_over():
    # Display "Game Over" message
    text_surf = font.render("Game Over", True, (255, 0, 0))
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    display_surface.blit(text_surf, text_rect)

    # Display final score (this score will not change)
    score_surf = font.render(f"Your Score: {final_score} s", True, (240, 240, 240))
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20))
    display_surface.blit(score_surf, score_rect)

    # Draw "End Game" button
    button_rect = pygame.Rect(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 100, 200, 50)
    pygame.draw.rect(display_surface, (255, 255, 255), button_rect)
    button_text = font.render("End Game", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    display_surface.blit(button_text, button_text_rect)

    return button_rect


# General setup 
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
running = True
clock = pygame.time.Clock()

font = pygame.font.Font(None, 40)

# Game variables
game_over = False
final_score = 0  # Initialize final score

# Import assets
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)

# Sprites 
all_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()

# Create player and stars
player = Player(all_sprites)
for _ in range(20):
    all_sprites.add(Star(all_sprites, star_surf))

# Main game loop
while True:
    dt = clock.tick(60) / 1000

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if game_over:
        button_rect = display_game_over()
        mouse_click = pygame.mouse.get_pressed()
        if mouse_click[0] and button_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.quit()
            exit()
    else:
        # Game logic
        all_sprites.update(dt)
        collisions()

        # Spawn fewer meteors but still maintain difficulty
        if randint(1, 17) == 1:  # Fewer meteors spawn, but still more often
            meteor_sprites.add(Meteor(meteor_surf, (randint(0, WINDOW_WIDTH), -50), all_sprites, 1))

        # Drawing
        display_surface.fill('#3a2e3f')
        all_sprites.draw(display_surface)
        display_score()

    pygame.display.update()
