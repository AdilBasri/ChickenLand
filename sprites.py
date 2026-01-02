import pygame
import math
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, tile_type):
        super().__init__()
        self.tile_type = tile_type
        try:
            if tile_type == 'grass': self.image = pygame.image.load('assets/grass.png').convert_alpha()
            elif tile_type == 'dirt': self.image = pygame.image.load('assets/dirt.png').convert_alpha()
            elif tile_type == 'box': self.image = pygame.image.load('assets/box.png').convert_alpha()
            elif tile_type == 'water':
                self.image = pygame.image.load('assets/water.png').convert_alpha()
                self.image.set_alpha(150)
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except FileNotFoundError:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((100, 100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            img = pygame.image.load('assets/flag.png').convert_alpha()
            self.image = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE*2))
        except FileNotFoundError:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE*2))
            self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect(bottomleft=(x, y + TILE_SIZE))

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class WebItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            img = pygame.image.load('assets/web.png').convert_alpha()
            self.image = pygame.transform.scale(img, (int(TILE_SIZE*0.8), int(TILE_SIZE*0.8)))
        except FileNotFoundError:
            self.image = pygame.Surface((32, 32))
            self.image.fill((200, 200, 255))
        self.rect = self.image.get_rect(center=(x + TILE_SIZE//2, y + TILE_SIZE//2))
        self.spawn_y = self.rect.y
        self.float_offset = 0
    
    def update(self):
        self.float_offset += 0.1
        self.rect.y = self.spawn_y + math.sin(self.float_offset) * 5

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class Particle(pygame.sprite.Sprite):
    def __init__(self, x, y, velocity, radius, color, life):
        super().__init__()
        self.radius = radius
        self.color = color
        self.velocity = list(velocity)
        self.life = life
        self.original_life = life
        self.image = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        self.life -= 1
        if self.life > 0:
            ratio = self.life / self.original_life
            new_size = int(self.radius * 2 * ratio)
            if new_size > 0:
                self.image = pygame.Surface((new_size, new_size), pygame.SRCALPHA)
                alpha = int(255 * ratio)
                color_with_alpha = (*self.color, alpha)
                pygame.draw.circle(self.image, color_with_alpha, (new_size//2, new_size//2), new_size//2)
        else: self.kill()

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class WaveGrass(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = []
        self.import_assets()
        self.frame_index = 0
        self.animation_speed = 0.15 
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(bottomleft=(x, y + 15))
        self.is_animating = False
        self.facing_right = True

    def import_assets(self):
        try:
            sheet = pygame.image.load('assets/wave.png').convert_alpha()
            frame_count = 5
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // frame_count
            for i in range(frame_count):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled_surface = pygame.transform.scale(surface, (TILE_SIZE, TILE_SIZE))
                self.frames.append(scaled_surface)
        except FileNotFoundError:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE//2))
            s.fill((200, 200, 50))
            self.frames = [s]

    def update(self, party):
        interacting_player = pygame.sprite.spritecollideany(self, party)
        if interacting_player and abs(interacting_player.velocity.x) > 0.1:
            self.is_animating = True
            if interacting_player.velocity.x > 0: self.facing_right = True
            elif interacting_player.velocity.x < 0: self.facing_right = False
        else:
            self.is_animating = False
            self.frame_index = 0
        self.animate()

    def animate(self):
        if self.is_animating:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(self.frames): self.frame_index = 0
        image = self.frames[int(self.frame_index)]
        if not self.facing_right: image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))