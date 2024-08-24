import pygame
import random
import os
import sys

WHITE = (255,255,255)
BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)

WIDTH = 800 #TODO modify to accomodate different window sizes
HEIGHT = 800 #TODO modify to accomodate different window sizes

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
    models = [os.path.join(get_player_dir(), fn) for fn in os.listdir(get_player_dir())]
    def __init__(self, max_health = PLAYER_MAX_HEALTH, health = PLAYER_MAX_HEALTH, 
                 rof = FIRE_RATE, projectile_count = PLAYER_PROJECTILES, pierce = PIERCE,
                 xp = XP, level = LEVEL, xp_thresh = XP_THRESH, xp_thresh_mult = XP_THRESH_MULT,
                 damage = BULLET_DAMAGE, speed = BULLET_SPEED, targeting = 0, spread = PROJECTILE_SPREAD, 
                 radius = PLAYER_RADIUS,font = None,screen = None,model=0, angle = 0):
        
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
        # self.mouse_aim = False
        # self.auto_aim = False
        self.spread = spread
        self.screen = screen
        self.model = model
        self.upgrade_choices = {"Increase Projectiles":self.increase_projectiles, "Increase Rate of Fire":self.increase_rof, 
                                  "Increase Damage":self.increase_damage, "Increase Pierce": self.increase_pierce, 
                                  "Increase Projectile Speed":self.increase_projectile_speed, "Enable Mouse Aiming":self.enable_mouse_aim,
                                  "Reduce Spread":self.reduce_spread}
        self.font = font
        self.radius = radius

    def take_damage(self, amount = 0):
        self.health -= amount

    def increase_damage(self, amount = 1):
        self.damage += amount

    def increase_pierce(self, amount = 1):
        self.pierce += amount
        if self.pierce >= MAX_PIERCE:
            del self.upgrade_choices['Increase Pierce']

    def increase_projectile_speed(self, amount = 1):
        self.projectile_speed += amount
        if self.projectile_speed >= MAX_SPEED:
            del self.upgrade_choices['Increase Projectile Speed']

    def enable_mouse_aim(self):
        self.targeting = 1
        del self.upgrade_choices['Enable Mouse Aiming']
        self.upgrade_choices["Enable Auto Aim"] = self.enable_auto_aim

    def enable_auto_aim(self):
        self.targeting = 2
        del self.upgrade_choices['Enable Auto Aim']

    def reduce_spread(self, amount = 1):
        self.spread += 1
        if self.spread >= MAX_SPREAD:
            del self.upgrade_choices['Reduce Spread']
    
    def increase_projectiles(self, amount = 1):
        self.projectile_count += amount
        if self.projectile_count >= MAX_PROJECTILES:
            del self.upgrade_choices['Increase Projectiles']

    def increase_rof(self, amount = 1):
        self.fire_rate -= amount  # Minimum fire rate is 2
        if self.fire_rate <= MAX_ROF:
            del self.upgrade_choices["Increase Rate of Fire"]
    
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

    # def draw_health(self):
    #     health_text = self.font.render(f'{self.health}', True, BLACK)
    #     self.screen.blit(health_text, (PLAYER_POS[0] - health_text.get_width() // 2, PLAYER_POS[1]-health_text.get_height() // 2))

    def draw_stats(self):
        targeting_sys = ['Random', 'Cursor', 'Auto']
        stats = [self.font.render(f'Level: {self.level}', True, WHITE),self.font.render(f'Projectiles: {self.projectile_count}', True, WHITE),
                 self.font.render(f'Damage: {self.damage}', True, WHITE),self.font.render(f'Fire Rate: {round(3600/self.fire_rate,2)}', True, WHITE),
                 self.font.render(f'Pierce: {self.pierce}', True, WHITE),self.font.render(f'Spread: {360 // self.spread}', True, WHITE),
                 self.font.render(f'Velocity: {self.projectile_speed}', True, WHITE),self.font.render(f'Targeting: {targeting_sys[self.targeting]}', True, WHITE)]
        
        top_margin = 10
        right_margin = 10

        text_height = stats[0].get_height()
        text_width = max([stat.get_width() for stat in stats])

        for i, text in enumerate(stats):
            self.screen.blit(text, (WIDTH-text_width-right_margin,top_margin+text_height*i))

    def gain_xp(self, amount):
        self.xp += amount
        if self.xp >= self.xp_thresh:
            self.level_up()

    def level_up(self): #TODO balance xp level requirements
        self.level += 1
        self.xp_thresh = self.xp_thresh + XP_THRESH_CONSTANT * self.level * self.xp_thresh_mult//2 # Increase threshold by CONSTANT for each level
        self.upgrade_screen()
        self.draw_stats()

    def upgrade_screen(self):
        # Present upgrade choices
        choices = sorted(random.sample(list(self.upgrade_choices.keys()),min(3,len(self.upgrade_choices.keys()))))
        if len(choices) == 1:
            self.upgrade_choices[choices[0]]()
            return

        self.screen.fill(BLACK)
        upgrade_text = self.font.render("Choose an upgrade:", True, WHITE)
        self.screen.blit(upgrade_text, (WIDTH // 2 - upgrade_text.get_width() // 2, HEIGHT // 2 - 100))
        
        for i, choice in enumerate(choices):
            choice_text = self.font.render(f'{i+1}: {choice}', True, WHITE)
            self.screen.blit(choice_text, (WIDTH // 2 - choice_text.get_width() // 2, HEIGHT // 2 + i * 30))
        self.draw_stats()
        
        pygame.display.flip()
        
        # Wait for player to choose an upgrade
        chosen = False

        keys = [pygame.K_1, pygame.K_2, pygame.K_3]

        key_choices = {key: i for i, key in enumerate(keys[:len(choices)])}

        while not chosen: 
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                    chosen = True
                elif event.type == pygame.KEYDOWN:
                    if event.key in key_choices:
                        self.upgrade_choices[choices[key_choices[event.key]]]()
                        chosen = True