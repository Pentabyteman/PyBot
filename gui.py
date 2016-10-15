import pygame


class GameWindow:

    def __init__(self, size, board_size, board):
        self.size = size
        self.board_size = min(board_size, size)  # may not be larger than size
        self.board_pos = [s - b for s, b in zip(self.size, self.board_size)]

        self.board = board
        self.surface = pygame.Surface(self.size)

        self.ui_components = pygame.sprite.Group()
        space = (0, 0, self.board_pos[0], self.size[1])
        btn_rect = pygame.Rect(space[2] * 0.1,
                               space[3] * 0.2,
                               space[2] * 0.8,
                               space[2] * 0.8)
        self.ic_play = pygame.image.load("play.png")
        self.ic_pause = pygame.image.load("pause.png")
        self.btn_play = ImageButton(self.ic_play, btn_rect)
        self.btn_play.clicked = self.play

        self.ui_components.add(self.btn_play)

    def draw(self):
        self.surface.fill((0, 0, 0, 0))  # clean up
        self.surface.blit(self.board.draw(), self.board_pos)
        self.ui_components.draw(self.surface)
        return self.surface

    def update(self, event):
        self.ui_components.update(event)

    def play(self, event):
        self.board.is_playing = not self.board.is_playing
        self.btn_play.icon = self.ic_pause if self.board.is_playing\
            else self.ic_play


class UIComponent(pygame.sprite.Sprite):

    STATE_INVALID, STATE_VALID = 0, 1

    def __init__(self, size, x=0, y=0):
        self.focussed = False
        self.state = UIComponent.STATE_INVALID
        self.size = size
        self._image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        super(UIComponent, self).__init__()

    def update(self, event):
        try:
            if not self.contains(*event.pos):
                if not self.focussed:
                    return
        except AttributeError:
            return
        if event.type == pygame.MOUSEMOTION:
            if self.contains(*event.pos):
                self.focussed = True
                self.mouse_entered()
            else:
                self.focussed = False
                self.mouse_left()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(*event.pos):
                self.clicked(event)

    def clicked(self, event):
        pass

    def mouse_entered(self):
        pass

    def mouse_left(self):
        pass

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

    def set_pos(self, x, y):
        self.rect.x, self.rect.y = x, y

    def set_center(self, x, y):
        self.rect.center = (x, y)

    @property
    def image(self):
        if self.state == UIComponent.STATE_INVALID:
            self.draw()
            self.state = UIComponent.STATE_VALID

        return self._image


class Button(UIComponent):

    def __init__(self, text, rect=None):
        self.text = text
        self._font = pygame.font.Font("orange_juice.ttf", 50)
        text_dim = [x * 1.2 for x in self._font.size(self.text)]
        if not rect:
            rect = pygame.Rect(0, 0, *text_dim)
        print("rect.size", rect.size)
        super(Button, self).__init__(rect.size, rect.x, rect.y)

    def draw(self):
        draw_roundrect(self._image, self._image.get_rect(),
                       self._bgcolor())
        text = self._font.render(self.text, True, self._fgcolor())
        textpos = text.get_rect()
        textpos.center = self._image.get_rect().center
        self._image.blit(text, textpos)

    def mouse_entered(self):
        self.state = Button.STATE_INVALID

    def mouse_left(self):
        self.state = Button.STATE_INVALID

    def _bgcolor(self):
        if self.focussed:
            return (255, 255, 255, 255)
        else:
            return (0, 0, 0, 255)

    def _fgcolor(self):
        if self.focussed:
            return (0, 0, 0, 255)
        else:
            return (255, 255, 255, 255)

    def clicked(self, event):
        pass


class ImageButton(UIComponent):

    def __init__(self, icon, rect):
        self.icon_size = [int(x * 0.8) for x in rect.size]
        self.icon_pos = [int(x * 0.1) for x in rect.size]
        self.icon = icon
        super(ImageButton, self).__init__(rect.size, rect.x, rect.y)

    @property
    def icon(self):
        return self.__icon

    @icon.setter
    def icon(self, new):
        self.__icon = pygame.transform.scale(new, self.icon_size)
        self.state = Button.STATE_INVALID

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        draw_roundrect(self._image, self._image.get_rect(),
                       self._bgcolor())
        self._image.blit(self.icon, self.icon_pos)

    def _bgcolor(self):
        if self.focussed:
            return (255, 255, 255, 255)
        else:
            return (0, 0, 0, 255)

    def mouse_entered(self):
        self.state = Button.STATE_INVALID

    def mouse_left(self):
        self.state = Button.STATE_INVALID


def draw_roundrect(surface, rect, color, radius=0.4):

    rect = pygame.Rect(rect)
    color = pygame.Color(*color)
    alpha = color.a
    color.a = 0
    pos = rect.topleft
    rect.topleft = 0, 0
    rectangle = pygame.Surface(rect.size, pygame.SRCALPHA)

    circle = pygame.Surface([min(rect.size) * 3] * 2, pygame.SRCALPHA)
    pygame.draw.ellipse(circle, (0, 0, 0), circle.get_rect(), 0)
    circle = pygame.transform.smoothscale(circle,
                                          [int(min(rect.size) * radius)] * 2)

    radius = rectangle.blit(circle, (0, 0))
    radius.bottomright = rect.bottomright
    rectangle.blit(circle, radius)
    radius.topright = rect.topright
    rectangle.blit(circle, radius)
    radius.bottomleft = rect.bottomleft
    rectangle.blit(circle, radius)

    rectangle.fill((0, 0, 0), rect.inflate(-radius.w, 0))
    rectangle.fill((0, 0, 0), rect.inflate(0, -radius.h))

    rectangle.fill(color, special_flags=pygame.BLEND_RGBA_MAX)
    rectangle.fill((255, 255, 255, alpha), special_flags=pygame.BLEND_RGBA_MIN)

    return surface.blit(rectangle, pos)
