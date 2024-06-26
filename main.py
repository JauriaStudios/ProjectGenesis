import os
from collections import deque
import oyaml as yaml

import pygame
import pygame_gui

from pygame import KEYDOWN
from pygame.locals import K_ESCAPE
from pygame.locals import QUIT

from lib.const import ROOT_PATH, RESOURCE_PATH, SCREEN_SIZE
from lib.music_list import MusicList
from lib.menu import Menu
from lib.field import Field


def init_screen(size: list) -> pygame.Surface:
    flags = pygame.HWSURFACE | pygame.SCALED | pygame.FULLSCREEN
    screen = pygame.display.set_mode(size, flags=flags)
    return screen


class Game:
    """This class is a basic game.
    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """

    def __init__(self, screen: pygame.Surface, manager) -> None:
        self.screen = screen
        self.fps = 60
        self.music_list = MusicList()

        self.manager = manager
        self.running = False
        self.mode = "MENU"
        self.current_ticks = 0
        self.loading_screen = False
        self.loading_start = 0
        self.loading_end = 2 * 1000  # 4 secs for loading screen
        self.shooting = False

        with open(os.path.join(ROOT_PATH, RESOURCE_PATH, "menu", "main.yml")) as fh:
            menu_options = yaml.load(fh, Loader=yaml.FullLoader)

        self.menu = Menu(menu_options, self.music_list)

        with open(os.path.join(ROOT_PATH, RESOURCE_PATH, "menu", "loading_page.yml")) as fh:
            loading_options = yaml.load(fh, Loader=yaml.FullLoader)

        self.loading = Menu(loading_options, self.music_list)

        self.field = Field(self, "stage2.0", self.screen.get_size(), self.music_list)

    def draw(self, dt) -> None:
        if self.mode == "LOADING":
            self.loading.draw(self.screen, dt)
        elif self.mode == "MENU":
            self.menu.draw(self.screen, dt)
        elif self.mode == "GAME":
            self.field.draw(self.screen, dt)
            self.manager.draw_ui(self.screen)

    def handle_input(self, dt) -> None:
        """Handle pygame input events"""
        poll = pygame.event.poll

        event = poll()

        while event:
            if event.type == QUIT:
                self.running = False
                break

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.running = False
                    break

            if self.mode == "MENU":
                self.menu.handle_input(event)
            elif self.mode == "GAME":
                self.field.handle_input(event)
                self.manager.process_events(event)

            # this will be handled if the window is resized
            # elif event.type == VIDEORESIZE:
            #     self.screen = init_screen(event.w, event.h)
            #     self.map_layer.set_size((event.w, event.h))

            event = poll()

    def update(self, dt):
        """Tasks that occur over time should be handled here"""
        if self.mode == "MENU":
            self.menu.update(dt)
            option = self.menu.get_mode()
            if option == 1:  # START
                self.mode = "LOADING"
                self.loading_screen = True
            elif option == 2:
                pass
            elif option == 3:
                self.running = False
        elif self.mode == "LOADING":
            self.current_ticks += dt * 1000
            if self.loading_screen is True:
                self.loading_start = self.current_ticks
                self.loading_screen = False
            if self.current_ticks - self.loading_start > self.loading_end:
                self.mode = "GAME"
                self.loading_start = 0
            self.loading.update(dt)
        elif self.mode == "GAME":
            self.field.update(dt)
            self.manager.update(dt)

    def run(self):
        """Run the game loop"""
        clock = pygame.time.Clock()
        self.running = True

        times = deque(maxlen=self.fps)

        try:
            while self.running:
                dt = clock.tick(self.fps) / 1000
                times.append(clock.get_fps())

                self.handle_input(dt)
                self.update(dt)
                self.draw(dt)

                pygame.display.flip()
                pygame.display.update()

        except KeyboardInterrupt:
            self.running = False
        except Exception as e:
            print(e)


def main() -> None:

    pygame.init()
    pygame.font.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    if joysticks:
        print("Joystick found:")

        for joystick in joysticks:
            print(f"\t1{joystick.get_name()}")

    screen = init_screen(SCREEN_SIZE)
    screen.fill(pygame.Color('#000000'))

    pygame.display.set_caption("Project Genesis")

    theme_path = os.path.join(RESOURCE_PATH, "hud", "theme.json")
    manager = pygame_gui.UIManager(SCREEN_SIZE, theme_path=theme_path)

    font_path = os.path.join(RESOURCE_PATH, "fonts", "PressStart2P-Regular.ttf")
    manager.add_font_paths("Press Start 2P", font_path)

    # fonts = [
    #     {"name": "press_start_12", "point_size": 12, "style": "regular"},
    #     {"name": "press_start_14", "point_size": 14, "style": "regular"},
    #     {"name": "press_start_18", "point_size": 18, "style": "regular"}
    # ]
    #
    # manager.preload_fonts(fonts)
    try:
        game = Game(screen, manager)
        game.run()

    except KeyboardInterrupt:
        pass

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
