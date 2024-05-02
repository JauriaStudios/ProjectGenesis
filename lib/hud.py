import os

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from typing import List
from lib.const import RESOURCE_PATH, ROOT_PATH


class PlayerSprite(pygame.sprite.Sprite):
    def __init__(self, *groups: pygame.sprite.AbstractGroup):
        super().__init__(*groups)

        path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "player.png")

        self.image = pygame.image.load(path)

        self.position = pygame.Vector2(200.0, 300.0)
        self.rect = self.image.get_rect()
        self.rect.topleft = (200, 300)

        self.max_health = 100
        self.current_health = 75

        self.max_mana = 100
        self.current_mana = 30

        self.max_stamina = 100.0
        self.current_stamina = 100.0

        self.speed = 100.0
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        self.stam_recharge_tick = 0.05
        self.stam_recharge_acc = 0.0

    def get_health_percentage(self) -> float:
        return self.current_health/self.max_health

    def get_mana_percentage(self) -> float:
        return self.current_mana/self.max_mana

    def get_stamina_percentage(self) -> float:
        return self.current_stamina/self.max_stamina

    def update(self, time_delta_secs: float) -> None:

        if self.moving_left:
            self.position.x -= self.speed * time_delta_secs
            self.current_stamina -= 0.4
        if self.moving_right:
            self.position.x += self.speed * time_delta_secs
            self.current_stamina -= 0.4
        if self.moving_up:
            self.position.y -= self.speed * time_delta_secs
            self.current_stamina -= 0.4
        if self.moving_down:
            self.position.y += self.speed * time_delta_secs
            self.current_stamina -= 0.4

        self.current_stamina = max(self.current_stamina, 0)

        if self.current_stamina < self.max_stamina:
            self.stam_recharge_acc += time_delta_secs
            if self.stam_recharge_acc >= self.stam_recharge_tick:
                self.current_stamina += 1
                self.stam_recharge_acc = 0.0

        self.current_stamina = min(self.current_stamina, self.max_stamina)

        self.rect.topleft = (int(self.position.x), int(self.position.y))


class Hud:

    def __init__(self, game):
        self.game = game

        self.sprite_list = pygame.sprite.Group()
        self.player_sprite = PlayerSprite(self.sprite_list)

        path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "player.png")
        self.image = pygame.image.load(path)

        self.avatar = pygame_gui.elements.UIImage(pygame.Rect((45, 45), (223, 223)), self.image, self.game.manager)

        # self.progress_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((100, 100), (200, 30)),
        #                                                self.game.manager,
        #                                                None,
        #                                                object_id=ObjectID('#progress_bar', '@UIStatusBar'))
        #
        # self.health_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((0, 30), (50, 6)),
        #                                              self.game.manager,
        #                                              sprite=self.player_sprite,
        #                                              percent_method=self.player_sprite.get_health_percentage,
        #                                              object_id=ObjectID(
        #                                                  '#health_bar', '@player_status_bars'))
        # self.mana_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((0, 40), (50, 6)),
        #                                            self.game.manager,
        #                                            sprite=self.player_sprite,
        #                                            percent_method=self.player_sprite.get_mana_percentage,
        #                                            object_id=ObjectID(
        #                                                '#mana_bar', '@player_status_bars'))
        # self.stamina_bar = pygame_gui.elements.UIStatusBar(pygame.Rect((0, 50), (50, 6)),
        #                                               self.game.manager,
        #                                               sprite=self.player_sprite,
        #                                               percent_method=self.player_sprite.get_stamina_percentage,
        #                                               object_id=ObjectID(
        #                                                   '#stamina_bar', '@player_status_bars'))

    def update(self, dt: float) -> None:

        if self.game.mode == "FIELD":
            self.sprite_list.update(dt)
        elif self.game.mode == "MENU":
            pass
