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
    import sysconfig
    import gui
    from app import App
    # outside modules
    import pygame
    import time
    import sys
    # local files
except ImportError:
    raise ImportError(importstring)
except Exception as e:
    print("Unknown Error: {}".format(e))

# correct version of python?
if sysconfig.get_python_version() != working_version:
    raise NameError(namestring)

BOARD_SIZE = (1017, 1017)  # quadratisch praktisch gut
WINDOW_SIZE = (1500, 1017)  # enough space for gui
volume = 0.5

class Game(App):

    def __init__(self, display, ai1=None, ai2=None, start=None, speed=False):
        super(Game, self).__init__()
        self.display = display

        self.window = gui.GameWindow(WINDOW_SIZE, BOARD_SIZE,
                                     on_finish=self.stop,
                                     ai1=ai1, ai2=ai2,
                                     start=start, speed=speed)
        self.last_time = time.time()

    def on_event(self, event):
        self.window.update(event)

    def on_tick(self):
        """Called every tick"""
        self.window.on_tick()

    def on_render(self):
        self.display.fill((255, 255, 255))
        self.display.blit(self.window.draw(), (0, 0))  # blit board
        pygame.display.flip()  # update screen


if __name__ == '__main__':

    display = pygame.display.set_mode(WINDOW_SIZE)  # setup display
    # debug: --debug <ai1> <ai2> <starting_team> <speed (0 / 1)>
    speed, debug = False, False
    if "--debug" in sys.argv:
        try:
            ai1, ai2 = sys.argv[2:4]
            start = int(sys.argv[4])
            speed = int(sys.argv[5]) == 1
            game = Game(display, ai1=ai1, ai2=ai2, start=start, speed=speed)
            debug = True
            volume = int(sys.argv[6])*volume
        except:
            print("There is an error in your syntax! Starting normally!")
            game = Game(display)
    else:
        game = Game(display)

    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.load('resources/bensound-pianomoment.mp3')
    pygame.mixer.music.play(-1)  # plays infinite loop
    game.exec_()

    delay = 5000 if not debug else 10
    pygame.mixer.music.fadeout(delay)
    pygame.time.wait(delay)
    pygame.mixer.quit()
    pygame.quit()
