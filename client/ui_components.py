#!/usr/bin/python
# -*- coding: iso-8859-15 -*-

import pygame
import fonthelper
from tkinter import filedialog


class UIGroup(pygame.sprite.Group):

    def __init__(self):
        super(UIGroup, self).__init__()
        self.focussed_sprite = None

    def update(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.focussed_sprite is not None:
                self.focussed_sprite.focussed = False
                self.focussed_sprite = None

        request_focus = False
        for sprite in self.sprites():
            if sprite.update(event):
                # print("wants focus")
                if self.focussed_sprite is not None and\
                   self.focussed_sprite != sprite:
                    self.focussed_sprite.focussed = False
                sprite.focussed = True
                self.focussed_sprite = sprite
                # print("now focussed", self.focussed_sprite)
                request_focus = True
        return request_focus

    def on_tick(self):
        for sprite in self.sprites():
            sprite.on_tick()


class UIComponent(pygame.sprite.DirtySprite):

    STATE_INVALID, STATE_VALID = 0, 1

    def __init__(self, size, x=0, y=0):
        self.dirty = 2
        self.hovered, self.__focussed = False, False
        self.parent = None
        self.state = UIComponent.STATE_INVALID
        self.size = size
        self._image = pygame.Surface(self.size, pygame.SRCALPHA)
        self.rect = self._image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.enabled = True
        self.requests_focus = False
        self.target, self.step = None, None
        self.virt_pos = self.rect.topleft
        super(UIComponent, self).__init__()

    def update(self, event):
        if not self.enabled:
            self.hovered, self.focussed = False, False
            self.state = UIComponent.STATE_INVALID
            return
        try:
            if not self.contains(*event.pos):
                if not self.hovered:
                    return
        except AttributeError:
            pass
        if event.type == pygame.MOUSEMOTION:
            if self.contains(*event.pos):
                self.hovered = True
                self.mouse_entered()
            else:
                self.hovered = False
                self.mouse_left()
            self.mouse_moved(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.contains(*event.pos):
                if event.button == 1:
                    self.clicked(event)
                    return self.requests_focus  # request focus
                elif event.button == 4:
                    self.scrolled(1)
                elif event.button == 5:
                    self.scrolled(-1)
        elif event.type == pygame.KEYDOWN and self.focussed:
            self.key_typed(event.key)

        return False

    def on_tick(self):
        if self.target is None:
            return
        if self.rect.topleft == self.target:
            print("Reached target")
            self.target, self.step = None, None
        else:
            diff = [abs(t - v) for t, v in zip(self.target, self.virt_pos)]
            self.virt_pos = [(own + step)
                             for own, step in zip(self.virt_pos,
                                                  self.step)]
            new_diff = [abs(t - v) for t, v in zip(self.target, self.virt_pos)]
            if new_diff > diff:
                self.virt_pos = self.target
            self.rect.topleft = self.virt_pos

    def clicked(self, event):
        pass

    def scrolled(self, direction):
        pass

    def mouse_moved(self, event):
        pass

    def mouse_entered(self):
        pass

    def mouse_left(self):
        pass

    def key_typed(self, key):
        pass

    def contains(self, x, y):
        return self.rect.collidepoint(x, y)

    def set_pos(self, x, y):
        self.rect.x, self.rect.y = x, y

    def set_center(self, x, y):
        self.rect.center = (x, y)

    def move_to(self, x, y, frames):
        self.target = (round(x), round(y))
        self.step = [(t - s) / frames
                     for t, s in zip(self.target, self.rect.topleft)]
        print("Target is at", self.target, "step", self.step)

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

    @property
    def focussed(self):
        return self.__focussed

    @focussed.setter
    def focussed(self, state):
        self.__focussed = state
        self.state = UIComponent.STATE_INVALID


class UIWidget(UIComponent):

    def __init__(self, rect):
        super(UIWidget, self).__init__(rect.size, rect.x, rect.y)
        self.ui_components = UIGroup()

    def add(self, component):
        component.parent = self
        self.ui_components.add(component)

    def update(self, event):
        if not self.enabled:
            return
        if hasattr(event, 'pos'):
            x, y = event.pos
            event.pos = (x - self.rect.x, y - self.rect.y)
        state = self.ui_components.update(event)
        if hasattr(event, 'pos'):
            event.pos = (x, y)
        if not state:
            super(UIWidget, self).update(event)
        return state

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        self.ui_components.draw(self._image)


class HoverableComponent(UIComponent):

    def __init__(self, rect, reverse_color=False):
        super(HoverableComponent, self).__init__(rect.size, rect.x, rect.y)
        self.colors = {"bg": ((255, 255, 255, 255), (0, 0, 0, 255)),
                       "fg": ((0, 0, 0, 255), (255, 255, 255, 255))}
        self._color_rev = reverse_color
        self._ignore = False

    def mouse_entered(self):
        self.state = UIComponent.STATE_INVALID

    def mouse_left(self):
        self.state = UIComponent.STATE_INVALID

    def _bgcolor(self):
        tag = "fg" if self._color_rev else "bg"
        return self.colors[tag][0 if self.hovered and not self._ignore else 1]

    def _fgcolor(self):
        tag = "bg" if self._color_rev else "fg"
        return self.colors[tag][0 if self.hovered and not self._ignore else 1]


class Button(HoverableComponent):

    def __init__(self, text, rect=None, text_size=15,
                 reverse_color=False):
        self.text = text
        self._font = pygame.font.Font("resources/fantasque.ttf", text_size)
        text_dim = [x * 1.2 for x in self._font.size(self.text)]
        if not rect:
            rect = pygame.Rect(0, 0, *text_dim)
        super(Button, self).__init__(rect, reverse_color=reverse_color)

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        draw_roundrect(self._image, self._image.get_rect(),
                       self._bgcolor())
        text = self._font.render(self.text, True, self._fgcolor())
        textpos = text.get_rect()
        textpos.center = self._image.get_rect().center
        self._image.blit(text, textpos)

    def clicked(self, event):
        pass


class ImageButton(HoverableComponent):

    def __init__(self, icon, rect):
        super(ImageButton, self).__init__(rect)
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


class Progressbar(UIComponent):

    def __init__(self, rect, color, bgcolor):
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
        self._font = pygame.font.Font("resources/fantasque.ttf", 20)

        self.btn_pos = (rect.width * 0.75, rect.height * 0.05)
        btn_rect = pygame.Rect(self.btn_pos[0],
                               self.btn_pos[1],
                               rect.width * 0.25,
                               rect.height * 0.9)

        ic_open = pygame.image.load("resources/open_file.png")
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
        path = filedialog.askopenfilename(initialdir="ai")
        if isinstance(path, str):
            self.path_name = path
            self.state = FileSelectionWidget.STATE_INVALID
            self.on_selected()

    def on_selected(self):
        pass

    @property
    def selectable(self):
        return self.__selectable

    @selectable.setter
    def selectable(self, new):
        self.__selectable = new
        self.state = FileSelectionWidget.STATE_INVALID


class Label(UIComponent):

    def __init__(self, text, rect, color=(0, 0, 0, 255), text_size=15,
                 centered=False, bold=False):
        super(Label, self).__init__(rect.size, rect.x, rect.y)
        self.text, self.color = text, color
        self._font = pygame.font.Font("resources/fantasque.ttf", text_size)
        self._font.set_bold(bold)
        self.centered = centered

    def __repr__(self):
        return "Label <{0}>".format(self.text)

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        text = self._font.render(self.text, True, self.color)
        textpos = text.get_rect()
        if self.centered:
            textpos.center = self._image.get_rect().center
        self._image.blit(text, textpos)

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, new):
        self.__text = new
        self.state = Label.STATE_INVALID


class TextInputField(HoverableComponent):

    def __init__(self, rect, fg_color, bg_color, text_size=15, hint="",
                 hintcolor=None, do_submit=False):
        super(TextInputField, self).__init__(rect)
        self.text, self.fg_color, self.bg_color = [], fg_color, bg_color
        self._font = pygame.font.Font("resources/fantasque.ttf", text_size)
        self.cursor, self.max_len = 0, 50
        self.colors = {"bg": ((100, 100, 100, 255), bg_color),
                       "fg": ((0, 0, 0, 255), fg_color)}
        self.hint, self.hintcolor = hint, hintcolor if hintcolor is not None\
            else fg_color
        self.requests_focus, self.do_submit = True, do_submit

    def __repr__(self):
        return "TextInputField <{}>".format(self.text)

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        draw_roundrect(self._image, self._image.get_rect(), self._bgcolor())
        if len(self.text) == 0:
            text = self._font.render(self.hint, True, self.hintcolor)
        else:
            try:
                text = self._font.render(self.text, True, self._fgcolor())
            except ValueError:
                self.text = ""
                text = self._font.render(self.hint, True, self.hintcolor)
        if self.focussed:
            # draw cursor
            x_pos = self._font.size("".join(self.text[:self.cursor]))[0]
            cursor_rect = (x_pos - 1, 0, 1,
                           text.get_rect().height)
            pygame.draw.rect(text, self._fgcolor(), cursor_rect)
        # move text to the left when text input field to small
        if text.get_rect().width > self.rect.width:
            text_pos = text.get_rect(right=self._image.get_rect().right)
        else:
            text_pos = self._image.get_rect()
        self._image.blit(text, text_pos)

    @property
    def text(self):
        return "".join(self.__text)

    @text.setter
    def text(self, new):
        if type(new) == str:
            new = list(new)
        self.__text = new
        self.cursor = len(new)
        self.state = UIComponent.STATE_INVALID

    @property
    def hint(self):
        return self.__hint

    @hint.setter
    def hint(self, new):
        self.__hint = new
        self.state = UIComponent.STATE_INVALID

    def key_typed(self, key):
        self.state = UIComponent.STATE_INVALID
        if key == pygame.K_RETURN:
            if not self.do_submit:
                return
            self.on_submit(self.text)
            self.text = ""
        elif key == pygame.K_BACKSPACE:
            try:
                if self.cursor > 0:
                    del self.__text[self.cursor - 1]
                    self.cursor -= 1
            except IndexError:
                pass  # index out of bounds
        elif key == pygame.K_LEFT:
            self.cursor = max(0, self.cursor - 1)
        elif key == pygame.K_RIGHT:
            self.cursor = min(len(self.__text), self.cursor + 1)
        elif key <= 127:
            self.__text.insert(self.cursor, chr(key))
            self.cursor += 1

    def on_submit(self, text):
        pass


class TextInputWidget(UIWidget):

    def __init__(self, rect, label_text, fg_color, bg_color, text_size=15,
                 hint="", hintcolor=None):
        super(TextInputWidget, self).__init__(rect)

        label_rect = pygame.Rect(0, 0, self.rect.width * 0.4,
                                 self.rect.height)
        in_height = label_rect.height * 0.8
        in_rect = pygame.Rect(label_rect.right,
                              label_rect.centery - in_height / 2,
                              self.rect.width * 0.5,
                              in_height)
        label = Label(label_text, label_rect, fg_color, text_size)
        self.add(label)
        self.in_field = TextInputField(in_rect, fg_color, bg_color, text_size,
                                       hint, hintcolor)
        self.add(self.in_field)

    @property
    def text(self):
        return self.in_field.text

    @text.setter
    def text(self, new):
        self.in_field.text = new


class ListView(UIComponent):

    def __init__(self, rect, color, entries=None, text_size=15):
        super(ListView, self).__init__(rect.size, rect.x, rect.y)
        if not entries:
            entries = []
        self.entries = entries
        self.color = color
        self._font = pygame.font.Font("resources/fantasque.ttf", text_size)
        self.line_height = self._font.size("Gj")[1] * 1.1

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        for idx, entry in enumerate(self.entries):
            text = self._font.render(entry, True, self.color)
            text_pos = text.get_rect(top=idx * self.line_height)
            self._image.blit(text, text_pos)

    def add(self, entry):
        self.entries.append(entry)
        self.state = UIComponent.STATE_INVALID

    def remove(self, entry):
        self.entries.remove(entry)
        self.state = UIComponent.STATE_INVALID

    @property
    def entries(self):
        return self.__entries

    @entries.setter
    def entries(self, new):
        self.__entries = new
        self.state = UIComponent.STATE_INVALID


class ChatListView(ListView):

    STATE_SCROLLED = 2
    SCROLL_FACTOR = 20

    def __init__(self, rect, color, text_size=15):
        super(ChatListView, self).__init__(rect, color, text_size=text_size)
        self.shifted = 0
        self.max_shift = 0

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        current_y = self.rect.bottom + self.shifted
        self.max_shift = -self.rect.height
        for entry in reversed(self.entries):
            # text = self._font.render(entry, True, self.color)
            text = fonthelper.render_text(entry, self._font, self.color,
                                          self.rect.width)
            text_pos = text.get_rect(bottom=current_y)
            current_y = text_pos.top
            self._image.blit(text, text_pos)
            self.max_shift += text_pos.height

    def shift_list(self, frames, count=1):
        pass

    def scrolled(self, d):
        self.shifted = max(0,
                           min(self.max_shift, self.shifted + d *
                               ChatListView.SCROLL_FACTOR))
        self.state = ChatListView.STATE_INVALID

    @property
    def image(self):
        image = super(ChatListView, self).image
        if self.state == ChatListView.STATE_SCROLLED:
            return image
        return image


class ChatSelector(Button):

    def __init__(self, *args, **kwargs):
        super(ChatSelector, self).__init__(*args, **kwargs)
        self.chat_selected = False
        self.requests_focus = True

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        draw_halfroundrect(self._image, self._image.get_rect(),
                           self._bgcolor(), orientation=1)
        text = self._font.render(self.text, True, self._fgcolor())
        textpos = text.get_rect()
        textpos.center = self._image.get_rect().center
        self._image.blit(text, textpos)

    @property
    def chat_selected(self):
        return self.__chat_selected

    @chat_selected.setter
    def chat_selected(self, new):
        self.__chat_selected = new
        self._ignore = new
        self._color_rev = new
        self.state = ChatSelector.STATE_INVALID

    def clicked(self, event):
        self.on_select(self.text)

    def on_select(self, text):
        pass


class ChatWidget(UIWidget):

    STATE_VISIBLE, STATE_INVISIBLE = 0, 1

    def __init__(self, rect, fg_color, send, own_name, text_size=15):
        super(ChatWidget, self).__init__(rect)
        self.real_rect = self.rect.copy()
        self.fg_color = fg_color
        self._font = pygame.font.Font("resources/fantasque.ttf", text_size)

        self.selection_rect = pygame.Rect(0, 0, self.rect.width * 0.2,
                                          self.rect.height)
        self.chat_rect = pygame.Rect(self.selection_rect.right,
                                     self.selection_rect.top,
                                     self.rect.width -
                                     self.selection_rect.width,
                                     self.rect.height)
        print("selection", self.selection_rect, "chat", self.chat_rect)

        list_rect = pygame.Rect(self.chat_rect.x,
                                self.chat_rect.y,
                                self.chat_rect.width,
                                self.chat_rect.height * 0.9)
        self.chat_list = ChatListView(list_rect, fg_color, text_size=text_size)
        self.add(self.chat_list)

        enter_rect = pygame.Rect(self.chat_rect.x + self.chat_rect.width * 0.1,
                                 self.chat_rect.height * 0.9,
                                 self.chat_rect.width * 0.8,
                                 self.chat_rect.height * 0.1)
        enter_field = TextInputField(enter_rect, (255, 255, 255, 255),
                                     (40, 40, 40, 255), 30, hint="Enter text",
                                     do_submit=True)
        enter_field.on_submit = self.on_chat
        self.add(enter_field)
        self.status = ChatWidget.STATE_VISIBLE
        self.send = send
        self.chat = Chat(self.chat_list)
        self.own_name = own_name
        self.buttons = []

    def setup_selectors(self, options):
        options.insert(0, "global")
        height = self.selection_rect.height * 0.1
        self.ui_components.remove(*self.buttons)
        self.buttons = []
        current_y = self.selection_rect.height * 0.1
        # existing = [btn.text for btn in self.buttons]
        if self.chat.current not in options:
            self.chat.current = "global"
        for option in options:
            # if option in existing:
                # continue
            btn_rect = pygame.Rect(self.selection_rect.x,
                                   current_y,
                                   self.selection_rect.width,
                                   height)
            btn = ChatSelector(option, btn_rect, text_size=15)
            btn.parent = self
            btn.on_select = self.select_chat
            self.buttons.append(btn)
            self.ui_components.add(btn)
            current_y = btn_rect.bottom
            if option == self.chat.current:
                btn.chat_selected = True
        self.state = ChatWidget.STATE_INVALID

    def select_chat(self, text):
        try:
            old = next(b for b in self.buttons if b.text == self.chat.current)
            old.chat_selected = False
        except StopIteration:
            print("Error: Old button not found")
        try:
            self.chat.current = text
            new = next(b for b in self.buttons if b.text == text)
        except StopIteration:
            print("Error: New not found")
            self.chat.current = "global"
            new = next(b for b in self.buttons if b.text == self.chat.current)
        finally:
            new.chat_selected = True

    def draw(self):
        self._image.fill((0, 0, 0, 0))
        draw_halfroundrect(self._image, self.chat_rect,
                           (255, 255, 255, 255), radius=0.2)
        self.ui_components.draw(self._image)

    def on_chat(self, text):
        self.send(text, self.chat.current)
        self.chat.add(self.chat.current, "{}: {}".format(self.own_name, text))

    def on_recv(self, mode, text, from_user):
        print("receive chat", mode, text, from_user)
        text = "{}: {}".format(from_user, text)
        if mode == "global":
            self.chat.add("global", text)
        else:
            self.chat.add(from_user, text)

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, new):
        self.__status = new
        if new == ChatWidget.STATE_VISIBLE:
            top = self.real_rect.top
            self.move_to(self.rect.x, top, 15)
        elif new == ChatWidget.STATE_INVISIBLE:
            top = self.real_rect.top + self.rect.height * 0.9
            self.move_to(self.rect.x, top, 15)
        self.state = ChatWidget.STATE_INVALID

    def clicked(self, event):
        self.status = ChatWidget.STATE_INVISIBLE\
            if self.status == ChatWidget.STATE_VISIBLE else\
            ChatWidget.STATE_VISIBLE


