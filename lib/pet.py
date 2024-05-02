import os
from collections import OrderedDict

import random
from typing import List

import pygame

from lib.const import ROOT_PATH, RESOURCE_PATH
from lib.projectile import Projectile
from lib.sprite_sheet import SpriteStripAnim
from lib.utils import Pid


class Pet(pygame.sprite.Sprite):
    """Pet

    """

    def __init__(self, game, player, name, x, y, width, height, follower=False, wanderer=False) -> None:
        super(Pet, self).__init__()

        self.interval = None
        self.current_time = None
        self.previous_time = 0

        self.game = game
        self.player = player

        self.image_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "sprites", f"{name}.png")

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.follower = follower
        self.wanderer = wanderer

        frame_speed = 10

        # self.sprite_sheet = SpriteSheet(self.image_path)

        self.anim_down = SpriteStripAnim(self.image_path, (0, 48*0, self.width, self.height), 3, -1, True, frame_speed)
        self.anim_left = SpriteStripAnim(self.image_path, (0, 48*1, self.width, self.height), 3, -1, True, frame_speed)
        self.anim_right = SpriteStripAnim(self.image_path, (0, 48*2, self.width, self.height), 3, -1, True, frame_speed)
        self.anim_up = SpriteStripAnim(self.image_path, (0, 48*3, self.width, self.height), 3, -1, True, frame_speed)

        self.anim_walk = OrderedDict()

        self.anim_walk["UP"] = self.anim_up
        self.anim_walk["LEFT"] = self.anim_left
        self.anim_walk["RIGHT"] = self.anim_right
        self.anim_walk["DOWN"] = self.anim_down

        self.image = self.anim_walk["DOWN"].images[0]

        self.direction = "DOWN"
        self.facing = 0
        self.mirror = False

        self.speed = 200

        self.velocity = [0, 0]
        self._position = [0.0, 0.0]
        self._old_position = self.position

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width * 0.5, 8)

        p = 10.0
        i = 5.0
        d = 10.0
        int_max = 3.0
        int_min = -3.0

        if self.follower:
            self.x_pid = Pid(p=p, i=i, d=d, derivator=0, integrator=0, integrator_max=int_max, integrator_min=int_min)
            self.y_pid = Pid(p=p, i=i, d=d, derivator=0, integrator=0, integrator_max=int_max, integrator_min=int_min)

    @property
    def position(self) -> List[float]:
        return list(self._position)

    @position.setter
    def position(self, value: List[float]) -> None:
        self._position = list(value)

    def update(self, dt: float) -> None:

        if self.follower:
            self.follow()
        elif self.wanderer:
            self.wander(dt)

        self._old_position = self._position[:]
        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

        if self.velocity[0] > 0 and self.velocity[1] > 0:
            # print("DIAGONAL DOWN RIGHT")
            self.direction = "RIGHT"  # DOWN RIGHT
            self.facing = 7
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[0] < 0 and self.velocity[1] < 0:
            # print("DIAGONAL UP LEFT")
            self.direction = "LEFT"  # UP LEFT
            self.facing = 3
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] > 0 and self.velocity[1] < 0:
            # print("DIAGONAL UP RIGHT")
            self.direction = "RIGHT"  # UP RIGHT
            self.facing = 5
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[0] < 0 and self.velocity[1] > 0:
            # print("DIAGONAL DOWN LEFT")
            self.direction = "LEFT"  # DOWN LEFT
            self.facing = 1
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] < 0:
            # print("LEFT")
            self.direction = "LEFT"  # LEFT
            self.facing = 2
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] > 0:
            # print("RIGHT")
            self.direction = "RIGHT"  # RIGHT
            self.facing = 6
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[1] < 0:
            # print("UP")
            self.direction = "UP"  # UP
            self.facing = 4
            self.mirror = False
            self.image = self.anim_walk["UP"].next()

        elif self.velocity[1] > 0:
            # print("DOWN")
            self.direction = "DOWN"  # DOWN
            self.facing = 0
            self.mirror = False
            self.image = self.anim_walk["DOWN"].next()

        else:
            self.image = self.anim_walk[self.direction].images[1]

    def follow(self):

        radius = 30
        # Check if position in X is greater than player position

        if self.position[0] < self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error > radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0

        elif self.position[0] > self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error < -radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0

        if self.position[1] < self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error > radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0

        elif self.position[1] > self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error < -radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0

    def move_back(self, dt: float) -> None:
        """If called after an update, the sprite can move back"""
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

    def shoot(self):
        projectile = Projectile(self)
        self.game.add_bullet(projectile)

    def wander(self, dt):

        self.current_time = pygame.time.get_ticks()

        self.interval = random.randint(1000, 10000)

        if self.current_time - self.previous_time >= self.interval:
            self.previous_time = self.current_time

            direction = random.randint(0, 4)
            if direction == 0:
                self.velocity[0] = -self.speed
            elif direction == 1:
                self.velocity[1] = -self.speed
            elif direction == 2:
                self.velocity[0] = self.speed
            elif direction == 3:
                self.velocity[1] = self.speed
            else:
                self.velocity[0] = 0
                self.velocity[1] = 0
