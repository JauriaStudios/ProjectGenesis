import os

from collections import deque

import oyaml as yaml

import pygame

from pygame import JOYAXISMOTION, KEYUP, JOYBUTTONDOWN, JOYBUTTONUP, KEYDOWN, KEYUP
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_MINUS, K_PLUS, K_ESCAPE, K_BACKSPACE
from pygame.locals import VIDEORESIZE, QUIT

from constants import ROOT_PATH, RESOURCE_DIR, RED, GRAY

from music_list import MusicList
from menu import Menu
from field import Field


def init_screen(width: int, height: int) -> pygame.Surface:
    flags = pygame.HWSURFACE | pygame.SCALED | pygame.FULLSCREEN
    screen = pygame.display.set_mode((width, height), flags=flags)
    return screen


class Game:
    """This class is a basic game.
    This class will load data, create a pyscroll group, a hero object.
    It also reads input and moves the Hero around the map.
    Finally, it uses a pyscroll group to render the map and Hero.
    """

    def __init__(self, screen: pygame.Surface) -> None:
        self.screen = screen
        self.music_list = MusicList()
        self.running = False
        self.mode = "MENU"
        self.shooting = False

        with open(os.path.join(ROOT_PATH, RESOURCE_DIR, "menu", "main.yml")) as fh:
            menu_options = yaml.load(fh, Loader=yaml.FullLoader)

        self.menu = Menu(menu_options, self.music_list)

        with open(os.path.join(ROOT_PATH, RESOURCE_DIR, "menu", "loading_page.yml")) as fh:
            loading_options = yaml.load(fh, Loader=yaml.FullLoader)

        self.loading = Menu(loading_options, self.music_list)

        self.field = Field("city2.tmx", self.screen.get_size(), self.music_list)

    def draw(self, dt) -> None:
        if self.mode == "LOADING":
            self.loading.draw(self.screen, dt)
        elif self.mode == "MENU":
            self.menu.draw(self.screen, dt)
        elif self.mode == "GAME":
            self.field.draw(self.screen, dt)

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
            if option == 1:
                self.mode = "LOADING"
            elif option == 2:
                pass
            elif option == 3:
                self.running = False
        elif self.mode == "LOADING":
            self.loading.update(dt)
        elif self.mode == "GAME":
            self.field.update(dt)

    def run(self):
        """Run the game loop"""
        clock = pygame.time.Clock()
        self.running = True

        times = deque(maxlen=60)

        try:
            while self.running:
                dt = clock.tick() / 1000
                times.append(clock.get_fps())

                self.handle_input(dt)
                self.update(dt)
                self.draw(dt)

                pygame.display.flip()

        except KeyboardInterrupt:
            self.running = False


def main() -> None:

    pygame.init()
    pygame.font.init()
    pygame.joystick.init()

    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

    if joysticks:
        print("Joystick found:")

    for joystick in joysticks:
        print(f"\t1 {joystick.get_name()}")

    screen = init_screen(1024, 768)
    pygame.display.set_caption("ProjectGenesis")

    try:
        game = Game(screen)
        game.run()

    except KeyboardInterrupt:
        pass

    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
