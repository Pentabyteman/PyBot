# MAIN FILE
modules = ["pygame v1.9", "sysconfig", "time", "tkinter"]

importstring = """Python was unable to import some important modules.
Be sure to have all necessary packages installed. Type help('modules')
in your shell if you are not sure which packages you have installed.
Required modules: {}""".format(modules)

working_version = '3.5'  # change to current version
namestring = """This app is only launchable with Python {},
please download this version of Python""".format(working_version)

# Loads of Error Handling if some idiots mess up with everything,,,
try:
    # outside modules
    import pygame
    import time
    import sysconfig
    import tkinter
    # local files
    import board
    import gui
    from app import App
except ImportError:
    raise ImportError(importstring)
except Exception as e:
    print("Unkonw Error: {}".format(e))

# correct version of python?
if sysconfig.get_python_version() != working_version:
    raise NameError(namestring)

BOARD_SIZE = (1017, 1017)  # quadratisch praktisch gut
WINDOW_SIZE = (1500, 1017)  # enough space for gui


class Game(App):

    def __init__(self, display):
        super(Game, self).__init__()
        self.display = display

        self.board = board.Board(BOARD_SIZE,
                                 on_finish=self.stop)
        self.window = gui.GameWindow(WINDOW_SIZE, BOARD_SIZE, self.board,
                                     on_finish=self.stop)
        self.last_time = time.time()

    def on_event(self, event):
        self.board.on_event(event)
        self.window.update(event)

    def on_tick(self):
        """Called every tick"""
        # delays the turns a little bit to give the players the opportunity
        # to view the turns of their robots
        if (time.time() - self.last_time) > 2:
            self.board.on_turn()
            self.last_time = time.time()

    def on_render(self):
        self.display.fill((255, 255, 255))
        self.display.blit(self.window.draw(), (0, 0))  # blit board
        pygame.display.flip()  # update screen


if __name__ == '__main__':

    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.load('bensound-pianomoment.mp3')
    pygame.mixer.music.play(-1)  # plays infinite loop
    display = pygame.display.set_mode(WINDOW_SIZE)  # setup display
    game = Game(display)
    game.exec_()
    pygame.mixer.music.fadeout(5000)
    pygame.time.wait(5000)
    pygame.mixer.quit()
    pygame.quit()
