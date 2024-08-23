import random
import math
import pygame
import os

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)
BLACK = (0,0,0)


ENEMY_HEALTH = 1  # Base health of each enemy
ENEMY_HEALTH_MULTIPLIER = 1  # Multiplies health every 30 seconds
ENEMY_SPIRALS = 6  # Number of spirals before player is reached
ENEMY_SPEED = 0.02  # Radians per frame
SPIRAL_SPEED = ENEMY_SPEED * ENEMY_SPIRALS  # How quickly they spiral inward
ENEMY_COLOR = WHITE
ENEMY_SIZE = 36

CENTER_X = 400 #TODO modify to accomodate different window sizes
CENTER_Y = 400 #TODO modify to accomodate different window sizes

# ENEMY_TYPES = [pygame.image.load(os.path.join(CWD,'assets\\enemies\\enemy')).convert_alpha() for enemy in os.listdir('assets\\enemies')]

# pygame.init()

def get_position_on_spiral(center_x, center_y, radius, angle):
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    return x, y

def get_enemies_dir():
    prev_dir = os.path.dirname(os.path.dirname(__file__))
    enemy_dir = os.path.join(prev_dir,'assets\\enemies')
    return enemy_dir

class Enemy:
    enemy_types = [os.path.join(get_enemies_dir(), enemy) for enemy in os.listdir(get_enemies_dir())]
    def __init__(self, angle, radius, health = ENEMY_HEALTH * ENEMY_HEALTH_MULTIPLIER, speed = ENEMY_SPEED, spiral_speed = SPIRAL_SPEED, color = ENEMY_COLOR):
        self.angle = angle
        self.radius = radius
        self.max_health = health
        self.health = self.max_health
        self.speed = speed
        self.spiral_speed = spiral_speed
        self.value = self.max_health
        self.color = color
        self.collisions = set()
        self.rand = random.random()
        self.model = 0
        self.x, self.y = get_position_on_spiral(CENTER_X, CENTER_Y, self.radius, self.angle)
        self.apply_effect()
    
    def apply_effect(self):
        if self.rand < .1:
            # self.color = GREEN
            self.model = 2
            self.value*=10
        elif self.rand < .2:
            # self.color = RED
            self.model = 1
            self.speed*= 2
            self.spiral_speed = self.speed * ENEMY_SPIRALS
        elif self.rand > .9:
            # self.color = BLUE
            self.model = 3
            self.max_health *= 2
            self.health = self.max_health
            self.value = self.health
            self.speed/=2
            self.spiral_speed = self.speed * ENEMY_SPIRALS
    
    def move(self):
        self.angle += self.speed
        self.radius -= self.spiral_speed
        if self.angle >= 2*math.pi:
            self.angle -= 2*math.pi
        self.x, self.y = get_position_on_spiral(CENTER_X, CENTER_Y, self.radius, self.angle)
    
    def draw(self, screen):
        # pygame.draw.circle(screen, self.color, (self.x, self.y), ENEMY_SIZE//2)
        screen.blit(Enemy.enemy_types[self.model],(self.x-ENEMY_SIZE//2,self.y-ENEMY_SIZE//2))
        self.draw_health(screen, self.x, self.y)

    def draw_health(self, screen, x, y):
        # health_text = font.render(str(self.health), True, BLACK)
        # screen.blit(health_text, (x - health_text.get_width() // 2, y - health_text.get_height() // 2))
        health_bar_width = ENEMY_SIZE
        green_width = int(health_bar_width*(self.health/self.max_health))
        red_width = health_bar_width - green_width
        pygame.draw.rect(screen, GREEN, pygame.Rect(self.x-health_bar_width//2, self.y-ENEMY_SIZE//2-5, green_width,4))
        pygame.draw.rect(screen, RED, pygame.Rect(self.x-health_bar_width//2+green_width, self.y-ENEMY_SIZE//2-5, red_width,4))

    def check_collision(self, bullet):
        distance = math.hypot(bullet.x - self.x, bullet.y - self.y)
        return distance < ENEMY_SIZE // 2 + bullet.size and bullet.num not in self.collisions

    def add_collision(self, bullet_num):
        self.collisions.add(bullet_num)

    def check_player_collision(self, player_radius):
        distance = math.hypot(self.x - CENTER_X, self.y - CENTER_Y)
        return distance < ENEMY_SIZE // 2 + player_radius