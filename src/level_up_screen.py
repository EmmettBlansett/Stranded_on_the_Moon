import pygame
import os
from constants import WIDTH,HEIGHT,WHITE,BLACK,YELLOW,GRAY

HOVER_COLOR = (0, 255, 0)

class LevelUpScreen:
    first_upgrade = True
    def __init__(self, options, screen, title_font, option_font, curr_stats, next_stats):
        # Calculate card positions
        self.screen = screen
        self.title_font = title_font
        self.option_font = option_font
        spacing = 50
        start_x = (WIDTH - (len(options) * 200 + (len(options) - 1) * spacing)) // 2
        self.cards = [UpgradeCard(self.screen,option, start_x + i * (200 + spacing), HEIGHT // 2 - 150, 
                                  self.option_font, curr_stats[i], next_stats[i]) for i, option in enumerate(options)]
        self.selected_option = None

        # Title
        title = self.title_font.render("LEVEL UP!", True, YELLOW)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

    def draw(self):
        # Draw cards
        for card in self.cards:
            card.draw(is_selected=(self.cards.index(card) == self.selected_option))

    def handle_mouse_hover(self, mouse_pos):
        for card in self.cards:
            card.check_hover(mouse_pos)

    def handle_mouse_click(self, mouse_pos):
        for i, card in enumerate(self.cards):
            if card.rect.collidepoint(mouse_pos):
                self.selected_option = i
                return i
        return -1
    
def get_icon_path(icon_fn = ''):
    prev_dir = os.path.dirname(os.path.dirname(__file__))
    icon_dir = os.path.join(prev_dir,'assets\\upgrade_icons')
    return os.path.join(icon_dir,icon_fn)
    
class UpgradeCard:
    upgrade_image_fn = {"Projectiles":get_icon_path('inc_proj.png'), "Fire Rate":get_icon_path('inc_rof.png'), 
                      "Damage":get_icon_path('inc_dmg.png'), "Pierce":get_icon_path('inc_prc.png'), 
                      "Velocity":get_icon_path('inc_spd.png'), "Manual Aiming":get_icon_path('crsr_tgt.png'),
                      "Auto Aiming":get_icon_path('auto_tgt.png'),"Reduce Spread":get_icon_path('rdc_sprd.png')}
    def __init__(self, screen, upgrade_name, x, y, font, old_stat, new_stat):
        self.old_stat = old_stat
        self.new_stat = new_stat
        self.option_font = font
        self.screen = screen
        self.upgrade_name = upgrade_name
        self.upgrade_image = pygame.transform.scale(pygame.image.load(UpgradeCard.upgrade_image_fn[upgrade_name]).convert_alpha(),(150,150))
        # self.image = pygame.Surface((150, 150))  # Placeholder image block
        # self.image.fill(GRAY)
        self.rect = pygame.Rect(x, y, 200, 300)
        self.is_hovered = False

    def draw(self, is_selected=False):
        border_color = HOVER_COLOR if self.is_hovered else (YELLOW if is_selected else WHITE)
        pygame.draw.rect(self.screen, border_color, self.rect.inflate(10, 10))  # Border with glow effect
        pygame.draw.rect(self.screen, BLACK, self.rect)  # Main card

        # Draw image
        self.screen.blit(self.upgrade_image, (self.rect.x + 25, self.rect.y + 30))

        # Draw upgrade name
        name_text = self.option_font.render(self.upgrade_name, True, WHITE)
        self.screen.blit(name_text, (self.rect.x + self.rect.width // 2 - name_text.get_width() // 2, self.rect.y + 200))

        # Draw upgrade details
        details_text = self.option_font.render(f'{self.old_stat} -> {self.new_stat}', True, WHITE)
        self.screen.blit(details_text, (self.rect.x + self.rect.width //2 - details_text.get_width() // 2, self.rect.y + 250))

    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)