import pygame
from settings import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y, variant='duck'):
        super().__init__()
        self.variant = variant
        self.frames = []
        
        # Hangi tür NPC ise onun görselini yükle
        try:
            if variant == 'duck':
                sheet = pygame.image.load('assets/duck_wolk.png').convert_alpha()
                frame_count = 2
                scale = 1.25
            elif variant == 'seagull':
                sheet = pygame.image.load('assets/seagull_wolk.png').convert_alpha()
                frame_count = 5
                scale = 2.5
            else:
                # Varsayılan
                sheet = pygame.image.load('assets/duck_wolk.png').convert_alpha()
                frame_count = 2
                scale = 1.25

            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // frame_count
            
            target_size = int(TILE_SIZE * scale)
            
            for i in range(frame_count):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled = pygame.transform.scale(surface, (target_size, target_size))
                # NPC oyuncuya baksın (Sola dönük)
                flipped = pygame.transform.flip(scaled, True, False)
                self.frames.append(flipped)
            
        except FileNotFoundError:
            s = pygame.Surface((TILE_SIZE, TILE_SIZE))
            s.fill((0, 255, 0)) # Yeşil Kutu
            self.frames = [s]

        self.frame_index = 0
        self.image = self.frames[0]
        # Yere basacak şekilde konumlandır
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE//2, y + TILE_SIZE))
        self.last_update = pygame.time.get_ticks()

    def animate(self):
        # NPC olduğu yerde beklerken hafif hareket etsin
        now = pygame.time.get_ticks()
        if now - self.last_update > 200: # Daha yavaş animasyon
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.image = self.frames[self.frame_index]

    def draw_scrolled(self, screen, scroll_x):
        self.animate()
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))
            
    def check_proximity(self, player_rect, scroll_x, screen, already_recruited):
        distance = abs(self.rect.centerx - player_rect.centerx)
        # Eğer bu bölümün karakteri zaten alındıysa konuşma balonu çıkmasın
        if distance < 150 and not already_recruited:
            return True
        return False

# Düşman (Köpek) - Değişiklik Yok
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = self.import_assets()
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(x, y + 20))
        self.velocity = pygame.math.Vector2(0, 0)
        self.speed = 3
        self.last_update = pygame.time.get_ticks()
        self.facing_left = True 

    def import_assets(self):
        try:
            sheet = pygame.image.load('assets/dog.png').convert_alpha()
            frames = []
            sheet_width = sheet.get_width()
            sheet_height = sheet.get_height()
            frame_width = sheet_width // 3 
            for i in range(3):
                surface = pygame.Surface((frame_width, sheet_height), pygame.SRCALPHA)
                surface.blit(sheet, (0, 0), (i * frame_width, 0, frame_width, sheet_height))
                scaled = pygame.transform.scale(surface, (int(TILE_SIZE * 1.5), int(TILE_SIZE * 1.5)))
                frames.append(scaled)
            return frames
        except FileNotFoundError:
            return [pygame.Surface((64,64)) for _ in range(3)]

    def ai_behavior(self, player):
        if abs(self.rect.y - player.rect.y) < 100:
            distance = player.rect.x - self.rect.x
            if abs(distance) < 800:
                if distance > 0:
                    self.velocity.x = self.speed
                    self.facing_left = False
                else:
                    self.velocity.x = -self.speed
                    self.facing_left = True 
            else:
                self.velocity.x = 0
        else:
            self.velocity.x = 0

    def update(self, tiles, player):
        self.ai_behavior(player)
        self.velocity.y += GRAVITY
        self.rect.x += self.velocity.x
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.x > 0: self.rect.right = tile.rect.left
                if self.velocity.x < 0: self.rect.left = tile.rect.right
        self.rect.y += self.velocity.y
        for tile in tiles:
            if self.rect.colliderect(tile.rect):
                if self.velocity.y > 0: 
                    self.rect.bottom = tile.rect.top
                    self.velocity.y = 0
                elif self.velocity.y < 0:
                    self.rect.top = tile.rect.bottom
                    self.velocity.y = 0
        self.animate()

    def animate(self):
        if self.velocity.x != 0:
            now = pygame.time.get_ticks()
            if now - self.last_update > ANIMATION_SPEED:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)    
        image = self.frames[self.frame_index]
        if not self.facing_left:
            image = pygame.transform.flip(image, True, False)
        self.image = image

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))