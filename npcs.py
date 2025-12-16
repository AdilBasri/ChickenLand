import pygame
from settings import *

class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # ARTIK DUCK GÖRSELİ KULLANIYORUZ
        # duck_wolk.png 2 kareden oluşuyor, ilk karesini alıp durma pozu yapacağız.
        try:
            sheet = pygame.image.load('assets/duck_wolk.png').convert_alpha()
            frame_width = sheet.get_width() // 2 # 2 Kare olduğu için 2'ye bölüyoruz
            
            surface = pygame.Surface((frame_width, sheet.get_height()), pygame.SRCALPHA)
            surface.blit(sheet, (0, 0), (0, 0, frame_width, sheet.get_height()))
            
            # Ördek Scale (1.25) uyguluyoruz ki oynadığımız ördekle aynı boyda olsun
            target_size = int(TILE_SIZE * 1.25)
            self.image = pygame.transform.scale(surface, (target_size, target_size))
            
            # NPC genelde sola baksın (Oyuncu sağdan geliyor)
            # duck_wolk sağa bakıyorsa flip gerekebilir, genelde sağa bakar.
            # Oyuncu sağdan geldiği için NPC sola dönük olsun:
            self.image = pygame.transform.flip(self.image, True, False) 
            
        except FileNotFoundError:
            # Görsel yoksa hata vermesin, kırmızı kare
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((255, 0, 0))

        # Konumlandırma (Yere tam basması için offset ayarı yok, direkt hitboxtan)
        self.rect = self.image.get_rect(midbottom=(x + TILE_SIZE//2, y + TILE_SIZE))

    def draw_scrolled(self, screen, scroll_x):
        if -TILE_SIZE < self.rect.x - scroll_x < SCREEN_WIDTH:
            screen.blit(self.image, (self.rect.x - scroll_x, self.rect.y))
            
    def check_proximity(self, player_rect, scroll_x, screen, companion_active):
        # Yoldaş zaten alındıysa (companion_active = True) artık E çıkmasın
        distance = abs(self.rect.centerx - player_rect.centerx)
        if distance < 150 and not companion_active:
            return True
        return False

# Düşman (Köpek) - (Değişiklik Yok, aynen korundu)
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