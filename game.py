import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spiral Shooter")

# Fonts
font = pygame.font.SysFont(None, 24)

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_RADIUS = 20
PLAYER_COLOR = GREEN
PLAYER_POS = (WIDTH // 2, HEIGHT // 2)
PLAYER_MAX_HEALTH = 100
PLAYER_HEALTH = PLAYER_MAX_HEALTH
# PLAYER_SPEED = 5
PLAYER_PROJECTILES = 1

# Bullet settings
BULLET_COLOR = RED
BULLET_RADIUS = 5
BULLET_SPEED = 8
BULLET_DAMAGE = 1
FIRE_RATE = 30  # Higher = slower firing rate (frames per shot)

# Enemy settings
SQUARE_SIZE = 30
SQUARE_COLOR = BLACK
ENEMY_START_RADIUS = 300
ENEMY_SPIRALS = 6  # Number of spirals before player is reached
ENEMY_SPEED = 0.02  # Radians per frame
SPIRAL_SPEED = ENEMY_SPEED * ENEMY_SPIRALS  # How quickly they spiral inward
ENEMY_HEALTH = 1  # Base health of each square
ENEMY_HEALTH_MULTIPLIER = 1  # Multiplies health every 30 seconds

# Game settings
SPAWN_RATE = 40  # How often new enemies spawn (num frames per spawn @ 60fps)
SCORE = 0


# Timer and XP system
TIME_LIMIT = 20
XP = 0
LEVEL = 1
XP_THRESH = 10  # Initial XP threshold
XP_THRESH_CONSTANT = 20

# Function to calculate the circular movement
def get_position_on_spiral(center_x, center_y, radius, angle):
    x = center_x + radius * math.cos(angle)
    y = center_y + radius * math.sin(angle)
    return x, y

# Classes
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
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

    def collide(self):
        self.pierce -= 1

class Enemy:
    def __init__(self, angle, radius, health = ENEMY_HEALTH * ENEMY_HEALTH_MULTIPLIER):
        self.angle = angle
        self.radius = radius
        self.max_health = health
        self.health = self.max_health
        self.speed = ENEMY_SPEED
        self.spiral_speed = SPIRAL_SPEED
        self.value = self.max_health
        self.color = SQUARE_COLOR
        self.collisions = set()
        self.rand = random.random()
        self.x, self.y = get_position_on_spiral(PLAYER_POS[0], PLAYER_POS[1], self.radius, self.angle)
        self.apply_effect()
    
    def apply_effect(self):
        if self.rand < .1:
            self.color = GREEN
            self.value*=10
        elif self.rand < .2:
            self.color = RED
            self.speed*= 2
            self.spiral_speed = self.speed * ENEMY_SPIRALS
        elif self.rand > .9:
            self.color = BLUE
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
        self.x, self.y = get_position_on_spiral(PLAYER_POS[0], PLAYER_POS[1], self.radius, self.angle)
    
    def draw(self):
        pygame.draw.circle(screen, self.color, (self.x, self.y), SQUARE_SIZE//2)
        self.draw_health(self.x, self.y)

    def draw_health(self, x, y):
        health_text = font.render(str(self.health), True, WHITE)
        screen.blit(health_text, (x - health_text.get_width() // 2, y - health_text.get_height() // 2))

    def check_collision(self, bullet):
        distance = math.hypot(bullet.x - self.x, bullet.y - self.y)
        return distance < SQUARE_SIZE // 2 + BULLET_RADIUS and bullet.num not in self.collisions

    def add_collision(self, bullet_num):
        self.collisions.add(bullet_num)

    def check_player_collision(self):
        distance = math.hypot(self.x - PLAYER_POS[0], self.y - PLAYER_POS[1])
        return distance < SQUARE_SIZE // 2 + PLAYER_RADIUS

class Player:
    def __init__(self):
        self.health = PLAYER_MAX_HEALTH
        self.fire_rate = FIRE_RATE
        self.projectile_count = PLAYER_PROJECTILES
        self.xp = XP
        self.level = LEVEL
        self.xp_thresh = XP_THRESH
        self.xp_thresh_mult = 1
        self.damage = BULLET_DAMAGE
        self.pierce = 0
        self.projectile_speed = BULLET_SPEED
        self.mouse_aim = False
        self.auto_aim = False
        self.spread = 1
        self.upgrade_choices = {"Increase Projectiles":self.increase_projectiles, "Increase Rate of Fire":self.increase_rof, 
                                  "Increase Damage":self.increase_damage, "Increase Pierce": self.increase_pierce, 
                                  "Increase Projectile Speed":self.increase_projectile_speed, "Enable Mouse Aiming":self.enable_mouse_aim,
                                  "Reduce Spread":self.reduce_spread}

    def increase_damage(self, amount = 1):
        self.damage += amount

    def increase_pierce(self, amount = 1):
        self.pierce += amount
        if self.pierce == 6:
            del self.upgrade_choices['Increase Pierce']

    def increase_projectile_speed(self, amount = 1):
        self.projectile_speed += amount
        if self.projectile_speed >= 16:
            del self.upgrade_choices['Increase Projectile Speed']

    def enable_mouse_aim(self):
        self.mouse_aim = True
        del self.upgrade_choices['Enable Mouse Aiming']
        self.upgrade_choices["Enable Auto Aim"] = self.enable_auto_aim

    def enable_auto_aim(self):
        self.mouse_aim = False
        self.auto_aim = True
        del self.upgrade_choices['Enable Auto Aim']

    def reduce_spread(self, amount = 1):
        self.spread += 1
        if self.spread >= 12:
            del self.upgrade_choices['Reduce Spread']
    
    def increase_projectiles(self, amount = 1):
        self.projectile_count += amount
        if self.projectile_count >= 8:
            del self.upgrade_choices['Increase Projectiles']

    def increase_rof(self, amount = 1):
        self.fire_rate -= amount  # Minimum fire rate is 2
        if self.fire_rate <= 2:
            del self.upgrade_choices["Increase Rate of Fire"]
    
    def heal(self, amount):
        self.health = min(PLAYER_MAX_HEALTH, self.health + amount)
    
    def draw(self):
        pygame.draw.circle(screen, PLAYER_COLOR, (PLAYER_POS[0], PLAYER_POS[1]), PLAYER_RADIUS)
        self.draw_health()

    def draw_health(self):
        health_text = font.render(f'{self.health}', True, BLACK)
        screen.blit(health_text, (PLAYER_POS[0] - health_text.get_width() // 2, PLAYER_POS[1]-health_text.get_height() // 2))

    def draw_stats(self):
        stats = [font.render(f'Level: {self.level}', True, BLACK),font.render(f'Projectiles: {self.projectile_count}', True, BLACK),
                 font.render(f'Damage: {self.damage}', True, BLACK),font.render(f'Fire Rate: {round(3600/self.fire_rate,2)}', True, BLACK),
                 font.render(f'Pierce: {self.pierce}', True, BLACK),font.render(f'Spread: {360 // self.spread}', True, BLACK),
                 font.render(f'Velocity: {self.projectile_speed}', True, BLACK)]
        text_height = stats[0].get_height()
        text_width = max([stat.get_width() for stat in stats])

        for i, text in enumerate(stats):
            screen.blit(text, (WIDTH-text_width,10+text_height*i))

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

        screen.fill(WHITE)
        pygame.display.flip()
        upgrade_text = font.render("Choose an upgrade:", True, BLACK)
        screen.blit(upgrade_text, (WIDTH // 2 - upgrade_text.get_width() // 2, HEIGHT // 2 - 100))
        
        for i, choice in enumerate(choices):
            choice_text = font.render(f'{i+1}: {choice}', True, BLACK)
            screen.blit(choice_text, (WIDTH // 2 - choice_text.get_width() // 2, HEIGHT // 2 + i * 30))
        
        pygame.display.flip()
        
        # Wait for player to choose an upgrade
        chosen = False

        keys = [pygame.K_1, pygame.K_2, pygame.K_3]

        key_choices = {key: i for i, key in enumerate(keys[:len(choices)])}

        # key_choices = {pygame.K_1: 1, pygame.K_2: 2, pygame.K_3: 3}

        while not chosen: 
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key in key_choices:
                        self.upgrade_choices[choices[key_choices[event.key]]]()
                        chosen = True

# Function to draw the solid spiral path
def draw_spiral_path():
    points = []
    for i in range(360 * 13):  # More points to create a full spiral
        radius = ENEMY_START_RADIUS - SPIRAL_SPEED * i
        if radius > 0:
            x, y = get_position_on_spiral(PLAYER_POS[0], PLAYER_POS[1], radius, i * ENEMY_SPEED)
            points.append((x, y))

    # Draw the spiral path as a continuous line
    if len(points) > 1:
        pygame.draw.lines(screen, BLUE, False, points, 1)

def intercept(bullet_speed, enemy):
    dt = enemy.radius / bullet_speed
    # dy = 
    # dt2 = (enemy.radius - dt*enemy.spiral_speed) / bullet_speed

    x1a = enemy.angle+enemy.speed*dt
    # print(f'Intercept Angle: {x1a}')
    # x1r = enemy.radius*dt2*60

    return x1a

def get_closest_enemy(enemies):
    if len(enemies) == 0:
        return -1
    min_dist = float('inf')
    min_dist_index = 0
    for i in range(len(enemies)):
        x, y = get_position_on_spiral(PLAYER_POS[0], PLAYER_POS[1], enemies[i].radius, enemies[i].angle)
        distance = math.hypot(x - PLAYER_POS[0], y - PLAYER_POS[1])
        if distance < min_dist:
            min_dist = distance
            min_dist_index = i
    # print(f'Enemy Color: {enemies[min_dist_index].color}')
    # print(f'Enemy Health: {enemies[min_dist_index].health}')
    # print(f'Enemy Angle: {enemies[min_dist_index].angle}')
    return min_dist_index


# Setup
player = Player()
enemies = []
bullets = []
clock = pygame.time.Clock()

# Game loop
running = True
frame_count = 0
SCORE = 0

while running:
    minute = frame_count // 3600
    second = (frame_count // 60) % 60

    player.xp_thresh_mult = max(1, minute)

    if minute == 15:
        print(f'Level:{player.level}')
        print(f'Score: {SCORE}')
        break # TODO replace with game over you win screen

    SPAWN_RATE = 60-3*minute
    
    # # Every 30 seconds, double the health of new enemies
    # if ((frame_count // 60) % 60) % 30 == 0:
    #     ENEMY_HEALTH_MULTIPLIER *= 2

    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the solid spiral path
    draw_spiral_path()

    # Shoot bullets automatically at a fixed rate
    if frame_count % player.fire_rate == 0:
        mx, my = pygame.mouse.get_pos()
        angle = 0.0
        
        if player.mouse_aim:
            angle = math.atan2(my - PLAYER_POS[1], mx - PLAYER_POS[0])+math.pi*2
        elif player.auto_aim:
            closest_enemy = get_closest_enemy(enemies)
            angle = 0 if closest_enemy == -1 else intercept(player.projectile_speed, enemies[closest_enemy])
        else:
            angle = random.uniform(0, 2 * math.pi)

        # angle =  if not player.mouse_aim else  # angle to fire bullets
        angles = [angle+(2*p*math.pi/player.projectile_count)*(1/player.spread) for p in range(player.projectile_count)]
        if player.mouse_aim or player.auto_aim:
            # offset = (max(angles)-min(angles))/2
            offset = angles[-1] - angles[len(angles)//2]
            for i in range(len(angles)):
                angles[i]+=2*math.pi-offset
        for p in range(player.projectile_count):
            bullets.append(
                Bullet(PLAYER_POS[0], PLAYER_POS[1], angles[p],
                       player.pierce, player.damage, player.projectile_speed))

    # Spawn new enemies at the end of the spiral path
    if frame_count % SPAWN_RATE == 0:
        new_enemy = Enemy(0, ENEMY_START_RADIUS, 2**minute)
        enemies.append(new_enemy)

    frame_count += 1

    # Move and draw bullets
    for bullet in bullets[:]:
        bullet.move()
        bullet.draw()
        if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
            bullets.remove(bullet)
    
    # Move and draw enemies
    for enemy in enemies[:]:
        enemy.move()
        enemy.draw()
        # Check for collision with bullets
        for bullet in bullets[:]:
            if enemy.check_collision(bullet):
                enemy.add_collision(bullet.num)
                enemy.health -= bullet.damage
                if bullet.pierce == 0:
                    bullets.remove(bullet)
                else:
                    bullet.collide()
                if enemy.health <= 0:
                    SCORE += enemy.value  # Increase score by enemy's original health
                    player.gain_xp(enemy.value)  # Gain XP based on enemy's original health
                    # enemy.on_death(player)
                    enemies.remove(enemy)
                break
        # Check if enemy touches the player
        if enemy.check_player_collision():
            player.health -= enemy.health
            enemies.remove(enemy)
            if player.health <= 0:
                print("Game Over!")
                running = False

    # Draw player
    player.draw()

    # Draw score and timer
    score_text = font.render(f"Score: {SCORE}", True, BLACK)
    time_text = font.render(f"Time: {minute}:{0 if second < 10 else ''}{second}", True, BLACK)
    screen.blit(score_text, (10, 10))
    screen.blit(time_text, (WIDTH // 2 - 40, 10))

    player.draw_stats()
    
    # Update display
    pygame.display.flip()
    
    # Cap the frame rate
    clock.tick(60)

# Quit the game
pygame.quit()
