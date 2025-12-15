import pygame
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