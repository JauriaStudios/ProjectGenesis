import os
from collections import OrderedDict
from typing import List

import time
import pygame

from constants import RESOURCE_DIR, ROOT_PATH
from projectile import Projectile
from sprite_sheet import SpriteStripAnim


class Player(pygame.sprite.Sprite):
    """Player

    """

    def __init__(self, game, image) -> None:
        super(Player, self).__init__()

        self.shooting = False
        self.run_attack_action = False
        self.animation_action_frame = 0
        self.game = game

        self.current_ticks = 0
        self.prev_ticks = 0
        self.ticks_interval = 60  # 1 second / 60 fps

        self.image_path = os.path.join(ROOT_PATH, RESOURCE_DIR, "sprites", image)

        self.width = 64
        self.height = 64

        frame_speed = 60

        # self.sprite_sheet = SpriteSheet(self.image_path)

        self.anim_effect_up = SpriteStripAnim(self.image_path, (0, self.width*0, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_left = SpriteStripAnim(self.image_path, (0, self.width*1, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_down = SpriteStripAnim(self.image_path, (0, self.width*2, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_right = SpriteStripAnim(self.image_path, (0, self.width*3, self.width, self.height), 7, -1, False, frame_speed)

        self.anim_up = SpriteStripAnim(self.image_path, (0, self.width*8, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_left = SpriteStripAnim(self.image_path, (0, self.width*9, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_down = SpriteStripAnim(self.image_path, (0, self.width*10, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_right = SpriteStripAnim(self.image_path, (0, self.width*11, self.width, self.height), 8, -1, True, frame_speed)

        self.anim_action_up = SpriteStripAnim(self.image_path, (0, self.width*12, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_left = SpriteStripAnim(self.image_path, (0, self.width*13, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_down = SpriteStripAnim(self.image_path, (0, self.width*14, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_right = SpriteStripAnim(self.image_path, (0, self.width*15, self.width, self.height), 6, -1, False, frame_speed)

        self.anim_effect = OrderedDict()
        self.anim_walk = OrderedDict()
        self.anim_action = OrderedDict()

        self.anim_effect["UP"] = self.anim_effect_up
        self.anim_effect["LEFT"] = self.anim_effect_left
        self.anim_effect["DOWN"] = self.anim_effect_down
        self.anim_effect["RIGHT"] = self.anim_effect_right

        self.anim_walk["UP"] = self.anim_up
        self.anim_walk["LEFT"] = self.anim_left
        self.anim_walk["DOWN"] = self.anim_down
        self.anim_walk["RIGHT"] = self.anim_right

        self.anim_action["UP"] = self.anim_action_up
        self.anim_action["LEFT"] = self.anim_action_left
        self.anim_action["DOWN"] = self.anim_action_down
        self.anim_action["RIGHT"] = self.anim_action_right

        self.image = self.anim_down.images[0]

        self.direction = "DOWN"
        self.facing = 0

        self.velocity = [0, 0]
        self._position = [0.0, 0.0]
        self._old_position = self.position

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 8)

    @property
    def position(self) -> List[float]:
        return list(self._position)

    @position.setter
    def position(self, value: List[float]) -> None:
        self._position = list(value)

    def update(self, dt: float) -> None:
        self._old_position = self._position[:]

        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt

        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

        if self.velocity[0] > 0 and self.velocity[1] > 0:
            self.direction = "DOWN"  # DOWN RIGHT
            self.facing = 7
            self.image = self.anim_right.next()
            # print(f"move DOWN RIGHT {self.direction}")

        elif self.velocity[0] < 0 and self.velocity[1] < 0:
            # print("DIAGONAL UP LEFT")
            self.direction = "LEFT"  # UP LEFT
            self.facing = 3
            self.image = self.anim_left.next()
            # print(f"move UP LEFT {self.direction}")

        elif self.velocity[0] > 0 and self.velocity[1] < 0:
            self.direction = "RIGHT"  # UP RIGHT
            self.facing = 5
            self.image = self.anim_right.next()
            # print(f"move UP RIGHT {self.direction}")

        elif self.velocity[0] < 0 and self.velocity[1] > 0:
            # print("DIAGONAL DOWN LEFT")
            self.direction = "LEFT"  # DOWN LEFT
            self.facing = 1
            self.image = self.anim_left.next()
            # print(f"move DOWN LEFT {self.direction}")

        elif self.velocity[0] < 0:
            self.direction = "LEFT"  # LEFT
            self.facing = 2
            self.image = self.anim_left.next()
            # print(f"move LEFT {self.direction}")

        elif self.velocity[0] > 0:
            self.direction = "RIGHT"  # RIGHT
            self.facing = 6
            self.image = self.anim_right.next()
            # print(f"move RIGHT {self.direction}")

        elif self.velocity[1] > 0:
            self.direction = "DOWN"  # DOWN
            self.facing = 0
            self.image = self.anim_down.next()
            # print(f"move DOWN {self.direction}")

        elif self.velocity[1] < 0:
            self.direction = "UP"  # UP
            self.facing = 4
            self.image = self.anim_up.next()
            # print(f"move UP {self.direction}")
        elif self.run_attack_action is False:
            self.image = self.anim_walk[self.direction].images[0]

        if self.run_attack_action:
            self.current_ticks += dt * 1000

            if self.current_ticks - self.prev_ticks > self.ticks_interval:

                if (self.shooting is True) and (self.animation_action_frame == 3):
                    self.shoot()
                    self.shooting = False
                elif self.animation_action_frame < 5:
                    # if (self.direction == 6) and (self.facing == 2):
                    #     self.image = pygame.transform.flip(self.image, self.mirror, False)

                    self.image = self.anim_action[self.direction].images[self.animation_action_frame]

                    self.animation_action_frame += 1
                    print(f"Play frame {self.animation_action_frame} in direction = {self.direction} facing {self.facing}")
                else:
                    self.animation_action_frame = 0
                    self.run_attack_action = False
                    print("animation end")

                self.prev_ticks = self.current_ticks

    def move_back(self, dt: float) -> None:
        """If called after an update, the sprite can move back"""
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

    def shoot(self):
        projectile = Projectile(self)
        self.game.add_bullet(projectile)

    def attack(self):
        self.shooting = True
        self.run_attack_action = True

    def action(self):
        self.run_attack_action = True

    def get_rect(self):
        return self.rect
