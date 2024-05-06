import os

import pygame
import pygame_gui
from pygame_gui.core import ObjectID

from typing import List
from lib.const import RESOURCE_PATH, ROOT_PATH


class HUDSprite(pygame.sprite.Sprite):
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

    def __init__(self, field, game):

        self.field = field
        self.game = game

        self.power_laser_visible = False
        self.player_laser_level = 0

        self.sprite_list = pygame.sprite.Group()
        self.player_sprite = HUDSprite(self.sprite_list)

        avatar_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "player_nobg.png")
        self.avatar_image = pygame.image.load(avatar_path).convert_alpha()

        power_bar_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "power_bar.png")
        self.power_bar_image = pygame.image.load(power_bar_path).convert_alpha()

        power_laser_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "power_laser.png")
        self.power_laser_image = pygame.image.load(power_laser_path).convert_alpha()

        power_power_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "power_up.png")
        self.power_up_image = pygame.image.load(power_power_path).convert_alpha()

        life_support_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "life_support.png")
        self.life_support_image = pygame.image.load(life_support_path).convert_alpha()

        life_on_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "life_on.png")
        self.life_on_image = pygame.image.load(life_on_path).convert_alpha()

        life_off_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "hud", "life_off.png")
        self.life_off_image = pygame.image.load(life_off_path).convert_alpha()

        self.avatar = pygame_gui.elements.UIImage(pygame.Rect((30, 45), (223, 223)), self.avatar_image, self.game.manager)

        self.power_bar = pygame_gui.elements.UIImage(pygame.Rect((78, 265), (126, 381)), self.power_bar_image, self.game.manager)

        self.power_laser = pygame_gui.elements.UIImage(pygame.Rect((78, 265), (126, 381)), self.power_laser_image, self.game.manager)

        self.power_up_1 = pygame_gui.elements.UIImage(pygame.Rect((127, 535), (27, 41)), self.power_up_image, self.game.manager)
        self.power_up_2 = pygame_gui.elements.UIImage(pygame.Rect((127, 495), (27, 41)), self.power_up_image, self.game.manager)
        self.power_up_3 = pygame_gui.elements.UIImage(pygame.Rect((127, 455), (27, 41)), self.power_up_image, self.game.manager)
        self.power_up_4 = pygame_gui.elements.UIImage(pygame.Rect((127, 415), (27, 41)), self.power_up_image, self.game.manager)
        self.power_up_5 = pygame_gui.elements.UIImage(pygame.Rect((127, 375), (27, 41)), self.power_up_image, self.game.manager)
        self.power_up_6 = pygame_gui.elements.UIImage(pygame.Rect((127, 335), (27, 41)), self.power_up_image, self.game.manager)


        self.life_support = pygame_gui.elements.UIImage(pygame.Rect((250, 90), (146, 35)), self.life_support_image, self.game.manager)

        self.life_off1 = pygame_gui.elements.UIImage(pygame.Rect((266, 63), (32, 32)), self.life_off_image,
                                                     self.game.manager)
        self.life_off2 = pygame_gui.elements.UIImage(pygame.Rect((308, 63), (32, 32)), self.life_off_image,
                                                     self.game.manager)
        self.life_off3 = pygame_gui.elements.UIImage(pygame.Rect((352, 63), (32, 32)), self.life_off_image,
                                                     self.game.manager)

        self.life_on_1 = pygame_gui.elements.UIImage(pygame.Rect((266, 63), (32, 32)), self.life_on_image, self.game.manager)
        self.life_on_2 = pygame_gui.elements.UIImage(pygame.Rect((308, 63), (32, 32)), self.life_on_image, self.game.manager)
        self.life_on_3 = pygame_gui.elements.UIImage(pygame.Rect((352, 63), (32, 32)), self.life_on_image, self.game.manager)


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

        self.power_laser.hide()

        self.power_up_1.hide()
        self.power_up_2.hide()
        self.power_up_3.hide()
        self.power_up_4.hide()
        self.power_up_5.hide()
        self.power_up_6.hide()
        self.life_on_1.hide()
        self.life_on_2.hide()
        self.life_on_3.hide()

    def update(self, dt: float) -> None:

        if self.game.mode == "GAME":
            if self.field.player:
                power = self.field.player.get_power()
                life = self.field.player.get_life()
                print(f"life {life}")
                # TODO fix multiple calls to show()
                if power >= 1:
                    # if self.power_laser_visible is not True:
                    self.power_laser.show()
                    self.power_up_1.show()
                    # self.power_laser_visible = True
                    # self.player_laser_level = power
                else:
                    self.power_laser.hide()
                    self.power_up_1.hide()

                if power >= 2:
                    self.power_up_2.show()
                else:
                    self.power_up_2.hide()
                if power >= 3:
                    self.power_up_3.show()
                else:
                    self.power_up_3.hide()
                if power >= 4:
                    self.power_up_4.show()
                else:
                    self.power_up_4.hide()
                if power >= 5:
                    self.power_up_5.show()
                else:
                    self.power_up_5.hide()
                if power >= 6:
                    self.power_up_6.show()
                else:
                    self.power_up_6.hide()

                if life >= 1:
                    self.life_on_1.show()
                else:
                    self.life_on_1.hide()
                if life >= 2:
                    self.life_on_2.show()
                else:
                    self.life_on_2.hide()
                if life >= 3:
                    self.life_on_3.show()
                else:
                    self.life_on_3.hide()

            self.sprite_list.update(dt)
        elif self.game.mode == "MENU":
            pass
