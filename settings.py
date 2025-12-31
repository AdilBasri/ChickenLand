import pygame

# Ekran Ayarları
pygame.init()
INFO = pygame.display.Info()
# Varsayılan olarak Fullscreen başlasın ama değiştirilebilir olsun
SCREEN_WIDTH = INFO.current_w
SCREEN_HEIGHT = INFO.current_h
FPS = 60

# Fizik Ayarları
GRAVITY = 0.8
JUMP_STRENGTH = -16
MAX_SPEED = 8      # Hız biraz düşürüldü, daha kontrollü olsun
ACCELERATION = 0.6
FRICTION = 0.88
ANIMATION_SPEED = 100

# Ağ (Grapple) Ayarları
ROPE_LENGTH_MAX = 700   
ROPE_SPEED = 25         
SWING_FORCE = 1.2       
REEL_SPEED = 8          
ARROW_LENGTH = 80       

# Boyutlar
TILE_SIZE = 64
PLAYER_SCALE = 2.5
VISUAL_Y_OFFSET = 55 

# Renkler
SKY_BLUE = (135, 206, 250)
UI_BG_COLOR = (0, 0, 0, 200) # Biraz daha koyu
TEXT_COLOR = (255, 255, 255)
SELECTION_COLOR = (255, 215, 0)
TRANSITION_COLOR = (0, 0, 0)
ROPE_COLOR = (255, 255, 255)
ARROW_COLOR = (255, 50, 50) 

# OYUN DURUMLARI
STATE_MENU = 'menu'
STATE_MAP = 'map'
STATE_GAME = 'game'
STATE_SETTINGS = 'settings'

# GLOBAL AYARLAR DEPOSU
GAME_SETTINGS = {
    'fullscreen': True,
    'volume': 10, # 0-10 arası
    'language': 'TR',
    'controls': 'Standard'
}

# KONTROL ŞEMALARI (Local Co-op için)
CONTROLS = {
    'ARROWS': {
        'left': pygame.K_LEFT,
        'right': pygame.K_RIGHT,
        'up': pygame.K_UP,
        'down': pygame.K_DOWN,
        'jump': pygame.K_UP,
        'grapple': pygame.K_SPACE,
        'interact': pygame.K_p # P1 Etkileşim
    },
    'WASD': {
        'left': pygame.K_a,
        'right': pygame.K_d,
        'up': pygame.K_w,
        'down': pygame.K_s,
        'jump': pygame.K_w,
        'grapple': pygame.K_f, # P2 Ağ atma
        'interact': pygame.K_e # P2 Etkileşim
    }
}

# HARİTA AYARLARI
MAP_NODE_SIZE = 40
MAP_COLOR_LOCKED = (100, 100, 100)
MAP_COLOR_UNLOCKED = (255, 215, 0) 
MAP_COLOR_COMPLETED = (50, 200, 50)