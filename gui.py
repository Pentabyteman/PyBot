import pygame
import time
import os
import board
import tkinter
from tkinter import filedialog
from bot_exceptions import InvalidAiException


class Speaker:

    def __init__(self):
        self.muted = False

    def play(self, sound):
        if not self.muted:
            sound.play()


class GameWindow:

    def __init__(self, size, board_size, on_finish=None):
        # expects size only to be wider than board_size
        self.size = size
        self.board_size = min(board_size, size)  # may not be larger than size
        self.board_pos = [round(0.5 * (s - b))
                          for s, b in zip(self.size, self.board_size)]
        self.on_finish = on_finish

        self.last_time = time.time()
        self.speaker = Speaker()
        self.init_board()
        self.surface = pygame.Surface(self.size)

        self.ui_components = pygame.sprite.Group()

        # calculate some rects for the space available for the gui
        left_space = pygame.Rect(0, 0, self.board_pos[0], self.size[1])
        right_space = pygame.Rect(self.board_pos[0] + self.board_size[0],
                                  self.board_pos[1],
                                  self.board_pos[0],
                                  self.size[1])

        # add a quit button
        quit_btn_rect = pygame.Rect(left_space.width * 0.125,
                                    left_space.height * 0.05,
                                    left_space.width * 0.25,
                                    left_space.width * 0.25)
        ic_quit = pygame.image.load("quit.png")
        quit_btn = ImageButton(ic_quit, quit_btn_rect)
        if on_finish is not None:
            quit_btn.clicked = on_finish
        self.ui_components.add(quit_btn)

        # add a mute button (finally!!)
        mute_btn_rect = pygame.Rect(left_space.width * 0.625,
                                    left_space.height * 0.05,
                                    left_space.width * 0.25,
                                    left_space.width * 0.25)
        self.ic_not_muted = pygame.image.load("not_muted.png")
        self.ic_muted = pygame.image.load("muted.png")
        self.mute_btn = ImageButton(self.ic_not_muted, mute_btn_rect)
        self.mute_btn.clicked = self.mute_sounds
        self.ui_components.add(self.mute_btn)

        # add the button to play/pause the game
        btn_rect = pygame.Rect(left_space.width * 0.1,
                               left_space.height * 0.2,
                               left_space.width * 0.4,
                               left_space.width * 0.4)
        self.ic_play = pygame.image.load("play.png")
        self.ic_pause = pygame.image.load("pause.png")
        self.btn_play = ImageButton(self.ic_play, btn_rect)
        self.btn_play.clicked = self.play
        self.has_started = False

        # button to reset the game
        btn_reset_rect = pygame.Rect(left_space.width * 0.5,
                                     left_space.height * 0.2,
                                     left_space.width * 0.4,
                                     left_space.width * 0.4)
        ic_reset = pygame.image.load("reset.png")
        btn_reset = ImageButton(ic_reset, btn_reset_rect)
        btn_reset.clicked = self.reset
        self.ui_components.add(btn_reset)

        # prepare file selection dialog
        self.root = tkinter.Tk()
        self.root.withdraw()

        # GameLog
        gameLog_top_x = int(right_space.x + right_space.width * 0.0625)
        gameLog_top_y = int(right_space.height * 0.4)
        gameLog_width = right_space.width * 0.875
        gameLog_height = right_space.height * 0.55
        gamelog_size = (gameLog_width, gameLog_height)
        self.gameLog = GameLog(gamelog_size, gameLog_top_x, gameLog_top_y)

        # list of file selection widgets
        self.file_selectors = []
        # list of health bars
        self.health_bars = []

        # stuff specific for each robot
        for idx, bot in enumerate(sorted(self.board.bots,
                                         key=lambda x: x.team)):
            # draw health bars for each robot on the right side of the board
            pb_offset = idx * right_space.height * 0.1
            width, height = right_space.width, right_space.height
            pb_rect = pygame.Rect(right_space.x + width * 0.1,
                                  right_space.y + height * 0.2 + pb_offset,
                                  width * 0.8,
                                  height * 0.05)
            pb_health = Progressbar(pb_rect, bot.team_color(),
                                    [round(x * 0.1)
                                     if i < 3
                                     else x
                                     for i, x in enumerate(bot.team_color())])
            self.health_bars.append(pb_health)
            self.ui_components.add(pb_health)

            # add button to select an ai file for the given robot
            widget_offset = idx * left_space.height * 0.06
            widget_rect = pygame.Rect(left_space.width * 0.1,
                                      left_space.height * 0.4 + widget_offset,
                                      left_space.width * 0.9,
                                      left_space.height * 0.05)

            widget_open = FileSelectionWidget(widget_rect)
            self.file_selectors.append(widget_open)  # add to list for access
            self.ui_components.add(widget_open)
        self.ui_components.add(self.gameLog)

        # add an error field after the open file widgets
        y_start = self.file_selectors[-1].rect.bottom
        label_rect = pygame.Rect(left_space.width * 0.1,
                                 y_start,
                                 left_space.width * 0.9,
                                 left_space.height * 0.05)
        self.error_label = Label("", label_rect, (255, 0, 0, 255))
        self.ui_components.add(self.error_label)

        self.ui_components.add(self.btn_play)

        # add callbacks to bots
        self.register_callbacks()

    def draw(self):
        self.surface.fill((0, 0, 0, 0))  # clean up
        self.surface.blit(self.board.draw(), self.board_pos)
        self.ui_components.draw(self.surface)
        return self.surface

    def on_tick(self):
        """Called every tick"""
        # delays the turns a little bit to give the players the opportunity
        # to view the turns of their robots
        if (time.time() - self.last_time) > 2:
            self.board.on_turn()
            self.last_time = time.time()

    def update(self, event):
        self.ui_components.update(event)

    def play(self, event):
        if not self.has_started:
            # first start of game -> give ai paths
            ais = [w.path_name for w in self.file_selectors]
            if any(not os.path.isfile(path) for path in ais):
                self.error_label.text = "Error: Invalid ai path!"
                return
            try:
                self.board.start_game([w.path_name
                                       for w in self.file_selectors])
            except InvalidAiException:
                self.error_label.text = "Error: Invalid ai file!"
                return
            self.has_started = True
            for widget in self.ui_components:
                widget.selectable = False
            self.error_label.text = ""
        else:
            self.board.is_playing = not self.board.is_playing
        self.btn_play.icon = self.ic_pause if self.board.is_playing\
            else self.ic_play

    def init_board(self):
        self.board = board.Board(self.board_size, on_finish=self.on_finish)
        self.board.speakers = self.speaker

    def register_callbacks(self):
        for bot, pb_health in zip(sorted(self.board.bots,
                                         key=lambda b: b.team),
                                  self.health_bars):
            bot.register_health_callback(lambda x:
                                         pb_health.set_progress(x / 100))
            bot.register_gamelog_callback(self.gameLog.update_turns)

    def reset(self, event):
        self.init_board()
        self.register_callbacks()
        self.has_started = False
        self.btn_play.icon = self.ic_play
        self.gameLog.reset()
        for sel in self.file_selectors:
            sel.reset()

    def mute_sounds(self, event):
        if pygame.mixer.music.get_volume() > 0:
            self.music_volume = pygame.mixer.music.get_volume()
            pygame.mixer.music.set_volume(0)
            self.speaker.muted = True
            self.mute_btn.icon = self.ic_muted
        else:
            pygame.mixer.music.set_volume(self.music_volume)
            self.speaker.muted = False
            self.mute_btn.icon = self.ic_not_muted


