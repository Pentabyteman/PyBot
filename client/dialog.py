import window
import pygame
from ui_components import Button, draw_roundrect, Label

app = None
SMALL, MEDIUM, LARGE = None, None, None


def init(a):
    global app, SMALL, MEDIUM, LARGE
    app = a
    w, h = app.display.get_size()
    SMALL = (w * 0.3, h * 0.2)
    MEDIUM = (w * 0.5, h * 0.3)
    LARGE = (w * 0.7, h * 0.5)


def show(dialog):
    global SMALL, MEDIUM, LARGE
    if app is None:
        return False
    app.dialog = dialog


class Dialog(window.Window):

    def __init__(self, size):
        super(Dialog, self).__init__(size)
        self.shadow_rect = self.rect.copy()
        self.shadow_rect.width = self.rect.width * 0.98
        self.shadow_rect.height = self.rect.height * 0.98
        self.area = self.rect.copy()
        self.area.x += self.rect.width * 0.01
        self.area.y += self.rect.height * 0.01
        self.area.width = self.shadow_rect.width
        self.area.height = self.shadow_rect.height
        self.content = pygame.Surface(self.area.size, pygame.SRCALPHA)

    def draw(self):
        self.surface.fill((0, 0, 0, 0))
        draw_roundrect(self.surface, self.shadow_rect,
                       (180, 180, 180, 255))
        draw_roundrect(self.surface, self.area,
                       (255, 255, 255, 255))  # background
        self.ui_components.draw(self.content)
        self.surface.blit(self.content, self.area)

    def on_finish(self):
        pass


class AlertDialog(Dialog):

    def __init__(self, size, text):
        super(AlertDialog, self).__init__(size)
        lbl_rect = pygame.Rect(self.area.width * 0.1,
                               self.area.height * 0.1,
                               self.area.width * 0.8,
                               self.area.height * 0.15)
        lbl = Label(text, lbl_rect, (0, 0, 0, 255), 28, centered=True,
                    bold=True)
        self.ui_components.add(lbl)

        btn_rect = pygame.Rect(self.area.width * 0.3,
                               self.area.height * 0.6,
                               self.area.width * 0.4,
                               self.area.height * 0.2)
        btn = Button("Ok", btn_rect, 30, True)
        btn.clicked = lambda x: self.on_finish()
        self.ui_components.add(btn)


class SpectateDialog(Dialog):

    def __init__(self, size, client):
        super(SpectateDialog, self).__init__(size)
        lbl_rect = pygame.Rect(self.area.width * 0.1,
                               self.area.height * 0.1,
                               self.area.width * 0.8,
                               self.area.height * 0.15)
        lbl = Label("Spectate", lbl_rect, (0, 0, 0, 255), 28, centered=True,
                    bold=True)
        self.ui_components.add(lbl)

        quit_rect = pygame.Rect(self.area.width * 0.4,
                                self.area.height * 0.8,
                                self.area.width * 0.2,
                                self.area.height * 0.15)
        btn_quit = Button("Cancel", quit_rect, text_size=25)
        btn_quit.clicked = lambda x: self.on_finish()
        self.ui_components.add(btn_quit)

        self.client = client
        self.client.on_games_info = self.setup_options
        self.client.send("games")

    def setup_options(self, games):
        margin_x = self.area.width * 0.01
        margin_y = self.area.height * 0.01
        width = self.area.width * 0.1
        height = width
        minx = self.area.width * 0.1
        maxx = self.area.width * 0.9
        currentx = minx
        currenty = self.area.height * 0.35
        for game in games:
            if currentx > maxx:
                currentx = minx
                currenty += height + margin_y
            btn_rect = pygame.Rect(currentx,
                                   currenty,
                                   width, height)
            currentx = btn_rect.right + margin_x
            btn = Button(str(game), btn_rect, text_size=20)
            btn.clicked = lambda x, n=game: self.join_game(n)
            self.ui_components.add(btn)

    def join_game(self, game):
        self.client.send("join {}".format(game))
        self.on_finish()
