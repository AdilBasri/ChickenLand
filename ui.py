import pygame
from settings import *

# --- FONT YÜKLEME ---
try:
    # 'assets/font.ttf' dosyasını yüklemeye çalış
    # Boyutu biraz küçülttük (20) ki metin sığsın
    FONT_DIALOGUE = pygame.font.Font('assets/font.ttf', 20)
    FONT_SMALL = pygame.font.Font('assets/font.ttf', 16)
except FileNotFoundError:
    print("UYARI: assets/font.ttf bulunamadı, sistem fontu kullanılıyor.")
    FONT_DIALOGUE = pygame.font.SysFont('Arial', 24, bold=True)
    FONT_SMALL = pygame.font.SysFont('Arial', 20, bold=True)

def draw_prompt(screen, x, y):
    # E tuşu uyarısı
    text_surf = FONT_SMALL.render("KONUS (E)", True, (255, 255, 255))
    
    # Arka plan kutusu (Siyah, ince beyaz çerçeve)
    padding = 10
    bg_rect = pygame.Rect(0, 0, text_surf.get_width() + padding*2, text_surf.get_height() + padding*2)
    bg_rect.centerx = x
    bg_rect.bottom = y
    
    pygame.draw.rect(screen, (0, 0, 0), bg_rect) # Siyah Zemin
    pygame.draw.rect(screen, (255, 255, 255), bg_rect, 2) # Beyaz Çerçeve
    
    text_rect = text_surf.get_rect(center=bg_rect.center)
    screen.blit(text_surf, text_rect)

def draw_dialogue_box(screen, selected_option):
    # Kutu Boyutları
    box_width = 800
    box_height = 250
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = SCREEN_HEIGHT - box_height - 50 # Aşağıya yasla
    
    box_rect = pygame.Rect(box_x, box_y, box_width, box_height)

    # --- RETRO KUTU TASARIMI ---
    # 1. Ana Zemin (Koyu Gri/Siyah)
    pygame.draw.rect(screen, (20, 20, 20), box_rect)
    
    # 2. Kalın Beyaz Çerçeve
    pygame.draw.rect(screen, (240, 240, 240), box_rect, 4)
    
    # 3. İç İnce Siyah Çerçeve (Detay)
    inner_rect = box_rect.inflate(-8, -8)
    pygame.draw.rect(screen, (0, 0, 0), inner_rect, 2)

    # --- METİN ---
    lines = [
        "Sen de mi kayboldun kardeşim",
        "Buna inanamıyorum, köyden çok uzaktayız.",
        "Buradan kurtulmak için yardımlaşmalıyız.",
        "Lütfen beni de yanına al!"
    ]
    
    text_start_y = box_y + 30
    line_spacing = 35
    
    for i, line in enumerate(lines):
        text_surf = FONT_DIALOGUE.render(line, True, TEXT_COLOR)
        screen.blit(text_surf, (box_x + 40, text_start_y + i * line_spacing))

    # --- SEÇENEKLER ---
    opt_y = box_y + box_height - 50
    
    # Seçilen rengi ayarla
    yes_color = SELECTION_COLOR if selected_option == 0 else (150, 150, 150)
    no_color = SELECTION_COLOR if selected_option == 1 else (150, 150, 150)
    
    # Seçeneklerin başına ok işareti koymak (> EVET)
    prefix_yes = "> " if selected_option == 0 else "  "
    prefix_no = "> " if selected_option == 1 else "  "

    yes_text = FONT_DIALOGUE.render(prefix_yes + "TABI KI", True, yes_color)
    no_text = FONT_DIALOGUE.render(prefix_no + "HAYIR", True, no_color)
    
    screen.blit(yes_text, (box_x + 150, opt_y))
    screen.blit(no_text, (box_x + 500, opt_y))