import os

import pygame
import pygame_gui
from pygame_gui.core import ObjectID
from pygame_gui.elements.ui_text_box import UITextBox

from typing import List
from lib.const import RESOURCE_PATH, ROOT_PATH, SCREEN_SIZE


class TextBox:
    def __init__(self, game, html_text, font_name=None):
        super().__init__()
        self.game = game
        self.manager = self.game.manager
        self.screen = self.game.screen
        self.visible = False
        self.html_text = html_text
        self.font = os.path.join(RESOURCE_PATH, "fonts", "PressStart2P-Regular.ttf")
        self.font = font_name
        self.text_box = UITextBox(
                html_text=self.html_text,
                relative_rect=pygame.Rect(SCREEN_SIZE[0]/2-350/2, SCREEN_SIZE[1]/2-360/2, 350, 360),
                manager=self.manager)

        # self.text_box.scroll_bar.has_moved_recently = False
        self.text_box.update(5.0)
        self.text_box.visible = False

    def update(self, dt):
        if self.text_box.visible:
            self.manager.draw_ui(window_surface=self.screen)

    def show_dialog(self, visible):
        self.text_box.visible = visible
