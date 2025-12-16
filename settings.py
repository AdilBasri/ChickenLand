import pygame

# Ekran Ayarları
pygame.init()
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

# Ağ (Grapple) Ayarları
ROPE_LENGTH_MAX = 400   # Ağın uzayabileceği maksimum mesafe
ROPE_SPEED = 15         # Ağın fırlatılma hızı
SWING_FORCE = 0.8       # Sallanırken uygulanan kuvvet
ARROW_LENGTH = 60       # Nişan alma okunun uzunluğu

# Boyutlar
TILE_SIZE = 64
PLAYER_SCALE = 2.5
CHAR_WIDTH = 40
CHAR_HEIGHT = 60
VISUAL_Y_OFFSET = 55 

# Renkler
SKY_BLUE = (135, 206, 250)
UI_BG_COLOR = (0, 0, 0, 180)
TEXT_COLOR = (255, 255, 255)
SELECTION_COLOR = (255, 215, 0)
TRANSITION_COLOR = (0, 0, 0)
ROPE_COLOR = (255, 255, 255) # Beyaz İp
ARROW_COLOR = (255, 0, 0)    # Kırmızı Ok

# --- HARİTALAR --- (Level 4 aşağıda güncellendi)
# ... Diğer haritalar level_map.py dosyasında ...

# LEVEL 1: MARIO 1-1
LEVEL_1_MAP = [
    "                                                                                                                                                                                                                                                                                                                                ",
    "                                                                                                                                                                                                                                                                                                                                ",
    "                                                                                                                                                                                                                                                                                                                                ",
    "                              K K K                                                                                       KKK                                                                                                       ",
    "                              K K K                                                                                       K K                                                                                                       ",
    "                          KKKKKKKKKKKKK                                                                                  KKKKK                                                                                                      ",
    "                                                                                                                        KKKKKKK                                                                                                     ",
    "               K            K        K                                                                                 KKKKKKKKK                                                                                                    ",
    "              KKK          KKK       K                             K  K  K                                            KKKKKKKKKKK                                                                                                   ",
    "             KKKKK  K  K  K   K  K   KKKKK      K                    K  K  K                            XXXX           KKKKKKKKKKKKK                                                                                                  ",
    "            KKKKKKK K  K  K   K  K  KKKKKKK                          KKKKKKKKKKKK                       XX            KKKKKKKKKKKKKKK                                                                                                 ",
    " XXXXX  K  KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK  K  XX  K K  K  K   K XX  K K  K  K KKKKKKKKKKKKK   KK  K    K   K   K   K   K  K  K  K   K  K   K  XXX  K   XXX  KK   K   K  KXXXK   K  K  K  K  KKKKKKKKKKKKKKKKKK                    ",
    " XXXXX WKW KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK W  W XX  WWWWWWWWW W   XX   W TWW  W KKKKKKKKKKKK  T W   WT TW    WTTWWWW WTTWWWW TWWWW TTWWWW TWWW TXXXX  T   XX  WWWWWWWWWWWWWWWWWWWWWWWWWWWWWWWW  KKKKKKKKKKKKKKKKKKK F                  ",
    " XXXXX     KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK      XXX               XXX   D       KKKKKKKKKKKK                  XX                       XXXXX      XXX         D                           KKKKKKKKKKKKKKKKKKKKK   FFF                  ",
    " XXXXX     KKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKKK      XXX               XXX           KKKKKKKKKKKK        D         XX                      XXXXXX      XXX                                    KKKKKKKKKKKKKKKKKKKKKKK  FFFFF                  ",
    "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  WW WW  XXXXXXXXXXXXXXX  WW WW  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX  WW WW  XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXTTTTTTTXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX",
    "TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT  WW WW  TTTTTTTTTTTTTTT  WW WW  TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT  WW WW  TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT",
]

# LEVEL 2: DÜZLÜK VE ÖRDEK (NPC)
# 'N' harfi Duck NPC'sini temsil eder
LEVEL_2_MAP = [
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                      N                                                                                         ",
    " XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX                                                         ",
    " TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT                                                         ",
    " TTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTTT                                                         ",
]
# LEVEL 3: BİRLİKTE MÜCADELE (Co-op)
# Daha zorlu, düşmanlı ve sulu bir parkur.
LEVEL_3_MAP = [
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                                                                                                                                                ",
    "                                                                         K                                                                                                                      ",
    "                                                                        KKK                                                                                                                     ",
    "                  K                                                    KKKKK                                                        F                                                           ",
    "                 KKK        D                                         KKKKKKK                 D                                    FFF                                                          ",
    "                KKKKK      XXXX                                      KKKKKKKKK               XXXX                                 FFFFF                                                         ",
    "               KKKKKKK     TTTT                 K                   KKKKKKKKKKK              TTTT                                FFFFFFF                                                        ",
    " XX    D      KKKKKKKKK    TTTT                KKK                 KKKKKKKKKKKKK             TTTT          XX            XX     FFFFFFFFF                                                       ",
    " XX   XXXX   KKKKKKKKKKK   TTTT   W     W     KKKKK     W    W    KKKKKKKKKKKKKKK    W    W  TTTT   W      XX  W      W  XX    FFFFFFFFFFF                                                      ",
    " XX   TTTT  KKKKKKKKKKKKK  TTTT  WWW   WWW   KKKKKKK   WWW  WWW  KKKKKKKKKKKKKKKKK  WWW  WWW TTTT  WWW    XXXXWWW    WWWXXXX   TTTTTTTTTTT                                                      ",
    "XXXX  TTTT  TTTTTTTTTTTTT  TTTT  WWWWWWWWW  KKKKKKKKK  WWWWWWWW  TTTTTTTTTTTTTTTTT  WWWWWWWW TTTT  WWWW  XXXXXXWWWW  WWXXXXXX  TTTTTTTTTTT                                                      ",
    "TTTT  TTTT  TTTTTTTTTTTTT  TTTT  WWWWWWWWW  TTTTTTTTT  WWWWWWWW  TTTTTTTTTTTTTTTTT  WWWWWWWW TTTT  WWWW  TTTTTTWWWW  WWTTTTTT  TTTTTTTTTTT                                                      ",
    "TTTT  TTTT  TTTTTTTTTTTTT  TTTT  WWWWWWWWW  TTTTTTTTT  WWWWWWWW  TTTTTTTTTTTTTTTTT  WWWWWWWW TTTT  WWWW  TTTTTTWWWW  WWTTTTTT  TTTTTTTTTTT                                                      ",
    "TTTT  TTTT  TTTTTTTTTTTTT  TTTT  WWWWWWWWW  TTTTTTTTT  WWWWWWWW  TTTTTTTTTTTTTTTTT  WWWWWWWW TTTT  WWWW  TTTTTTWWWW  WWTTTTTT  TTTTTTTTTTT                                                      ",
    "TTTT  TTTT  TTTTTTTTTTTTT  TTTT  WWWWWWWWW  TTTTTTTTT  WWWWWWWW  TTTTTTTTTTTTTTTTT  WWWWWWWW TTTT  WWWW  TTTTTTWWWW  WWTTTTTT  TTTTTTTTTTT                                                      ",
]