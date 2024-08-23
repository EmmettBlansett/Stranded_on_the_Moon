import pygame
import math

BULLET_DAMAGE = 1
BULLET_SPEED = 8
BULLET_RADIUS = 5
BULLET_COLOR = (255,0,0)

class Bullet:
    counter = 0
    def __init__(self, x, y, angle, pierce = 0, damage = BULLET_DAMAGE, speed = BULLET_SPEED, size = BULLET_RADIUS, color = BULLET_COLOR):
        self.num = Bullet.counter
        Bullet.counter+=1
        self.x = x
        self.y = y
        self.angle = angle
        self.damage = damage
        self.speed = speed
        self.size = size
        self.color = color
        self.pierce = pierce
        self.velocity = [math.cos(self.angle), math.sin(self.angle)]
    
    def move(self):
        self.x += self.speed * self.velocity[0]
        self.y += self.speed * self.velocity[1]
    
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def collide(self):
        self.pierce -= 1