import pygame
import math  # EKLENDİ: Bu eksikti
from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.type = type
        if type == 'grass': self.image = pygame.image.load('assets/grass.png').convert_alpha()
        elif type == 'dirt': self.image = pygame.image.load('assets/dirt.png').convert_alpha()
        elif type == 'box': self.image = pygame.image.load('assets/box.png').convert_alpha()
        elif type == 'water':
            self.image = pygame.image.load('assets/water.png').convert_alpha()
            self.image.set_alpha(200)

        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load('assets/flag.png').convert_alpha()
        except:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0))
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))

class WebItem(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            img = pygame.image.load('assets/web.png').convert_alpha()
            self.image = pygame.transform.scale(img, (40, 40)) # Biraz küçük olsun
        except:
            self.image = pygame.Surface((40, 40))
            self.image.fill((200, 200, 200)) # Gri Kutu
            
        # Kutunun üzerinde dursun diye biraz offset
        self.rect = self.image.get_rect(center=(x + TILE_SIZE//2, y + TILE_SIZE//2))
        
        # Animasyon için (havada süzülme efekti)
        self.start_y = self.rect.y
        self.timer = 0

    def update(self):
        self.timer += 0.1
        # math kütüphanesi eklendiği için artık çalışır
        self.rect.y = self.start_y + math.sin(self.timer) * 5

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))