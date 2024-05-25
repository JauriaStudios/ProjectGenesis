import os
from typing import List

import pygame


from lib.const import RESOURCE_PATH
from lib.sprite_sheet import SpriteStripAnim


class Projectile(pygame.sprite.Sprite):
    """Projectile

    """

    def __init__(self, player, game, owner, bullet_vector=None ):
        super(Projectile, self).__init__()

        self.game = game
        self.owner = owner
        self.player = player

        self.name = "note1"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.image_path = os.path.join(base_dir, RESOURCE_PATH, "shoots", f"{self.name}.png")
        self.rotation = 0
        self.rotation_speed = 20

        self.x = self.player.position[0] + self.player.rect.width * 0.5
        self.y = self.player.position[1] + self.player.rect.height * 0.5

        self.duration = 1 * 1000  # second * 1000 millis
        self.prev_ticks = 0
        self.current_ticks = 0

        self.width = 32
        self.height = 32

        self.speed = 30
        frame_speed = 7

        self.shoot_anim = SpriteStripAnim(self.image_path, (0, 0, self.height, self.width), 5, -1, True, frame_speed)

        self.image = self.shoot_anim.images[0]

        if bullet_vector is not None:
            self.velocity = bullet_vector
        else:
            if player.direction == "RIGHT":
                self.velocity = [self.speed, 0]
            elif player.direction == "LEFT":
                self.velocity = [-self.speed, 0]
            elif player.direction == "UP":
                self.velocity = [0, -self.speed]
            elif player.direction == "DOWN":
                self.velocity = [0, self.speed]

        self._position = [self.x, self.y]
        self._old_position = self.position

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 8)

    @property
    def position(self) -> List[float]:
        return list(self._position)

    @position.setter
    def position(self, value: List[float]) -> None:
        self._position = list(value)

    # THE MAIN ROTATE FUNCTION
    def rot(self):
        self.image = pygame.transform.rotate(self.image, self.rotation)
        self.rotation += self.rotation_speed
        self.rotation = self.rotation % 360
        self.rect = self.image.get_rect(center=self.rect.center)

    def update(self, dt: float) -> None:

        self.current_ticks += dt * 1000
        print("SPRITE START")

        if self.current_ticks - self.prev_ticks >= self.duration:
            self.prev_ticks = self.current_ticks
            print("SPRITE FIN")
            self.game.remove_bullet(self)
            return

        self.image = self.shoot_anim.next()
        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * (dt * 10)
        self._position[1] += self.velocity[1] * (dt * 10)
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
        self.rot()

    def move_back(self, dt: float) -> None:
        """If called after an update, the sprite can move back"""
        self.image = self.shoot_anim.images[0]
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom
