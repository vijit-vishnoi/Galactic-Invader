import pygame
from os.path import join
from random import randint, uniform

pygame.init()

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

clock = pygame.time.Clock()

explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

game_over = False
final_score = 0

font = pygame.font.Font(None, 40)

star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.5)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
game_music = pygame.mixer.Sound(join('audio', 'game_music.wav'))
game_music.set_volume(0.4)

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
            return
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
            return
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
        self.speed = randint(400, 500)
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

    if pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask):
        global final_score
        final_score = pygame.time.get_ticks() // 1000
        game_over = True

    for laser in laser_sprites:
        collided_meteors = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_meteors:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)

def display_score():
    if game_over:
        text_surf = font.render(f"Score: {final_score} ", True, (240, 240, 240))
    else:
        current_time = pygame.time.get_ticks() // 1000
        text_surf = font.render(f"Score: {current_time} ", True, (240, 240, 240))

    text_rect = text_surf.get_rect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT -50))

    padding = 20
    text_rect.inflate_ip(padding, padding)

    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)

def display_game_over():
    text_surf = font.render("Game Over", True, (255, 0, 0))
    text_rect = text_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 - 50))
    display_surface.blit(text_surf, text_rect)

    score_surf = font.render(f"Your Score: {final_score} ", True, (240, 240, 240))
    score_rect = score_surf.get_rect(center=(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2 + 20))
    display_surface.blit(score_surf, score_rect)

    button_rect = pygame.Rect(WINDOW_WIDTH / 2 - 100, WINDOW_HEIGHT / 2 + 100, 200, 50)
    pygame.draw.rect(display_surface, (255, 255, 255), button_rect)
    button_text = font.render("End Game", True, (0, 0, 0))
    button_text_rect = button_text.get_rect(center=button_rect.center)
    display_surface.blit(button_text, button_text_rect)

    return button_rect


all_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()

player = Player(all_sprites)
for _ in range(20):
    all_sprites.add(Star(all_sprites, star_surf))

while True:
    dt = clock.tick(60) / 1000

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
        all_sprites.update(dt)
        collisions()

        if randint(1, 17) == 1:
            meteor_sprites.add(Meteor(meteor_surf, (randint(0, WINDOW_WIDTH), -50), all_sprites, 1))

        display_surface.fill('#3a2e3f')
        all_sprites.draw(display_surface)
        display_score()

    pygame.display.update()
