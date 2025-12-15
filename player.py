import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, walk_path='assets/chicken.png', jump_path='assets/jump.png'):
        super().__init__()
        self.animations = {'walk': [], 'jump': []}
        
        # Varsayılan olarak Tavuk (6 Kare) yüklüyoruz
        self.import_character_assets(walk_path, jump_path)
        
        self.frame_index = 0
        self.status = 'walk'
        self.facing_right = True
        
        self.image = self.animations['walk'][self.frame_index]
        self.rect = pygame.Rect(x, y, CHAR_WIDTH, CHAR_HEIGHT)
        
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, 0)
        
        self.last_update = pygame.time.get_ticks()
        self.on_ground = False
        self.jump_count = 0 
        self.start_pos = (x, y)
        self.is_dead = False

    def import_character_assets(self, walk_path, jump_path):
        try:
            # Tavuk animasyonları 6 karedir
            walk_sheet = pygame.image.load(walk_path).convert_alpha()
            self.animations['walk'] = self.split_sheet(walk_sheet, 6) 
            
            jump_sheet = pygame.image.load(jump_path).convert_alpha()
            self.animations['jump'] = self.split_sheet(jump_sheet, 6)
        except FileNotFoundError:
            print(f"HATA: {walk_path} veya {jump_path} bulunamadı!")
            surface = pygame.Surface((TILE_SIZE, TILE_SIZE))
            surface.fill((255, 0, 255))
            self.animations['walk'] = [surface]
            self.animations['jump'] = [surface]

    def split_sheet(self, sheet, frame_count):
        frames = []
        sheet_width = sheet.get_width()
        sheet_height = sheet.get_height()
        frame_width = sheet_width // frame_count
        target_size = int(TILE_SIZE * PLAYER_SCALE)
        for i in range(frame_count):
            surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
            surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
            scaled_surface = pygame.transform.scale(surface, (target_size, target_size))
            frames.append(scaled_surface)
        return frames

    def get_input(self, game_state):
        if game_state != 'playing': 
            self.acceleration.x = 0
            return

        keys = pygame.key.get_pressed()
        self.acceleration.x = 0
        if keys[pygame.K_RIGHT]:
            self.acceleration.x = ACCELERATION
            self.facing_right = True
        elif keys[pygame.K_LEFT]:
            self.acceleration.x = -ACCELERATION
            self.facing_right = False

    def jump(self):
        if self.on_ground or self.jump_count < 2:
            self.velocity.y = JUMP_STRENGTH
            self.on_ground = False
            self.jump_count += 1

    def apply_gravity(self):
        self.acceleration.y = GRAVITY

    def physics_update(self):
        self.apply_gravity()
        self.velocity += self.acceleration
        self.velocity.x *= FRICTION
        if abs(self.velocity.x) > MAX_SPEED:
            self.velocity.x = MAX_SPEED * (1 if self.velocity.x > 0 else -1)
        if abs(self.velocity.x) < 0.1: self.velocity.x = 0

    def check_collisions(self, tiles, hazards):
        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
                self.velocity.x = 0
        self.rect.y += self.velocity.y
        self.on_ground = False
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.y > 0: 
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                    self.on_ground = True
                    self.jump_count = 0 
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0
        
        for hazard in hazards:
            if self.rect.inflate(-20, -20).colliderect(hazard.rect):
                self.is_dead = True
        if self.rect.y > 2000: # Düşme sınırı
            self.is_dead = True

    def animate(self):
        now = pygame.time.get_ticks()
        if not self.on_ground:
            self.status = 'jump'
            if now - self.last_update > ANIMATION_SPEED:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.animations['jump'])
        else:
            self.status = 'walk'
            if abs(self.velocity.x) > 0.5:
                if now - self.last_update > ANIMATION_SPEED:
                    self.last_update = now
                    self.frame_index = (self.frame_index + 1) % len(self.animations['walk'])
            else:
                pass 

        if self.frame_index >= len(self.animations[self.status]): self.frame_index = 0
        image = self.animations[self.status][self.frame_index]
        if not self.facing_right:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def update(self, tiles, hazards, game_state):
        self.get_input(game_state)
        self.physics_update()
        self.check_collisions(tiles, hazards)
        self.animate()

    def draw(self, screen, scroll_x):
        image_rect = self.image.get_rect()
        image_rect.centerx = self.rect.centerx - scroll_x
        image_rect.bottom = self.rect.bottom
        image_rect.y += VISUAL_Y_OFFSET
        screen.blit(self.image, image_rect)

# Companion için override
class Companion(Player):
    def __init__(self, x, y):
        # Companion chick1.png kullanıyor (6 kare)
        super().__init__(x, y, walk_path='assets/chick1.png', jump_path='assets/jump.png')
        self.target_player = None 

    def get_input(self, game_state):
        self.acceleration.x = 0
        if self.target_player and game_state == 'playing':
            distance = self.target_player.rect.centerx - self.rect.centerx
            if abs(distance) > 80: 
                if distance > 0:
                    self.acceleration.x = ACCELERATION
                    self.facing_right = True
                else:
                    self.acceleration.x = -ACCELERATION
                    self.facing_right = False
            if self.target_player.velocity.y < 0 and self.on_ground:
                 self.jump()