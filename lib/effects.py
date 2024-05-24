import os

import pygame

from typing import List

from .const import ROOT_PATH, RESOURCE_PATH
from .sprite_sheet import SpriteStripAnim


class PurpleImpact(pygame.sprite.Sprite):

    def __init__(self, image, position, frame_speed):
        super(PurpleImpact, self).__init__()

        self.name = image
        self.image_path = os.path.join(RESOURCE_PATH, "effects", f"{self.name}.png")
        self.width = 32
        self.height = 32

        self.speed = 6
        self.impact_anim = SpriteStripAnim(self.image_path, (0, 0, self.width, self.height), 4, -1, True, frame_speed)

        self.image = self.impact_anim.images[0]
        self.rect = self.image.get_rect()



        self.velocity = [0, 0]
        self._position = (position[0], position[1])
        self._old_position = self.position

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 8)

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
        self.image = self.impact_anim.next()
