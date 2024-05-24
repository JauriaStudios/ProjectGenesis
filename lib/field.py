import os
import random
from pprint import pprint

import oyaml as yaml
import pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

from pygame import Rect, JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, KEYUP, KEYDOWN
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_MINUS, K_PLUS, K_ESCAPE, K_BACKSPACE, K_SPACE, K_c, K_x

from pytmx import load_pygame

from .const import ROOT_PATH, RESOURCE_PATH
from .enemy import Enemy
from .hud import Hud
from .item import Item
from .menu import Menu
from .pet import Pet
from .projectile import Projectile
from .text import TextBox
from .warp_point import WarpPoint
from .player import Player
from .npc import Npc
from .effects import PurpleImpact


class Field(object):
    def __init__(self, game, name, screen_size, music):

        print("INIT FIELD")
        self.impact = None
        self.dialog_purple = None
        self.dialog_red = None
        self.dialog = None
        self.dialog_on = None
        self.hud = None
        self.game = game
        self.hero_move_speed = None
        self.group = None
        self.map_layer = None
        self.map_data = None
        self.tmx_data = None
        self.file_path = None
        self.menu = None
        self.player_collides = None
        self.map_objects = None
        self.spawns = None
        self.items = None
        self.warps = None
        self.walls = None
        self.player = None
        self.pet = None
        self.enemies = None
        self.npcs = None

        self.hide_purple = False
        self.hide_red = False

        # self.max_counter = 2

        self.player_bullets = None
        self.map_name = name
        self.screen_size = screen_size
        self.music = music

        self.field_mode = "FIELD"
        self.fading = "OUT"
        self.fade_end = False

        self.alpha = 255

        screen_rect = Rect(0, 0, screen_size[0], screen_size[1])

        self.fade_rect = pygame.Surface(screen_rect.size)
        self.fade_rect.fill((0, 0, 0))
        self.initialize()
        self.init_menu()

    def initialize(self):

        print("INITIALIZE FIELD")


        self.impact = []
        self.player_bullets = []
        self.dialog_purple = False
        self.dialog_red = False
        self.dialog_on = False
        self.hud = Hud(self, self.game)
        # self.music.change_music(2)
        # self.music.play_music()

        self.file_path = str(os.path.join(ROOT_PATH, RESOURCE_PATH, "maps", self.map_name))

        # load data from pytmx
        self.tmx_data = load_pygame(f"{self.file_path}.tmx")

        # create new data source for pyscroll
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data,
                                                   self.screen_size,
                                                   clamp_camera=True,
                                                   tall_sprites=0
                                                   )
        self.map_layer.zoom = 2.5

        # pyscroll supports layered rendering. our map has 3 'under' layers,
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2

        self.items_group = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=8)

        self.hero_move_speed = 150  # pixels per second

        self.items = []
        self.npcs = []
        self.enemies = {}
        self.enemies_killed = []
        self.walls = []
        self.warps = {}
        self.spawns = {}
        self.map_objects = []
        self.player = Player(self, name="Izzy", x=0, y=0)
        self.impact = []
        self.player.increase_life(2)
        self.player.set_power(5)

        self.pet = Pet(self, self.player, name="gengar", x=0, y=0, width=48, height=48, follower=True, wanderer=False)

        self.group.add(self.player)
        self.group.add(self.pet)
        self.group.add(self.pet)

        enemy_count = 0

        for obj in self.tmx_data.objects:

            # pprint(obj.properties)

            if obj.type == "player_spawn":
                # print("PLAYER SPAWN FOUND")

                self.player._position[0] = int(obj.x) + self.player.width/2
                self.player._position[1] = int(obj.y) - self.player.height/2

                self.pet._position[0] = int(obj.x) + self.player.width
                self.pet._position[1] = int(obj.y) - self.player.height

            if obj.type == "enemy_spawn":
                # print("SPAWN FOUND")

                enemy_name = obj.properties.get("Name")
                enemy_level = obj.properties.get("Level")

                # print(F"Spawn {enemy_name} level {enemy_level}")

                enemy = Enemy(self, self.player, name=enemy_name, enemy_id=enemy_count, x=int(obj.x), y=int(obj.y), width=64, height=64, follower=True, wanderer=False, level=enemy_level)

                self.enemy_group.add(enemy)
                self.group.add(enemy)

                self.spawns[obj.name] = (int(obj.x), int(obj.y))
                self.enemies[enemy_count] = enemy

                enemy_count += 1

            elif obj.type == "collision":
                collision = Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))

                self.walls.append(collision)
                # self.group.add(collision)

            elif obj.type == "map_warp":
                warp = WarpPoint(obj, name="warp", frame_speed=10)

                self.warps[obj.name] = warp
                self.group.add(warp)

            elif obj.type == "item":
                item_name = obj.properties.get("Name")
                item = Item(item_name, (int(obj.x), int(obj.y)), 10)
                self.items_group.add(item)
                self.group.add(item)
            else:
                pprint(obj)

        self.fading = "OUT"
        # for name, spawn in self.spawns.items():
        #     self.npc_1.position = self.spawns[name]

        image_path = os.path.join(RESOURCE_PATH, "dialog", "purplegem.png")
        purple_html = "<body>"\
                      f"<img src='{image_path}' "\
                      "padding='40px 10px 0px 100px'>"\
                      "<br>"\
                      "<p font_color=#ffffff>"\
                      "Has recibido <font color=#6c17d3><b>1 Cristal morado.</b></font>" \
                      "<br>" \
                      "Restablece 1 punto de <font color=#6c17d3><b>poder.</b></font>" \
                      "<br>" \
                      "<p>Pulsa 'SPACE' para disparar" \
                      "</font>""</p>"
        image_path = os.path.join(RESOURCE_PATH, "dialog", "redgem.png")
        red_html = "<body>"\
                          f"<img src='{image_path}' "\
                          "padding='40px 10px 0px 100px'>"\
                          "<br>"\
                          "<p><font color=#ffffff text_vert_alignment='center'>"\
                          "Has recibido <font color=#e20909><b>1 Cristal rojo.</b></font>"\
                          "<br>"\
                          "Restablece 1 corazón de <font color=#e20909><b>vida.</b></font>" \
                          "<br>" \
                          "<p>Pulsa la tecla X" \
                          "</font>""</p>"
        self.dialog_win_purple = TextBox(self.game, purple_html)
        self.dialog_win_red = TextBox(self.game, red_html)


    def init_menu(self):

        print("INIT MENU")

        file_path = os.path.join(ROOT_PATH, RESOURCE_PATH, "menu", "field.yml")
        with open(file_path) as fh:
            options = yaml.load(fh, Loader=yaml.FullLoader)

        self.menu = Menu(options, self.music)
        # print(options)


    def handle_input(self, event):
        dead_zone = 0.25
        if self.field_mode == "FIELD":

            if event.type == JOYAXISMOTION:
                if event.axis == 0 or event.axis == 1:
                    if abs(event.value) > dead_zone:

                        self.player.velocity[event.axis] = event.value * self.hero_move_speed
                    else:
                        self.player.velocity[event.axis] = 0

                # elif event.axis == 3:
                #     if event.value > dead_zone or event.value < dead_zone:
                #         self.map_layer.zoom += event.value / 10

            elif event.type == JOYBUTTONDOWN:
                if event.button == 0:
                    for name, warp in self.warps.items():
                        if warp.get_player():
                            map_name = warp.get_warp_map()
                            # print(f"Change Field {map_name} from warp name {name}")
                            self.change_field(map_name)

                elif event.button == 1:
                    # self.npc_1.shoot()
                    self.player.action()
                elif event.button == 2:
                    self.player.attack()
                elif event.button == 8:
                    self.field_mode = "MENU"

            elif event.type == JOYBUTTONUP:
                if event.button == 2:
                    pass

            elif event.type == KEYDOWN:
                if not self.player.run_attack_action:
                    if event.key == K_LEFT:
                        self.player.velocity[0] = -self.hero_move_speed

                    elif event.key == K_RIGHT:
                        self.player.velocity[0] = self.hero_move_speed

                    elif event.key == K_UP:
                        self.player.velocity[1] = -self.hero_move_speed

                    elif event.key == K_DOWN:
                        self.player.velocity[1] = self.hero_move_speed

                    elif event.key == K_SPACE:
                        self.player.attack()

                    elif event.key == K_c:
                        for name, warp in self.warps.items():
                            if warp.get_player():
                                map_name = warp.get_warp_map()
                                # print(f"Change Field {map_name} from warp name {name}")
                                self.change_field(map_name)

                    elif event.key == K_x:
                        if self.dialog_purple:
                            self.dialog_win_purple.show_dialog(False)
                            self.dialog_purple = True
                        if self.dialog_red:
                            self.dialog_win_red.show_dialog(False)
                            self.dialog_red = True

                else:
                    self.player.velocity[0] = 0
                    self.player.velocity[1] = 0

            elif event.type == KEYUP:
                if self.player.run_attack_action == False:
                    if event.key == K_LEFT or event.key == K_RIGHT:
                        self.player.velocity[0] = 0
                    elif event.key == K_UP or event.key == K_DOWN:
                        self.player.velocity[1] = 0
                else:
                    self.player.velocity[0] = 0
                    self.player.velocity[1] = 0
        elif self.field_mode == "MENU":
            self.menu.handle_input(event)

    def update(self, dt):

        if self.field_mode == "FIELD":
            if self.player.life_bar > 0:
                self.group.update(dt)

            # check if the sprite's feet are colliding with wall
            # sprite must have a rect called feet, and move_back method,
            # otherwise this will fail

            for sprite in self.group.sprites():
                if isinstance(sprite, Player):
                    if sprite.feet.collidelist(self.walls) > -1:
                        sprite.move_back(dt)

                    for name, warp in self.warps.items():
                        if sprite.feet.colliderect(warp.get_rect()):
                            self.warps[name].go_inside()
                        else:
                            self.warps[name].go_outisde()

                if isinstance(sprite, Item):
                    if self.player.rect.colliderect(sprite.rect):
                        if sprite.name == "purplegem":
                            self.player.set_power(1)
                            if self.hide_purple is False:
                                self.dialog_win_purple.show_dialog(True)
                                self.dialog_purple = True
                                self.hide_purple = True
                        if sprite.name == "redgem":
                            self.player.increase_life(1)
                            if self.hide_red is False:
                                self.dialog_win_red.show_dialog(True)
                                self.dialog_red = True
                                self.hide_red = True

                        self.items_group.remove(sprite)
                        self.group.remove(sprite)

                elif isinstance(sprite, Npc):
                    if sprite.feet.collidelist(self.walls) > -1:
                        sprite.move_back(dt)

                    elif sprite.feet.colliderect(self.player.get_rect()):
                        sprite.velocity[0] = 0
                        sprite.velocity[1] = 0

                elif isinstance(sprite, Enemy):
                    if sprite.feet.collidelist(self.walls) > -1:
                        sprite.move_back(dt)

                    elif sprite.feet.colliderect(self.player.get_rect()):
                        sprite.velocity[0] = 0
                        sprite.velocity[1] = 0
                elif isinstance(sprite, Projectile):
                    if sprite.feet.colliderect(self.player.get_rect()):
                        if sprite.owner == "Enemy":
                            self.player.decrease_life(1)
                            self.group.remove(sprite)

                    for enemy_id, enemy in self.enemies.items():
                        if enemy.alive():
                            if sprite.feet.colliderect(enemy.get_feet()):
                                if sprite.owner == "Player":

                                    i = random.randint(0, 1)
                                    if i == 1:
                                        item = Item("purplegem", (int(enemy.position[0]), int(enemy.position[1])), 10)
                                    else:
                                        item = Item("redgem", (int(enemy.position[0]), int(enemy.position[1])), 10)

                                    self.items_group.add(item)
                                    self.group.add(item)

                                    self.group.remove(sprite)
                                    self.enemies_killed.append(enemy_id)

                if len(self.enemies_killed) > 0:
                    for enemy_id in self.enemies_killed:
                        enemy = self.enemies[enemy_id]
                        self.kill_enemy(enemy)

            if self.fading == "IN":
                fade_speed = 1
                self.alpha += fade_speed
                if self.alpha >= 255:
                    self.fading = None
                    self.fade_end = True
                    if self.map_name != self.previous_map_name:
                        self.initialize()

            elif self.fading == "OUT":
                fade_speed = 1
                self.alpha -= fade_speed
                if self.alpha <= 0:
                    self.fading = None
                    self.fade_end = True

            # if self.fade_end is True:
            #     self.initialize()
            #     self.fade_end = False
            #     self.fading = "OUT"

            self.hud.update(dt)
            self.dialog_win_red.update(dt)
            self.dialog_win_purple.update(dt)

        elif self.field_mode == "MENU":
            self.menu.update(dt)

    def draw(self, screen, dt):

        if self.field_mode == "MENU":
            self.menu.draw(screen)
        elif self.field_mode == "FIELD":
            # center the map/screen on our Hero
            self.group.center(self.player.rect.center)

            # draw the map and all sprites

            self.group.draw(screen)

            if self.fading is not None:
                self.fade_rect.set_alpha(self.alpha)
                screen.blit(self.fade_rect, (0, 0))

    def add_bullet(self, bullet):
        # self.player_bullets.append(bullet)
        self.group.add(bullet)

    def remove_bullet(self, bullet):
        # self.player_bullets.append(bullet)
        self.group.remove(bullet)

    def change_field(self, name):
        self.fading = "IN"
        self.previous_map_name = self.map_name
        self.map_name = name

    def kill_enemy(self, enemy):
        # self.player_bullets.append(bullet)

        enemy.kill()
        enemy.remove((self.enemy_group, self.group))
