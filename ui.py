import pygame
import math
import os
from settings import *

# --- YARDIMCI FONKSİYONLAR ---
def draw_prompt(screen, x, y):
    prompt_rect = pygame.Rect(x - 20, y - 40, 40, 40)
    pygame.draw.rect(screen, (255, 255, 255), prompt_rect, border_radius=5)
    pygame.draw.rect(screen, (0, 0, 0), prompt_rect, 2, border_radius=5)
    font = pygame.font.SysFont("Arial", 24, bold=True)
    text_surf = font.render("E", True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=prompt_rect.center)
    screen.blit(text_surf, text_rect)

def draw_dialogue_box(screen, selected_option):
    box_rect = pygame.Rect(50, SCREEN_HEIGHT - 150, SCREEN_WIDTH - 100, 130)
    pygame.draw.rect(screen, UI_BG_COLOR, box_rect, border_radius=10)
    pygame.draw.rect(screen, (255, 255, 255), box_rect, 2, border_radius=10)
    
    font = pygame.font.SysFont("Arial", 20)
    title = font.render("EKİBE KATILMAK İSTİYOR!", True, SELECTION_COLOR)
    screen.blit(title, (box_rect.x + 20, box_rect.y + 20))
    desc = font.render("Bu karakteri partiye dahil etmek ister misin?", True, TEXT_COLOR)
    screen.blit(desc, (box_rect.x + 20, box_rect.y + 50))
    
    opt1_color = SELECTION_COLOR if selected_option == 0 else TEXT_COLOR
    opt2_color = SELECTION_COLOR if selected_option == 1 else TEXT_COLOR
    txt1 = font.render("> EVET (Partiye Ekle)", True, opt1_color)
    txt2 = font.render("> HAYIR (Sonra Belki)", True, opt2_color)
    screen.blit(txt1, (box_rect.x + 50, box_rect.y + 90))
    screen.blit(txt2, (box_rect.x + 300, box_rect.y + 90))

