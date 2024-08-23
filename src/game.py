import pygame
import math
import random
import os

from player import Player
from enemy import Enemy
from bullet import Bullet

# # Initialize Pygame
# pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
CENTER_X, CENTER_Y = WIDTH//2, HEIGHT//2

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Game settings
PATH_RADIUS = 300
ENEMY_SIZE = 36

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

# Function to draw the solid spiral path
# def draw_spiral_path(screen):
#     points = []
#     for i in range(360 * 13):  # More points to create a full spiral
#         radius = PATH_RADIUS - SPIRAL_SPEED * i
#         if radius > 0:
#             x, y = get_position_on_spiral(CENTER_X, CENTER_Y, radius, i * ENEMY_SPEED)
#             points.append((x, y))

#     # Draw the spiral path as a continuous line
#     if len(points) > 1:
#         pygame.draw.lines(screen, LIGHT_GRAY, False, points, 0)

# def draw_path_bg(phase, screen):
#     screen.blit(PATH_BGS[phase], (0,0))

def intercept_angle(bullet_speed, enemy):
    dt = enemy.radius / bullet_speed
    x1a = enemy.angle+enemy.speed*dt
    return x1a

def get_closest_enemy(enemies):
    if len(enemies) == 0:
        return -1
    min_dist = float('inf')
    min_dist_index = 0
    for i in range(len(enemies)):
        x, y = get_position_on_spiral(CENTER_X, CENTER_Y, enemies[i].radius, enemies[i].angle)
        distance = math.hypot(x - CENTER_X, y - CENTER_Y)
        if distance < min_dist:
            min_dist = distance
            min_dist_index = i
    return min_dist_index

def pause(screen, font):
    pause_message = 'PAUSED'
    pause_text = font.render(pause_message, True, WHITE)
    screen.fill(BLACK, (WIDTH//2-200, HEIGHT//2-200, 400, 400))
    screen.blit(pause_text, (WIDTH//2-pause_text.get_width()//2,HEIGHT//2-pause_text.get_height()))
    pygame.display.flip()
    paused = True
    while paused:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                paused = False
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = False
                    break

def game_over(win, score, minutes, seconds, screen, font):
    game_over_message = 'GAME OVER!!!' if not win else 'YOU WIN!!!'
    game_over_text = font.render(game_over_message, True, WHITE)
    survived_text = font.render(f"You survived for {minutes}:{0 if seconds < 10 else ''}{seconds}", True, WHITE)
    score_text = font.render(f'SCORE: {score}', True, WHITE)

    text_spacer = 50

    screen.fill(BLACK, (WIDTH//2-200, HEIGHT//2-200, 400, 400))
    screen.blit(score_text, ((WIDTH//2-score_text.get_width()//2, HEIGHT//2-score_text.get_height()//2)))
    screen.blit(game_over_text, (WIDTH//2-game_over_text.get_width()//2, HEIGHT//2 - score_text.get_height()//2 - text_spacer))
    screen.blit(survived_text, (WIDTH//2-survived_text.get_width()//2, HEIGHT//2 - score_text.get_height()//2 + text_spacer))

    pygame.display.flip()

    acknowledged = False
    retry = False
    while not acknowledged:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                acknowledged = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    pygame.quit()
                    acknowledged = True
                    break
                elif event.key ==  pygame.K_r:
                    acknowledged = True
                    retry = True
                    break
    if retry:
        game_loop(first_try = False)

def get_phase_dir():
    prev_dir = os.path.dirname(os.path.dirname(__file__))
    enemy_dir = os.path.join(prev_dir,'assets\\phases')
    return enemy_dir

def game_loop(first_try = True):

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Spiral Shooter")

    # Fonts
    font = pygame.font.SysFont(None, 24)
    # Setup
    PATH_BGS = [pygame.image.load(os.path.join(get_phase_dir(),phase)).convert_alpha() for phase in os.listdir(get_phase_dir())]

    player = Player(font=font,screen=screen)
    enemy = Enemy(0,0)
    if first_try:
        Enemy.enemy_types = [pygame.image.load(enemy_fn) for enemy_fn in Enemy.enemy_types]
    enemies = []
    bullets = []
    clock = pygame.time.Clock()

    # Game loop
    running = True
    frame_count = 0
    score = 0

    minute = 0
    second = 0

    phase = 0

    while running:
        if frame_count and frame_count % 3600 == 0:
            phase = min(7, phase + minute%2)
            minute += 1

        if frame_count and frame_count % 60 == 0:
            second += 1
            if second > 5:
                game_over(False, score, minute, second, screen, font)
                running = False
                break
            if second == 60:
                second = 0

        player.xp_thresh_mult = max(1, minute)

        spawn_rate = max(5,60-3*minute) # How often new enemies spawn (num frames per spawn @ 60fps)

        screen.fill(BLACK)

        # draw path background
        screen.blit(PATH_BGS[phase], (0,0))
        
        # Draw score and timer
        score_text = font.render(f"Score: {score}", True, WHITE)
        time_text = font.render(f"Time: {minute}:{0 if second < 10 else ''}{second}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(time_text, (WIDTH // 2 - 40, 10))
        
        # Draw the solid spiral path
        # draw_spiral_path()

        # Shoot bullets automatically at fire rate
        if frame_count % player.fire_rate == 0:
            mx, my = pygame.mouse.get_pos()
            angle = 0
            
            if player.targeting==1:
                angle = math.atan2(my - CENTER_Y, mx - CENTER_X)+math.pi*2
            elif player.targeting==2:
                closest_enemy = get_closest_enemy(enemies)
                angle = 0 if closest_enemy == -1 else intercept_angle(player.projectile_speed, enemies[closest_enemy])
            else:
                angle = random.uniform(0, 2*math.pi)

            # angle =  if not player.mouse_aim else  # angle to fire bullets
            angles = [angle+(2*p*math.pi/player.projectile_count)*(1/player.spread) for p in range(player.projectile_count)]
            if player.targeting:
                # offset = (max(angles)-min(angles))/2
                offset = angles[-1] - angles[len(angles)//2]
                for i in range(len(angles)):
                    angles[i]+=2*math.pi-offset
            for p in range(player.projectile_count):
                bullets.append(
                    Bullet(CENTER_X, CENTER_Y, angles[p],
                        player.pierce, player.damage, player.projectile_speed))

        # Spawn new enemies at the end of the spiral path
        if frame_count % spawn_rate == 0:
            new_enemy = Enemy(0, PATH_RADIUS-ENEMY_SIZE//2, 2**minute)
            enemies.append(new_enemy)

        frame_count += 1

        # Move and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(screen)
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
        
        # Move and draw enemies
        for enemy in enemies[:]:
            enemy.move()
            enemy.draw(screen)
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
                        score += enemy.value  # Increase score by enemy's original health
                        player.gain_xp(enemy.value)  # Gain XP based on enemy's original health
                        # enemy.on_death(player)
                        enemies.remove(enemy)
                    break
            # Check if enemy touches the player
            if enemy.check_player_collision(player.radius):
                player.health -= enemy.health
                enemies.remove(enemy)
                if player.health <= 0:
                    game_over(False, score, minute, second, screen, font)
                    running = False

        # Draw player
        player.draw()
        player.draw_stats()
        if minute == TIME_LIMIT:
                    game_over(True, score, minute, second, screen, font)
                    running = False

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause(screen, font)
        
        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60)
    # Quit the game
    pygame.quit()

if __name__ == '__main__':
    game_loop()
