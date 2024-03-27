
import os

import pygame
from lib.constants import ROOT_PATH, RESOURCE_DIR, RED, WHITE

# from cursor import Cursor
from lib.text_sprite import TextSprite
# from dialog import Dialog

from pygame import JOYAXISMOTION, KEYUP, JOYBUTTONDOWN, JOYBUTTONUP, KEYDOWN, KEYUP
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_MINUS, K_PLUS, K_ESCAPE, K_BACKSPACE, K_RETURN
# from pygame.locals import QUIT


class Menu:
    def __init__(self, options, music):

        self.options = options
        self.music = music
        self.index = None
        # self.cursor = Cursor(400, 400, 3, 50)

        self.current_ticks = 0
        self.prev_ticks = 0
        self.ticks_interval = 444  # 1 second / 60 fps
        self.text_visible = True

        self.sprite_group = pygame.sprite.Group()

        # self.dialog = Dialog(380, 350, 240, 180)

        # self.sprite_group.add(self.dialog)
        self.background = None
        self.num_options = 1

        for name, menu in self.options.items():
            for key, option in menu.items():
                if key == "background" and option != "":
                    self.image_path = os.path.join(ROOT_PATH, RESOURCE_DIR, "menu", option)
                    self.background = pygame.image.load(self.image_path)
                elif isinstance(option, dict):
                    self.num_options += 1
                    text = TextSprite(option)
                    self.sprite_group.add(text)

        # self.sprite_group.add(self.cursor)

        # self.music.change_music(0)
        # self.music.play_music()

    def draw(self, screen, dt):
        self.current_ticks += dt * 1000

        if self.background:
            screen.blit(self.background, (0, 0))

        if self.current_ticks - self.prev_ticks > self.ticks_interval:
            self.prev_ticks = self.current_ticks
            self.text_visible ^= True

        if self.text_visible is True:
            self.sprite_group.draw(screen)
        # print("MENU DRAW")

    def update(self, dt):

        self.sprite_group.update(dt)

        # print("MENU DT")
    def handle_input(self, event):

        # if event.type == JOYAXISMOTION:
        #     if event.axis == 1:  # Y Axis = 1
        #         if round(event.value) == -1.0:
        #             self.cursor.move_up()
        #         elif round(event.value) == 1.0:
        #             self.cursor.move_down()
        # elif event.type == JOYBUTTONDOWN:
        if event.type == JOYBUTTONDOWN:

            # if event.button == 1:
            #     self.index = self.cursor.get_position()
            # elif event.button == 0:
            #     self.index = self.cursor.get_position()
            self.index = 1
        elif event.type == JOYBUTTONUP:
            if event.button == 2:
                pass

        elif event.type == KEYDOWN:
            # if event.key == K_UP:
            #     self.cursor.move_up()
            #
            # elif event.key == K_DOWN:
            #     self.cursor.move_down()

            # elif event.key == K_RETURN:
            if event.key == K_RETURN:
                # self.index = self.cursor.get_position()
                self.index = 1

    def get_mode(self):
        return self.index