# --- ANA MENÜ ---
class MainMenu:
    def __init__(self):
        self.options = ["YENI OYUN", "AYARLAR", "CIKIS"]
        self.selected_index = 0
        self.font = pygame.font.SysFont("Arial", 40, bold=True)
        self.title_font = pygame.font.SysFont("Arial", 80, bold=True)
        
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                return self.options[self.selected_index]
        return None

    def draw(self, screen):
        screen.fill((20, 20, 40)) 
        title_surf = self.title_font.render("CHICKEN LAND", True, (255, 215, 0))
        title_rect = title_surf.get_rect(center=(SCREEN_WIDTH//2, 150))
        screen.blit(title_surf, title_rect)
        for i, option in enumerate(self.options):
            color = (255, 255, 255)
            prefix = ""
            if i == self.selected_index:
                color = (255, 215, 0)
                prefix = "> "
            text_surf = self.font.render(prefix + option, True, color)
            text_rect = text_surf.get_rect(center=(SCREEN_WIDTH//2, 350 + i * 60))
            screen.blit(text_surf, text_rect)

# --- DÜNYA HARİTASI (WINDOWS DÜZELTMELİ) ---
class WorldMap:
    def __init__(self):
        # 1. DOSYA BULMA (Windows uyumluluğu için)
        possible_files = ['assets/map.jpg', 'assets/map.png', 'assets/map.jpeg', 'map.jpg', 'map.png']
        original_img = None
        
        print("--- HARİTA YÜKLENİYOR ---")
        for f in possible_files:
            if os.path.exists(f):
                try:
                    original_img = pygame.image.load(f).convert()
                    print(f"BAŞARILI: '{f}' bulundu ve yüklendi.")
                    print(f"Orijinal Boyut: {original_img.get_width()}x{original_img.get_height()}")
                    break
                except:
                    continue
        
        if original_img:
            # 2. DOĞRU ÖLÇEKLEME (Yüksekliğe Göre)
            # Haritanın boyunu ekran boyuna (1080) eşitle, enini orantılı ayarla.
            target_height = SCREEN_HEIGHT
            original_w = original_img.get_width()
            original_h = original_img.get_height()
            
            aspect_ratio = original_w / original_h
            target_width = int(target_height * aspect_ratio)
            
            # Kaliteli küçültme/büyütme
            self.image = pygame.transform.smoothscale(original_img, (target_width, target_height))
        else:
            # HATA DURUMU (Yedek yeşil ekran)
            print("HATA: Harita dosyası bulunamadı! 'assets' klasörünü kontrol et.")
            self.image = pygame.Surface((3000, SCREEN_HEIGHT))
            self.image.fill((100, 100, 50))
            pygame.draw.line(self.image, (200, 50, 50), (0, 500), (3000, 500), 10)

        self.map_width = self.image.get_width()
        self.map_height = self.image.get_height()
        
        # 3. KAMERA
        self.scroll_x = 0
        self.target_scroll_x = 0
        self.is_dragging = False
        self.last_mouse_x = 0
        
        # 4. BÖLÜM NOKTALARI (YÜZDELİK SİSTEM)
        # Haritanın solundan sağına yüzdelik konumlara göre yerleştiriyoruz.
        # Bu sayede harita boyutu ne olursa olsun noktalar kaymaz.
        # [X_Oranı, Y_Oranı] -> (0.10 demek %10 genişlikte demek)
        
        self.node_positions_pct = [
            {'id': 1, 'pct': (0.08, 0.75), 'info': 'Wasteland', 'reward': ''},         # Sol Alt (Kurukafa)
            {'id': 2, 'pct': (0.28, 0.55), 'info': 'Kemik Vadisi', 'reward': '+1 Duck'}, # Kanyon Ortası
            {'id': 3, 'pct': (0.48, 0.45), 'info': 'Sinir Kapisi', 'reward': ''},       # Yeşil Geçiş
            {'id': 4, 'pct': (0.68, 0.65), 'info': 'Marti Koprusu', 'reward': '+1 Seagull'}, # Nehir
            {'id': 5, 'pct': (0.82, 0.50), 'info': 'Tavuk Koyu', 'reward': ''},         # Köy
            {'id': 6, 'pct': (0.95, 0.35), 'info': 'Kraliyet Kalesi', 'reward': '+1 Twi'}, # Kale
        ]
        
        self.nodes = []
        for n in self.node_positions_pct:
            # Yüzdeleri gerçek piksel koordinatına çevir
            real_x = int(self.map_width * n['pct'][0])
            real_y = int(self.map_height * n['pct'][1])
            
            self.nodes.append({
                'id': n['id'],
                'pos': (real_x, real_y),
                'status': 'locked', # Varsayılan kilitli
                'info': n['info'],
                'reward': n['reward']
            })
            
        # İlk bölüm her zaman açık
        self.nodes[0]['status'] = 'unlocked'
            
        self.current_selection = 0 
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.info_font = pygame.font.SysFont("Arial", 24, bold=True)

    def unlock_next_level(self, completed_level_id):
        if 0 <= completed_level_id - 1 < len(self.nodes):
            self.nodes[completed_level_id - 1]['status'] = 'completed'
            if completed_level_id < len(self.nodes):
                self.nodes[completed_level_id]['status'] = 'unlocked'
                self.current_selection = completed_level_id 
                self.focus_on_node(self.current_selection)

    def focus_on_node(self, node_index):
        node_x = self.nodes[node_index]['pos'][0]
        self.target_scroll_x = node_x - (SCREEN_WIDTH // 2)
        # Clamp (Sınırla)
        max_scroll = self.map_width - SCREEN_WIDTH
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))

    def handle_input(self, event):
        mouse_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                self.is_dragging = True
                self.last_mouse_x = mouse_pos[0]
                
                # Tıklama kontrolü
                for node in self.nodes:
                    screen_x = node['pos'][0] - self.scroll_x
                    screen_y = node['pos'][1]
                    dist = math.sqrt((mouse_pos[0] - screen_x)**2 + (mouse_pos[1] - screen_y)**2)
                    if dist < 40:
                        if node['status'] != 'locked':
                            return node['id']

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                dx = mouse_pos[0] - self.last_mouse_x
                self.target_scroll_x -= dx 
                self.last_mouse_x = mouse_pos[0]
                self.scroll_x = self.target_scroll_x 

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                if self.current_selection < len(self.nodes) - 1:
                    if self.nodes[self.current_selection + 1]['status'] != 'locked':
                        self.current_selection += 1
                        self.focus_on_node(self.current_selection)
            elif event.key == pygame.K_LEFT:
                if self.current_selection > 0:
                    self.current_selection -= 1
                    self.focus_on_node(self.current_selection)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                node = self.nodes[self.current_selection]
                if node['status'] != 'locked':
                    return node['id']
        
        return None

    def draw(self, screen):
        max_scroll = self.map_width - SCREEN_WIDTH
        if max_scroll < 0: max_scroll = 0
        
        self.target_scroll_x = max(0, min(self.target_scroll_x, max_scroll))
        self.scroll_x += (self.target_scroll_x - self.scroll_x) * 0.1
        
        # Haritayı Çiz
        screen.blit(self.image, (-self.scroll_x, 0))
        
        # Yolları Çiz
        if len(self.nodes) > 1:
            adjusted_points = [(n['pos'][0] - self.scroll_x, n['pos'][1]) for n in self.nodes]
            # Koyu kahverengi, biraz saydamlık efekti için çizgiyi iki kere çizebiliriz ama şimdilik düz.
            pygame.draw.lines(screen, (60, 40, 20), False, adjusted_points, 8)

        # Noktaları Çiz
        for i, node in enumerate(self.nodes):
            screen_x = node['pos'][0] - self.scroll_x
            screen_y = node['pos'][1]
            
            # Sadece ekrandakileri çiz
            if -50 < screen_x < SCREEN_WIDTH + 50:
                color = MAP_COLOR_LOCKED
                if node['status'] == 'unlocked': color = MAP_COLOR_UNLOCKED
                elif node['status'] == 'completed': color = MAP_COLOR_COMPLETED
                
                scale = 1.0
                mouse_pos = pygame.mouse.get_pos()
                dist = math.sqrt((mouse_pos[0] - screen_x)**2 + (mouse_pos[1] - screen_y)**2)
                
                if i == self.current_selection or dist < 40:
                    scale = 1.3
                    pygame.draw.circle(screen, (255, 255, 255), (screen_x, screen_y), (MAP_NODE_SIZE//2 * scale) + 4, 3)

                pygame.draw.circle(screen, color, (screen_x, screen_y), int(MAP_NODE_SIZE//2 * scale))
                
                text = self.font.render(str(node['id']), True, (255, 255, 255))
                text_rect = text.get_rect(center=(screen_x, screen_y))
                screen.blit(text, text_rect)
                
                if node['status'] == 'completed':
                    offset = 10 * scale
                    pygame.draw.line(screen, (200, 0, 0), (screen_x - offset, screen_y - offset), (screen_x + offset, screen_y + offset), 4)
                    pygame.draw.line(screen, (200, 0, 0), (screen_x + offset, screen_y - offset), (screen_x - offset, screen_y + offset), 4)

                if i == self.current_selection or dist < 40:
                    info_text = f"BOLUM {node['id']}: {node['info']}"
                    if node['reward']: info_text += f" ({node['reward']})"
                    
                    info_surf = self.info_font.render(info_text, True, (255, 255, 255))
                    bg_rect = info_surf.get_rect(midbottom=(screen_x, screen_y - 40))
                    bg_rect.inflate_ip(20, 10)
                    
                    s = pygame.Surface((bg_rect.width, bg_rect.height))
                    s.set_alpha(200)
                    s.fill((0,0,0))
                    screen.blit(s, bg_rect.topleft)
                    screen.blit(info_surf, (bg_rect.x + 10, bg_rect.y + 5))