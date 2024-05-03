import os

import pygame

from typing import List

from .const import ROOT_PATH, RESOURCE_PATH
from .sprite_sheet import SpriteStripAnim


class Item(pygame.sprite.Sprite):

    def __init__(self, image, position, frame_speed):
        super(Item, self).__init__()

        # self.warp = warp
        # for name, property in self.warp.properties.items():
        #     print(name, property)
        self.image_name = image
        self.image_path = os.path.join(RESOURCE_PATH, self.image_name)

       # self.map_name = self.warp.properties.get("Map")

        self.player_inside = False

        #self.image_path = os.path.join(ROOT_PATH, RESOURCE_DIR, "sprites", image)

        self.width = 33
        self.height = 74

        self.item_anim_up = SpriteStripAnim(self.image_path, (0, 0, self.width, self.height), 1, -1, True, frame_speed)

        self.image = self.item_anim_up.images[0]
        self.rect = self.image.get_rect()

        self._position = (position[0], position[1])
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

    def go_inside(self, player):
        # print("IN")
        self.player_inside = True

    def go_outisde(self):
        # print("OUT")
        self.player_inside = False

    def get_player(self):
        return self.player_inside

    def get_warp_map(self):
        return self.map_name

    def update(self, dt: float) -> None:

        self.image = self.item_anim_up.next()
