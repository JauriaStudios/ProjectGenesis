import math
import os
from collections import OrderedDict
from typing import List

import random

import pygame

from lib.const import RESOURCE_PATH, ROOT_PATH
from lib.projectile import Projectile
from lib.sprite_sheet import SpriteStripAnim
from lib.utils import Pid


class Enemy(pygame.sprite.Sprite):
    """Enemy

    """

    def __init__(self, game, player, name, enemy_id, x, y, width, height, follower=False, wanderer=False, level=0) -> None:
        super(Enemy, self).__init__()

        self.interval = None
        self.current_time = None
        self.previous_time = 0

        self.enemy_id = enemy_id

        self.shooting = False
        self.run_attack_action = False
        self.animation_action_frame = 0
        self.game = game

        self.current_ticks = 0
        self.prev_ticks = 0
        self.ticks_interval = 120  # 1 second / 60 fps

        self.player = player

        self.attacking = False

        self.image_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "sprites", f"{name}.png")

        self.x = x
        self.y = y

        self.width = width
        self.height = height

        self.follower = follower
        self.wanderer = wanderer
        self.level = level

        frame_speed = 6

        self.anim_effect_up = SpriteStripAnim(self.image_path, (0, self.width*0, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_left = SpriteStripAnim(self.image_path, (0, self.width*1, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_down = SpriteStripAnim(self.image_path, (0, self.width*2, self.width, self.height), 7, -1, False, frame_speed)
        self.anim_effect_right = SpriteStripAnim(self.image_path, (0, self.width*3, self.width, self.height), 7, -1, False, frame_speed)

        self.anim_attack_up = SpriteStripAnim(self.image_path, (0, self.height * 4, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_attack_left = SpriteStripAnim(self.image_path, (0, self.height * 5, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_attack_down = SpriteStripAnim(self.image_path, (0, self.height * 6, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_attack_right = SpriteStripAnim(self.image_path, (0, self.height * 7, self.width, self.height), 8, -1, True, frame_speed)

        self.anim_walk_up = SpriteStripAnim(self.image_path, (0, self.height*8, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_walk_left = SpriteStripAnim(self.image_path, (0, self.height*9, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_walk_down = SpriteStripAnim(self.image_path, (0, self.height*10, self.width, self.height), 8, -1, True, frame_speed)
        self.anim_walk_right = SpriteStripAnim(self.image_path, (0, self.height*11, self.width, self.height), 8, -1, True, frame_speed)

        self.anim_action_up = SpriteStripAnim(self.image_path, (0, self.width*12, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_left = SpriteStripAnim(self.image_path, (0, self.width*13, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_down = SpriteStripAnim(self.image_path, (0, self.width*14, self.width, self.height), 6, -1, False, frame_speed)
        self.anim_action_right = SpriteStripAnim(self.image_path, (0, self.width*15, self.width, self.height), 6, -1, False, frame_speed)

        #self.anim_dead = SpriteStripAnim(self.image_path, (0, self.height*21, self.width, self.height), 6, -1, False, frame_speed)

        self.anim_effect = OrderedDict()
        self.anim_attack = OrderedDict()
        self.anim_walk = OrderedDict()
        self.anim_action = OrderedDict()

        self.anim_effect["UP"] = self.anim_effect_up
        self.anim_effect["LEFT"] = self.anim_effect_left
        self.anim_effect["DOWN"] = self.anim_effect_down
        self.anim_effect["RIGHT"] = self.anim_effect_right

        self.anim_attack["UP"] = self.anim_attack_up
        self.anim_attack["LEFT"] = self.anim_attack_left
        self.anim_attack["DOWN"] = self.anim_attack_down
        self.anim_attack["RIGHT"] = self.anim_attack_right

        self.anim_action["UP"] = self.anim_action_up
        self.anim_action["LEFT"] = self.anim_action_left
        self.anim_action["DOWN"] = self.anim_action_down
        self.anim_action["RIGHT"] = self.anim_action_right

        self.anim_walk["UP"] = self.anim_walk_up
        self.anim_walk["LEFT"] = self.anim_walk_left
        self.anim_walk["DOWN"] = self.anim_walk_down
        self.anim_walk["RIGHT"] = self.anim_walk_right

        self.image = self.anim_walk["DOWN"].images[0]

        self.direction = "DOWN"
        self.facing = 0
        self.mirror = False

        self.speed = 12

        self.velocity = [0, 0]
        self._position = [self.x, self.y]
        self._old_position = self.position

        self.rect = self.image.get_rect()
        self.feet = pygame.Rect(0, 0, self.rect.width/2 * 0.5, 8)

        p = 3.0
        i = 2.0
        d = 1.0

        derivator = 0
        integrator = 0

        integrator_max = 3
        integrator_min = -3

        if self.follower:
            self.x_pid = Pid(p=p, i=i, d=d,
                             derivator=derivator,
                             integrator=integrator,
                             integrator_max=integrator_max,
                             integrator_min=integrator_min)

            self.y_pid = Pid(p=p, i=i, d=d,
                             derivator=derivator,
                             integrator=integrator,
                             integrator_max=integrator_max,
                             integrator_min=integrator_min)

    @property
    def position(self) -> List[int]:
        return list(self._position)

    @position.setter
    def position(self, value: List[int]) -> None:
        self._position = list(value)

    def update(self, dt: float) -> None:

        if self.follower:
            self.follow()
        elif self.wanderer:
            self.wander(dt)

        self._old_position = self._position[:]

        self._position[0] += self.velocity[0] * dt
        self._position[1] += self.velocity[1] * dt

        self.rect.topleft = self.position
        self.feet.midbottom = self.rect.midbottom

        if self.velocity[0] > 0 and self.velocity[1] > 0:
            # print("DIAGONAL DOWN RIGHT")
            self.direction = "RIGHT"
            self.facing = 7
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[0] < 0 and self.velocity[1] < 0:
            # print("DIAGONAL UP LEFT")
            self.direction = "LEFT"
            self.facing = 3
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] > 0 and self.velocity[1] < 0:
            # print("DIAGONAL UP RIGHT")
            self.direction = "RIGHT"
            self.facing = 5
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[0] < 0 and self.velocity[1] > 0:
            # print("DIAGONAL DOWN LEFT")
            self.direction = "LEFT"
            self.facing = 1
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] < 0:
            # print("LEFT")
            self.direction = "LEFT"
            self.facing = 2
            self.mirror = False
            self.image = self.anim_walk["LEFT"].next()

        elif self.velocity[0] > 0:
            # print("RIGHT")
            self.direction = "RIGHT"
            self.facing = 6
            self.mirror = True
            self.image = self.anim_walk["RIGHT"].next()

        elif self.velocity[1] < 0:
            # print("UP")
            self.direction = "UP"
            self.facing = 4
            self.mirror = False
            self.image = self.anim_walk["UP"].next()

        elif self.velocity[1] > 0:
            # print("DOWN")
            self.direction = "DOWN"
            self.facing = 0
            self.mirror = False
            self.image = self.anim_walk["DOWN"].next()

        elif self.velocity[0] == 0 and self.velocity[1] == 0:
            # FIXME enemy attack
            if self.level <= 2:
                self.anim_attack
                pass
            if self.level == 2:
                self.run_attack_action = False
                self.attack()

        else:
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
                    # print(f"Play frame {self.animation_action_frame} in direction = {self.direction} facing {self.facing}")
                else:
                    self.animation_action_frame = 0
                    self.run_attack_action = True
                    # print("animation end")

                self.prev_ticks = self.current_ticks

    def follow(self):
        self.pid_plus()

    def pid_plus(self):

        radius = 700

        # Check if position in X is greater than player position
        if self.position[0] > self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error > radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0
                self.wanderer = False
                self.follower = True

        elif self.position[0] < self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error < -radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0
                self.wanderer = True
                self.follower = False

        # Check if position in Y is greater than player position
        if self.position[1] > self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error > radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0
                self.wanderer = True
                self.follower = False

        elif self.position[1] < self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error < -radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0
                self.wanderer = True
                self.follower = False

    def pid_minus(self):

        radius = 200

        # Check if position in X is greater than player position
        if self.position[0] < self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error < radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0

        elif self.position[0] > self.player.position[0]:
            self.x_pid.set_setpoint(self.player.position[0])
            self.x_pid.update(self.position[0])
            error = self.x_pid.get_error()
            if error > -radius:
                self.velocity[0] = error
            else:
                self.velocity[0] = 0

        # Check if position in Y is greater than player position
        if self.position[1] < self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error < -radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0

        elif self.position[1] > self.player.position[1]:
            self.y_pid.set_setpoint(self.player.position[1])
            self.y_pid.update(self.position[1])
            error = self.y_pid.get_error()
            if error > radius:
                self.velocity[1] = error
            else:
                self.velocity[1] = 0

    def move_back(self, dt: float) -> None:
        """If called after an update, the sprite can move back"""
        self._position = self._old_position
        self.rect.topleft = self._position
        self.feet.midbottom = self.rect.midbottom

    def shoot(self):
        # get the player vector
        distance = [self.player.position[0] - self.position[0], self.player.position[1] - self.position[1]]
        norm = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
        direction = [distance[0] / norm, distance[1] / norm]
        bullet_vector = [direction[0] * math.sqrt(20), direction[1] * math.sqrt(10)]
        projectile = Projectile(self, self.game, "Enemy",  bullet_vector)

        self.game.add_bullet(projectile)

    def attack(self):
        self.pid_minus()
        self.shooting = True
        self.run_attack_action = True

        self.attacking = True
        print("el enemigo esta atacando")

    def wander(self, dt):

        self.pid_minus()

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

    def get_rect(self):
        return self.rect

    def get_feet(self):
        return self.feet

    def get_id(self):
        return self.enemy_id