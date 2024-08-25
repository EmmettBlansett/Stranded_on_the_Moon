import pygame

from constants import WIDTH, HEIGHT, WHITE, LIGHTGRAY, GRAY, DARKGRAY, BLACK, YELLOW, GREEN

class Menu:
    def __init__(self, screen, menu_title = '', font = None, x = 0, y = 0, width = WIDTH, height = HEIGHT, bg_color = GRAY, bg_image = None):
        self.menu_title = menu_title
        self.font = font
        self.rect = pygame.Rect(x,y,width,height)
        self.bg_image = None if not bg_image else pygame.transform.scale(pygame.image.load(bg_image).convert(),(self.rect.width,self.rect.height))
        self.bg_color = bg_color
        self.buttons = []
        self.screen = screen
        self.selected_button = None

    def add_button(self, *args, **kwargs):
        self.buttons.append(Button(*args, **kwargs))

    def draw(self):
        if self.bg_image:
            self.screen.blit(self.bg_image,(self.rect.x,self.rect.y))
        else:
            self.screen.fill(self.bg_color, (self.rect))
            
        for button in self.buttons:
            button.draw(self.screen)

    def handle_mouse_hover(self, mouse_pos):
        for button in self.buttons:
            button.check_hover(mouse_pos)

    def handle_mouse_click(self, mouse_pos):
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(mouse_pos):
                self.selected_button = i
                return i
        return -1

class Button:
    def __init__(self, screen, x, y, width, height, font, text = '', func = lambda: None, text_color = BLACK, bg_color = GRAY, pressed_color = DARKGRAY):
        self.rect = pygame.Rect(x, y, width, height)
        # self.x = x
        # self.y = y
        # self.width = width
        # self.height = height
        self.screen = screen
        self.font = font
        self.text = text
        self.func = func
        self.text_color = text_color
        self.bg_color = bg_color
        self.pressed_color = pressed_color
        self.is_hovered = False

    def draw(self, screen):

        # Draw button shape
        border_color = self.pressed_color if self.is_hovered else self.bg_color
        pygame.draw.rect(screen, border_color, self.rect.inflate(4, 4))  # Border with glow effect
        pygame.draw.rect(screen, self.bg_color, self.rect)  # Main card

        # Draw button text
        button_text = self.font.render(self.text, True, self.text_color)
        center_text_x = self.rect.x + self.rect.width//2 - button_text.get_width()//2
        center_text_y = self.rect.y + self.rect.height//2 - button_text.get_height()//2
        self.screen.blit(button_text,(center_text_x, center_text_y))

    
    def check_hover(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
