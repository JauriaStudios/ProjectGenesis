import os

import pygame

from typing import List

from .const import ROOT_PATH, RESOURCE_PATH
from .sprite_sheet import SpriteStripAnim


class Item(pygame.sprite.Sprite):

    def __init__(self, image, position, frame_speed):
        super(Item, self).__init__()

        self.name = image
        self.image_path = os.path.join(RESOURCE_PATH, "items", f"{self.name}.png")
        self.width = 16
        self.height = 16

        self.player_inside = False
        self.power_item = SpriteStripAnim(self.image_path, (0, 0, self.width, self.height), 4, -1, True, frame_speed)

        self.image = self.power_item.images[0]
        self.rect = self.image.get_rect()

        self._position = (position[0]-self.width/2, position[1]-self.height/2)
        self._old_position = self.position

        self.rect.topleft = self._position

    @property
    def position(self) -> List[float]:
        return list(self._position)

    @position.setter
    def position(self, value: List[float]) -> None:
        self._position = list(value)

    def get_rect(self):
        return pygame.Rect(self.warp.x,
                           self.warp.y,
                           self.warp.width,
                           self.warp.height)

    def update(self, dt: float) -> None:
        self.image = self.power_item.next()