class UIComponent(pygame.sprite.DirtySprite):

    STATE_INVALID, STATE_VALID = 0, 1

    def __init__(self, size, x=0, y=0):
        self.dirty = 2
        self.focussed = False
        self.parent = None
        self.state = UIComponent.STATE_INVALID
        self.size = size
        self._image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self._image.get_rect()
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
            self.mouse_moved(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.contains(*event.pos):
                self.clicked(event)

    def clicked(self, event):
        pass

    def mouse_moved(self, event):
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

    @property
    def state(self):
        return self.__state

    @state.setter
    def state(self, new):
        self.__state = new
        if self.parent:
            self.parent.state = new


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
        super(ImageButton, self).__init__(rect.size, rect.x, rect.y)
        self.icon_size = [int(x * 0.8) for x in rect.size]
        self.icon_pos = [int(x * 0.1) for x in rect.size]
        self.icon = icon

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


class Progressbar(UIComponent):

    def __init__(self, rect, color, bgcolor):
        print("colors:", color, bgcolor)
        self.color, self.bgcolor = color, bgcolor
        self.__progress = 0.5
        super(Progressbar, self).__init__(rect.size, rect.x, rect.y)

    def draw(self):
        draw_progressbar(self._image, self._image.get_rect(),
                         self.color, self.bgcolor,
                         self.progress)

    @property
    def progress(self):
        return self.__progress

    @progress.setter
    def progress(self, new):
        self.__progress = min(max(new, 0), 1)  # between 0 and 1
        self.state = Progressbar.STATE_INVALID

    def set_progress(self, new):
        self.progress = new


class FileSelectionWidget(UIComponent):

    def __init__(self, rect):
        super(FileSelectionWidget, self).__init__(rect.size, rect.x, rect.y)
        # label positioning and font
        self.selectable = True
        self._font = pygame.font.Font("fantasque.ttf", 20)

        self.btn_pos = (rect.width * 0.75, rect.height * 0.05)
        btn_rect = pygame.Rect(self.btn_pos[0],
                               self.btn_pos[1],
                               rect.width * 0.25,
                               rect.height * 0.9)

        ic_open = pygame.image.load("open_file.png")
        self.btn_open = ImageButton(ic_open, btn_rect)
        self.btn_open.parent = self
        self.btn_open.clicked = self.on_select
        self.path_name = ""

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        if self.selectable:
            self.label_rect = pygame.Rect(0,
                                          self.rect.height * 0.15,
                                          self.rect.width * 0.65,
                                          self.rect.height * 0.7)
            self._image.blit(self.btn_open.image, self.btn_pos)
        else:
            self.label_rect = pygame.Rect(0,
                                          self.rect.height * 0.15,
                                          self.rect.width * 0.9,
                                          self.rect.height * 0.7)
        draw_roundrect(self._image, self.label_rect, (200, 200, 200, 255), 0.2)
        name = self.path_name.split("/")[-1]
        text = self._font.render(name, True, (0, 0, 0, 255))
        textpos = text.get_rect()
        textpos.centery = self._image.get_rect().centery
        textpos.x += self._image.get_rect().width * 0.05
        self._image.blit(text, textpos)

    def reset(self):
        self.path_name = ""
        self.selectable = True

    def mouse_moved(self, event):
        if hasattr(event, "pos"):
            x, y = event.pos
            event.pos = (x - self.rect.x, y - self.rect.y)
        if self.selectable:
            self.btn_open.update(event)

    def clicked(self, event):
        if hasattr(event, "pos"):
            x, y = event.pos
            event.pos = (x - self.rect.x, y - self.rect.y)
        if self.selectable:
            self.btn_open.update(event)

    def on_select(self, event):
        # open up file dialog
        path = filedialog.askopenfilename()
        if isinstance(path, str):
            self.path_name = path
            self.state = FileSelectionWidget.STATE_INVALID

    @property
    def selectable(self):
        return self.__selectable

    @selectable.setter
    def selectable(self, new):
        self.__selectable = new
        self.state = FileSelectionWidget.STATE_INVALID


class Label(UIComponent):

    def __init__(self, text, rect, color=(0, 0, 0, 255)):
        super(Label, self).__init__(rect.size, rect.x, rect.y)
        self.text, self.color = text, color
        self._font = pygame.font.Font("fantasque.ttf", 15)

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        text = self._font.render(self.text, True, self.color)
        textpos = self._image.get_rect()
        self._image.blit(text, textpos)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, new):
        self.__text = new
        self.state = Label.STATE_INVALID
        print("updated text", new)


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