class Chat:

    def __init__(self, chat_view):
        self.view = chat_view
        self.chat_konv = {}
        self.current = "global"

    def add(self, from_user, text):
        if from_user not in self.chat_konv:
            self.chat_konv[from_user] = []
        self.chat_konv[from_user].append(text)
        if from_user == self.current:
            self.view.add(text)

    @property
    def current(self):
        return self.__current

    @current.setter
    def current(self, new):
        if hasattr(self, '__current') and new == self.__current:
            return
        self.__current = new
        if new not in self.chat_konv:
            self.view.entries = []
        else:
            self.view.entries = self.chat_konv[new].copy()
            self.view.shifted = 0
            self.view.state = UIComponent.STATE_INVALID


class QueueButton(UIWidget):

    def __init__(self, rect, join_func, leave_func):
        super(QueueButton, self).__init__(rect)
        self.join, self.leave = join_func, leave_func
        self.init_join()

    def init_join(self):
        print("initialise join view")
        btn_rect = self.rect.copy()
        btn_rect.x, btn_rect.y = 0, 0
        self.ui_components.empty()
        btn = Button("Join queue", btn_rect, text_size=30)
        btn.parent = self
        btn.clicked = self.join
        self.ui_components.add(btn)
        print("ui components", self.ui_components)
        self.state = UIComponent.STATE_INVALID

    def on_join(self):
        self.init_leave()

    def on_leave(self):
        self.init_join()

    def init_leave(self):
        self.ui_components.empty()
        lbl_rect = pygame.Rect(0, 0,
                               self.rect.width * 0.75,
                               self.rect.height)
        lbl = Label("Joined queue ...", lbl_rect, (0, 255, 0, 255),
                    text_size=20, centered=True)
        lbl.parent = self
        self.ui_components.add(lbl)

        size = min(self.rect.width * 0.2, self.rect.height)
        print("button size", size, self.rect.width * 0.2, self.rect.height)
        btn_rect = pygame.Rect(self.rect.width * 0.8,
                               (self.rect.height - size) / 2,
                               size, size)
        print("button rect", btn_rect)
        img = pygame.image.load("resources/cancel.png")

        btn = ImageButton(img, btn_rect)
        btn.parent = self
        btn.clicked = self.leave
        self.ui_components.add(btn)
        self.state = UIComponent.STATE_INVALID

    def join(self, *args):
        pass

    def leave(self, *args):
        pass


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


def draw_halfroundrect(surface, rect, color, radius=0.4,
                       orientation=0):
    draw_roundrect(surface, rect, color, radius)

    overlay_rect = rect.copy()
    if orientation == 0:
        overlay_rect.height *= 0.5
        overlay_rect.top += overlay_rect.height
    else:
        overlay_rect.width *= 0.5
        overlay_rect.right = rect.right
    pygame.draw.rect(surface, color, overlay_rect)


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
        gamelog_rownumber = int(self.gamelog_size[1] / 30)  # ypos of first col
        current_row = -1  # watch out, needs to start with -1
        index = 0  # watch out, needs to start with 0
        for i in range(0, len(self.turnlist)):
            new_text = self.turnlist[i]
            font = pygame.font.Font("resources/fantasque.ttf", 12)
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
