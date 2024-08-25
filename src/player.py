import pygame
import random
import os
import sys
import time

from constants import WIDTH,HEIGHT,WHITE,BLACK,RED,GREEN,BLUE,YELLOW
from level_up_screen import LevelUpScreen

# WIDTH = 800 #TODO modify to accomodate different window sizes
# HEIGHT = 800 #TODO modify to accomodate different window sizes

CENTER_X = WIDTH//2
CENTER_Y = HEIGHT//2

# Player settings
PLAYER_RADIUS = 20
PLAYER_COLOR = WHITE
PLAYER_POS = (WIDTH // 2, HEIGHT // 2)
PLAYER_MAX_HEALTH = 100
PLAYER_HEALTH = PLAYER_MAX_HEALTH
PLAYER_PROJECTILES = 1
MAX_PROJECTILES = 16
PROJECTILE_SPREAD = 2
MAX_SPREAD = 18

BULLET_SPEED = 8
MAX_SPEED = 16
BULLET_DAMAGE = 1
PIERCE = 0
MAX_PIERCE = 6
FIRE_RATE = 30  # Higher = slower firing rate (frames per shot)
MAX_ROF = 2

XP = 0
LEVEL = 1
XP_THRESH = 10  # Initial XP threshold
XP_THRESH_CONSTANT = 20
XP_THRESH_MULT = 1

# font = pygame.font.SysFont(None, 24)

def get_player_dir():
    prev_dir = os.path.dirname(os.path.dirname(__file__))
    player_dir = os.path.join(prev_dir,'assets\\players')
    return player_dir

class Player:
    models = [pygame.image.load(os.path.join(get_player_dir(), fn)) for fn in os.listdir(get_player_dir())]
    def __init__(self, max_health = PLAYER_MAX_HEALTH, health = PLAYER_MAX_HEALTH, 
                 rof = FIRE_RATE, projectile_count = PLAYER_PROJECTILES, pierce = PIERCE,
                 xp = XP, level = LEVEL, xp_thresh = XP_THRESH, xp_thresh_mult = XP_THRESH_MULT,
                 damage = BULLET_DAMAGE, speed = BULLET_SPEED, targeting = 0, spread = PROJECTILE_SPREAD, 
                 radius = PLAYER_RADIUS, game_font = None, stat_font = None, screen = None,model=0, angle = 0):
        self.max_health = max_health
        self.health = health
        self.fire_rate = rof
        self.projectile_count = projectile_count
        self.xp = xp
        self.level = level
        self.xp_thresh = xp_thresh
        self.xp_thresh_mult = xp_thresh_mult
        self.damage = damage
        self.angle = angle
        self.pierce = pierce
        self.projectile_speed = speed
        self.targeting = targeting
        self.spread = spread
        self.screen = screen
        self.model = model
        self.upgrade_choices = {"Projectiles":self.increase_projectiles, "Fire Rate":self.increase_rof, 
                                  "Damage":self.increase_damage, "Pierce": self.increase_pierce, 
                                  "Velocity":self.increase_projectile_speed, "Manual Aiming":self.enable_mouse_aim,
                                  "Reduce Spread":self.reduce_spread}
        self.font = game_font
        self.stat_font = stat_font
        self.radius = radius
        self.maxxed = [False] * 8

    def get_stat(self,stat_name):
        match stat_name:
            case "Projectiles":
                return self.projectile_count
            case "Fire Rate":
                return 3600//(self.fire_rate)
            case "Damage":
                return self.damage
            case "Pierce":
                return self.pierce
            case "Velocity":
                return self.projectile_speed
            case "Manual Aiming":
                return "Random"
            case "Auto Aiming":
                return "Manual"
            case "Reduce Spread":
                return 360 // (self.spread)
    
    def get_stat_upgraded(self, stat_name):
        match stat_name:
            case "Projectiles":
                return self.projectile_count+1
            case "Fire Rate":
                return 3600//(self.fire_rate-1)
            case "Damage":
                return self.damage+1
            case "Pierce":
                return self.pierce+1
            case "Velocity":
                return self.projectile_speed+1
            case "Manual Aiming":
                return "Manual"
            case "Auto Aiming":
                return "Auto"
            case "Reduce Spread":
                return 360 // (self.spread+1)

    def take_damage(self, amount = 0):
        self.health -= amount

    def increase_damage(self, amount = 1):
        self.damage += amount

    def increase_pierce(self, amount = 1):
        self.pierce += amount
        if self.pierce >= MAX_PIERCE:
            self.maxxed[4] = True 
            del self.upgrade_choices['Pierce']

    def increase_projectile_speed(self, amount = 1):
        self.projectile_speed += amount
        if self.projectile_speed >= MAX_SPEED:
            self.maxxed[6] = True 
            del self.upgrade_choices['Velocity']

    def enable_mouse_aim(self):
        self.targeting = 1
        del self.upgrade_choices['Manual Aiming']
        self.upgrade_choices["Auto Aiming"] = self.enable_auto_aim

    def enable_auto_aim(self):
        self.targeting = 2
        self.maxxed[7] = True 
        del self.upgrade_choices['Auto Aiming']

    def reduce_spread(self, amount = 1):
        self.spread += 1
        if self.spread >= MAX_SPREAD:
            self.maxxed[5] = True 
            del self.upgrade_choices['Reduce Spread']
    
    def increase_projectiles(self, amount = 1):
        self.projectile_count += amount
        if self.projectile_count >= MAX_PROJECTILES:
            self.maxxed[1] = True 
            del self.upgrade_choices['Projectiles']

    def increase_rof(self, amount = 1):
        self.fire_rate -= amount  # Minimum fire rate is 2
        if self.fire_rate <= MAX_ROF:
            self.maxxed[3] = True 
            del self.upgrade_choices["Fire Rate"]
    
    def heal(self, amount):
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)
    
    def draw(self,screen):
        screen.blit(Player.models[self.model],(CENTER_X-PLAYER_RADIUS,CENTER_Y-PLAYER_RADIUS))
        # self.draw_health(screen, CENTER_X, CENTER_Y)
        # pygame.draw.circle(self.screen, PLAYER_COLOR, (PLAYER_POS[0], PLAYER_POS[1]), self.radius)
        self.draw_health(screen)

    def draw_health(self,screen):
        health_bar_width = PLAYER_RADIUS*2
        green_width = int(health_bar_width*(self.health/self.max_health))
        red_width = health_bar_width - green_width
        pygame.draw.rect(screen, GREEN, pygame.Rect(CENTER_X-health_bar_width//2, CENTER_Y-PLAYER_RADIUS-5, green_width,4))
        pygame.draw.rect(screen, RED, pygame.Rect(CENTER_X-health_bar_width//2+green_width, CENTER_Y-PLAYER_RADIUS-5, red_width,4))

    def draw_stats(self):
        targeting_sys = ['Random', 'Manual', 'Auto']
        stat_text = [f'Level: {self.level}',f'Projectiles: {self.projectile_count}',
                     f'Damage: {self.damage}',f'Fire Rate: {3600//self.fire_rate}',
                     f'Pierce: {self.pierce}',f'Spread: {360 // self.spread}',
                     f'Velocity: {self.projectile_speed}',f'Targeting: {targeting_sys[self.targeting]}']
        max_text = [self.stat_font.render('(MAX) '*self.maxxed[i], True, GREEN) for i in range(len(stat_text))]

        stats = [self.stat_font.render(stat_text[i], True, WHITE) for i in range(len(stat_text))]
        
        top_margin = 10
        right_margin = 10

        text_height = stats[0].get_height()
        text_width = max([stat.get_width() for stat in stats])

        for i, text in enumerate(stats):
            self.screen.blit(text, (WIDTH-text_width-right_margin,top_margin+text_height*i))
            self.screen.blit(max_text[i], (WIDTH-text_width-max_text[i].get_width()-right_margin,top_margin+text_height*i))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_thresh:
            self.level_up()

    def level_up(self): #TODO balance xp level requirements
        self.level += 1
        self.xp_thresh = self.xp_thresh + XP_THRESH_CONSTANT * self.level * self.xp_thresh_mult//2 # Increase threshold by CONSTANT for each level
        self.upgrade_screen()

    def upgrade_screen(self):
        # Present upgrade choices
        choices = sorted(random.sample(list(self.upgrade_choices.keys()),min(3,len(self.upgrade_choices.keys()))))
        if len(choices) == 1:
            title = self.font.render("LEVEL UP!", True, YELLOW)
            self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, CENTER_Y-PLAYER_RADIUS-20))
            self.upgrade_choices[choices[0]]()
            pygame.display.flip()
            return
        
        # Wait for player to choose an upgrade
        chosen = False

        upgrade_funcs = {i: self.upgrade_choices[upgrade] for i, upgrade in enumerate(choices)}
        curr_stats = [self.get_stat(choice) for choice in choices]
        next_stats = [self.get_stat_upgraded(choice) for choice in choices]
        level_screen=LevelUpScreen(choices,self.screen,self.font,self.font,curr_stats,next_stats)

        while not chosen: 
            mouse_pos = pygame.mouse.get_pos()
            level_screen.handle_mouse_hover(mouse_pos)
            # Handle showing stats while in upgrade screen
            if pygame.key.get_pressed()[pygame.K_TAB]:
                self.screen.fill(BLACK,(WIDTH-200,0,200,150))
                self.draw_stats()
            else:
                self.screen.fill(BLACK,(WIDTH-200,0,200,150))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    chosen = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        selected_upgrade = level_screen.handle_mouse_click(mouse_pos)
                        if selected_upgrade>-1:
                            upgrade_funcs[selected_upgrade]()
                            chosen = True
                            break
            level_screen.draw()
            pygame.display.flip()
            time.sleep(1/60)