def draw_progressbar(surface, rect, color, bgcolor, progress, text="",
                     radius=0.7):
    draw_roundrect(surface, rect, bgcolor, radius)

    foreground = pygame.surface.Surface(rect.size, pygame.SRCALPHA)
    draw_roundrect(foreground, foreground.get_rect(), color, radius)

    revealed = (0, 0, rect.width * progress, rect.height)
    foreground.set_colorkey((0, 0, 0))
    surface.blit(foreground, rect.topleft, area=revealed)

    if text == "":
        return
    font = pygame.font.Font("texgyreadventor-regular.otf", 15)
    text = font.render(text, True, (20, 20, 20))
    t_rect = text.get_rect(center=rect.center)
    surface.blit(text, t_rect)


class GameLog(UIComponent):

    DEFAULT_TURNLIST = ["ROBOT RED:", "ROBOT BLUE:"]

    def __init__(self, gamelog_size, x, y):
        super(GameLog, self).__init__(gamelog_size, x, y)
        self.turnlist = GameLog.DEFAULT_TURNLIST.copy()
        self.gamelog_size = gamelog_size

    def update_turns(self, new_turn):
        self.turnlist.append(new_turn)
        self.state = UIComponent.STATE_INVALID

    def draw(self):
        self._image.fill((0, 0, 0, 255))
        # xpos of first row
        gamelog_rowsize = int(self.gamelog_size[0] / 2)
        gamelog_rownumber = int(self.gamelog_size[1]/30)  # ypos of first col
        current_row = -1  # watch out, needs to start with -1
        index = 0  # watch out, needs to start with 0
        for i in range(0, len(self.turnlist)):
            new_text = self.turnlist[i]
            font = pygame.font.Font("fantasque.ttf", 12)
            if i % 2 == 0:  # muss ne neue Reihe aufmachen
                current_row += 1
                index = 0
            else:  # rechts weiter malen
                index += 1
            surf = font.render(
                new_text,
                True,
                (255, 255, 255, 255))
            # Position not working, please check the y-value
            position = [index * gamelog_rowsize,
                        current_row * gamelog_rownumber]
            self._image.blit(surf, position)

    def reset(self):
        self.turnlist = GameLog.DEFAULT_TURNLIST.copy()
        self.state = UIComponent.STATE_INVALID
