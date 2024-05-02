import os

import pygame

from typing import List


class Hud:

    def __init__(self, game):
        # self.image_name = self.player_icon
        # self.image = self.power_bar
        self.game = game
        self.player_icon = pygame.image.load("/hud/player.png")
        self.power_bar = pygame.image.load("/hud/bar_0_percent.png")

      #building hud
    def print_images(self, screen, rect=None):

        if self.game.mode == "GAME" :
            self.rect2 = self.player_icon.get_rect()
            self.rect2.center = 200, 150
            self.rect1 = self.power_bar.get_rect()
            self.rect1.center = 200, 150

            
             # scale images
             #self.player_icon = pygame.transform.scale(self.player_icon, (10, 10))
             #self.power_bar = pygame.transform.scale(self.power_bar, (10, 10))
        elif self.game.mode == "MENU":
            pass
            

    def update(self, dt: float) -> None:

        self.screen.blit(self.player_icon, self.power_bar, self.rect1, self.rect2)
