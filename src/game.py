import pygame
import math
import random
import os
import sys
import time

from player import Player
from enemy import Enemy
from bullet import Bullet
from menu import Menu, Button

# Constants
from constants import WIDTH, HEIGHT, WHITE, LIGHTGRAY, GRAY, DARKGRAY, BLACK

# Screen dimensions
CENTER_X, CENTER_Y = WIDTH//2, HEIGHT//2

# Game settings
PATH_RADIUS = 300
ENEMY_SIZE = 36

# Timer and XP system
TIME_LIMIT = 20
TIME_WARP_MULT = 1
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

def model_aim(screen, image, angle, topleft=(CENTER_X-20, CENTER_Y-20)):
    #point the image toward the angle
    rotated_image = pygame.transform.rotate(image, -angle*180/math.pi)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)
    screen.blit(rotated_image, new_rect)

def game_over(win, score, minutes, seconds, screen, font):
    game_over_message = 'GAME OVER!!!' if not win else 'YOU WIN!!!'
    game_over_text = font.render(game_over_message, True, WHITE)
    survived_text = font.render(f"You survived for {minutes}:{0 if seconds < 10 else ''}{seconds}", True, WHITE)
    score_text = font.render(f'SCORE: {score}', True, WHITE)
    choice_text = font.render(f'(E)XIT or (R)ETRY', True, WHITE)

    text_spacer = 50

    screen.fill(BLACK, (WIDTH//2-200, HEIGHT//2-200, 400, 400))
    screen.blit(score_text, ((WIDTH//2-score_text.get_width()//2, HEIGHT//2-score_text.get_height()//2)))
    screen.blit(game_over_text, (WIDTH//2-game_over_text.get_width()//2, HEIGHT//2 - score_text.get_height()//2 - text_spacer))
    screen.blit(survived_text, (WIDTH//2-survived_text.get_width()//2, HEIGHT//2 - score_text.get_height()//2 + text_spacer))
    screen.blit(choice_text, (WIDTH//2-choice_text.get_width()//2, HEIGHT//2 - score_text.get_height() + 2*text_spacer))

    pygame.display.flip()

    acknowledged = False
    retry = False
    while not acknowledged:
        time.sleep(1/60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                acknowledged = True
                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    pygame.quit()
                    sys.exit()
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

def update_time(frame_count, minute, second):
    if frame_count and frame_count % 3600 == 0:
        minute += 1

    if frame_count and frame_count % 60 == 0:
        second += 1
        if second == 60:
            second = 0
    return (minute, second)

def get_angles(player, targeting, mx = 0, my = 0, intercept_angle = 0):
    if targeting==1:
        angle = math.atan2(my - CENTER_Y, mx - CENTER_X)+math.pi*2
    elif targeting==2:
        angle = intercept_angle
    else:
        angle = random.uniform(0, 2*math.pi)
    player_angle = angle

    angles = [angle+(2*p*math.pi/player.projectile_count)*(1/player.spread) for p in range(player.projectile_count)]
    center_offset = (max(angles)-min(angles))/2
    if targeting:
        offset = (angles[-1] - angles[len(angles)//2]) if player.targeting == 2 else center_offset
        if targeting == 2 and player.projectile_count > 1:
            player_angle += center_offset/(player.projectile_count-1) * (1-player.projectile_count%2)
        for i in range(len(angles)):
            angles[i]+=2*math.pi-offset
    else:
        player_angle += center_offset

    return (player_angle, angles)

def get_asset_file(folder, file):
    game_dir = os.path.dirname(os.path.dirname(__file__))
    asset_dir = os.path.join(game_dir,'assets')
    return os.path.join(asset_dir, f'{folder}\\{file}')

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
        Player.models = [pygame.image.load(player_fn) for player_fn in Player.models]
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

    #TODO add animations class (frame, duration, update(), draw())

    while running:
        minute, second = update_time(frame_count, minute, second)
        phase = min(len(PATH_BGS)-1, minute//2)

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

        # Shoot bullets automatically at fire rate
        if frame_count % player.fire_rate == 0:
            mx, my = pygame.mouse.get_pos()
            intercept = 0

            if player.targeting == 2:
                intercept = 0 if len(enemies) == 0 else intercept_angle(bullet.speed, enemies[get_closest_enemy(enemies)])

            player.angle, angles = get_angles(player, player.targeting, mx, my, intercept)

            for p in range(player.projectile_count):
                bullets.append(
                    Bullet(CENTER_X, CENTER_Y, angles[p],
                        player.pierce, player.damage, player.projectile_speed))

        # Spawn new enemies at the end of the spiral path
        if frame_count % spawn_rate == 0:
            new_enemy = Enemy(0, PATH_RADIUS-ENEMY_SIZE//2, 2**minute)
            enemies.append(new_enemy)

        # Move and draw bullets
        for bullet in bullets[:]:
            bullet.move()
            bullet.draw(screen)
            if bullet.x < 0 or bullet.x > WIDTH or bullet.y < 0 or bullet.y > HEIGHT:
                bullets.remove(bullet)
        
        # Move and draw enemies
        xp_gained = 0
        for enemy in enemies:
            draw = True
            enemy.move()
            # Check if enemy touches the player
            if enemy.check_player_collision(player.radius):
                player.take_damage(enemy.health)
                enemies.remove(enemy)
                draw = False
                if player.health <= 0:
                    game_over(False, score, minute, second, screen, font)
                    running = False
            # Check for collision with bullets
            for bullet in bullets:
                if enemy.check_collision(bullet):
                    enemy.add_collision(bullet.num)
                    enemy.health -= bullet.damage
                    if bullet.pierce == 0:
                        bullets.remove(bullet)
                    else:
                        bullet.collide()
                    if enemy.health <= 0:
                        score += enemy.value  # Increase score by enemy's original health
                        xp_gained += enemy.value
                        # enemy.on_death(player)
                        enemies.remove(enemy)
                        draw = False
                        break
            if draw:
                enemy.draw(screen)
        
        # Draw player aiming at current angle
        model_aim(screen, Player.models[player.model],player.angle)
        player.draw_health(screen)

        if pygame.key.get_pressed()[pygame.K_TAB]:
            player.draw_stats()

        player.gain_xp(xp_gained)  # Gain XP based on enemy's original health

        if minute == TIME_LIMIT:
            game_over(True, score, minute, second, screen, font)
            running = False
            break

        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pause(screen)
        
        frame_count += 1
        
        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(60 * TIME_WARP_MULT)


    # Quit the game
    pygame.quit()
    sys.exit()

def main_menu():

    pygame.init()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Stranded on the Moon")

    # Fonts
    font = pygame.font.SysFont(None, 24)

    menu_button_width = 200
    menu_button_height = 50

    bg_image = get_asset_file('menu_background', 'stranded_on_the_moon.png')

    main_menu = Menu(screen,'Stranded on the Moon',font,0,0,WIDTH,HEIGHT,LIGHTGRAY,bg_image)
    main_menu.add_button(screen,CENTER_X-menu_button_width//2,CENTER_Y+200,menu_button_width,menu_button_height,font,text='PLAY',func=game_loop)
    main_menu.add_button(screen,CENTER_X-menu_button_width//2,CENTER_Y+300,menu_button_width,menu_button_height,font,text='EXIT',func=pygame.quit)

    action = None
    while not action:
        mouse_pos = pygame.mouse.get_pos()
        main_menu.handle_mouse_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_button = main_menu.handle_mouse_click(mouse_pos)
                    if selected_button>-1:
                        action = main_menu.buttons[selected_button].func
        main_menu.draw()
        pygame.display.flip()
        time.sleep(1/60)
    action()

def pause(screen):
    # Fonts
    font = pygame.font.SysFont(None, 24)

    menu_button_width = 200
    menu_button_height = 50

    pause_menu = Menu(screen,'PAUSED',font,WIDTH//4,HEIGHT//4,WIDTH//2,HEIGHT//2,BLACK)
    pause_menu.add_button(screen,CENTER_X-menu_button_width//2,CENTER_Y-10-menu_button_height,menu_button_width,menu_button_height,font,text='RESUME')
    pause_menu.add_button(screen,CENTER_X-menu_button_width//2,CENTER_Y+10,menu_button_width,menu_button_height,font,text='QUIT',func=sys.exit)

    paused = True
    while paused:

        mouse_pos = pygame.mouse.get_pos()
        pause_menu.handle_mouse_hover(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    selected_button = pause_menu.handle_mouse_click(mouse_pos)
                    if selected_button>-1:
                        action = pause_menu.buttons[selected_button].func
                        paused = False
        pause_menu.draw()
        pygame.display.flip()
        time.sleep(1/60)
    action()

if __name__ == '__main__':
    main_menu()
