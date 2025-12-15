import pygame

# Ekran Ayarları
pygame.init()
# Tam ekran boyutunu dinamik alıyoruz
INFO = pygame.display.Info()
SCREEN_WIDTH = INFO.current_w
SCREEN_HEIGHT = INFO.current_h
FPS = 60

# Fizik Ayarları
GRAVITY = 0.8
JUMP_STRENGTH = -15
MAX_SPEED = 10
ACCELERATION = 0.5
FRICTION = 0.88
ANIMATION_SPEED = 100

# Boyutlar
TILE_SIZE = 64
PLAYER_SCALE = 2.5
CHAR_WIDTH = 40
CHAR_HEIGHT = 60
VISUAL_Y_OFFSET = 55  # Görselin yere basması için ayar

# Renkler
SKY_BLUE = (135, 206, 250)
UI_BG_COLOR = (0, 0, 0, 180)
TEXT_COLOR = (255, 255, 255)
SELECTION_COLOR = (255, 215, 0)