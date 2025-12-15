import pygame
from settings import *

# Fontlar
FONT_SMALL = pygame.font.SysFont('Arial', 24, bold=True)
FONT_DIALOGUE = pygame.font.SysFont('Arial', 28)

def draw_prompt(screen, x, y):
    prompt_surf = pygame.Surface((120, 40), pygame.SRCALPHA)
    prompt_surf.fill(UI_BG_COLOR)
    text_surf = FONT_SMALL.render("Press (E)", True, TEXT_COLOR)
    text_rect = text_surf.get_rect(center=(60, 20))
    prompt_surf.blit(text_surf, text_rect)
    prompt_rect = prompt_surf.get_rect(centerx=x, bottom=y)
    screen.blit(prompt_surf, prompt_rect)

def draw_dialogue_box(screen, selected_option):
    box_width, box_height = 800, 300
    box_x = (SCREEN_WIDTH - box_width) // 2
    box_y = (SCREEN_HEIGHT - box_height) // 2
    
    dialogue_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
    dialogue_surf.fill(UI_BG_COLOR)
    pygame.draw.rect(dialogue_surf, TEXT_COLOR, dialogue_surf.get_rect(), 3)

    lines = [
        "Sen de mi kayboldun?",
        "Buna inanamıyorum şimdi iki tavuk köyden bu kadar uzakta ne yapacağız?",
        "Geri dönmenin bir yolu olmalı.",
        "Yalvarırım beni de yanına al!"
    ]
    text_y = 30
    for line in lines:
        text = FONT_DIALOGUE.render(line, True, TEXT_COLOR)
        dialogue_surf.blit(text, (30, text_y))
        text_y += 35

    opt_y = box_height - 60
    yes_color = SELECTION_COLOR if selected_option == 0 else TEXT_COLOR
    no_color = SELECTION_COLOR if selected_option == 1 else TEXT_COLOR

    yes_text = FONT_DIALOGUE.render("EVET", True, yes_color)
    no_text = FONT_DIALOGUE.render("HAYIR", True, no_color)
    
    dialogue_surf.blit(yes_text, (250, opt_y))
    dialogue_surf.blit(no_text, (500, opt_y))

    screen.blit(dialogue_surf, (box_x, box_y))