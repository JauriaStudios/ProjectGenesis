import os

import pygame

from typing import List
from lib.const import RESOURCE_PATH, ROOT_PATH

class Hud:

    def __init__(self, game):
        self.game = game

        self.image_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "player.png")
        self.power_bar_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "bar_0_percent.png")

        self.player_icon = pygame.image.load(self.image_path).convert_alpha()
        self.power_bar = pygame.image.load(self.power_bar_path).convert_alpha()

        self.player_rect = self.player_icon.get_rect()
        #self.rect2.center = 200, 150
        self.power_bar_rect = self.power_bar.get_rect()
        #self.rect1.center = 200, 150

    def update(self, dt: float) -> None:

        if self.game.mode == "FIELD":
            pass
            # self.game.screen.blit(self.player_icon, self.power_bar, self.rect1, self.rect2)
            # self.game.screen.blit(self.player_icon, (0, 0))
        elif self.game.mode == "MENU":
            pass
