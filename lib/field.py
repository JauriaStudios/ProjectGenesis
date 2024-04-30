import os
from pprint import pprint

import oyaml as yaml
import pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

from pygame import Rect, JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, KEYUP, KEYDOWN
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_MINUS, K_PLUS, K_ESCAPE, K_BACKSPACE, K_SPACE

from pytmx import load_pygame

from lib.constants import ROOT_PATH, RESOURCE_PATH, RED
from lib.enemy import Enemy
from lib.menu import Menu
from lib.pet import Pet
from lib.warp_point import WarpPoint
from lib.player import Player
from lib.npc import Npc


class Field(object):
    def __init__(self, name, screen_size, music):

        print("INIT FIELD")

        self.player = None
        self.pet = None
        self.hero_move_speed = None
        self.group = None
        self.map_layer = None
        self.map_data = None
        self.tmx_data = None
        self.file_path = None
        self.menu = None

        self.spawns = dict()
        self.warps = dict()
        self.walls = list()
        self.npcs = list()
        self.enemies = list()

        # self.npcs = None
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


        # self.music.change_music(2)
        # self.music.play_music()

        self.file_path = str(os.path.join(ROOT_PATH, RESOURCE_PATH, "maps", self.map_name))

        # load data from pytmx
        self.tmx_data = load_pygame(self.file_path)

        # create new data source for pyscroll
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data,
                                                   self.screen_size,
                                                   clamp_camera=True,
                                                   tall_sprites=0
                                                   )
        self.map_layer.zoom = 2.5

        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=8)

        self.hero_move_speed = 200  # pixels per second

        self.npcs = []
        self.enemies = []
        self.walls = []
        self.warps = {}
        self.spawns = {}

        self.player = Player(self, name="Izzy", x=0, y=0)

        self.pet = Pet(self, self.player, name="gengar", x=0, y=0, width=48, height=48, follower=True, wanderer=False)

        self.group.add(self.player)
        self.group.add(self.pet)



        for obj in self.tmx_data.objects:

            pprint(obj.properties)

            if obj.type == "player_spawn":
                # print("PLAYER SPAWN FOUND")

                self.player._position[0] = int(obj.x) + self.player.width
                self.player._position[1] = int(obj.y) - self.player.height

                self.pet._position[0] = int(obj.x) + self.player.width
                self.pet._position[1] = int(obj.y) - self.player.height

            if obj.type == "enemy_spawn":
                # print("SPAWN FOUND")

                enemy_name = obj.properties.get("Name")
                enemy_level = obj.properties.get("Level")

                print(F"Spawn {enemy_name} level {enemy_level}")

                enemy = Enemy(self, self.player, name=enemy_name, x=int(obj.x), y=int(obj.y), width=64, height=64, follower=False, wanderer=True, level=enemy_level)

                self.group.add(enemy)

                self.spawns[obj.name] = (int(obj.x), int(obj.y))
                self.enemies.append(enemy)


            elif obj.type == "collision":
                collision = Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height))

                self.walls.append(collision)
                # self.group.add(collision)


            elif obj.type == "map_warp":
                warp = WarpPoint(obj, name="warp", frame_speed=10)

                self.warps[obj.name] = warp
                self.group.add(warp)

            else:
                pprint(obj)



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
                if event.key == K_LEFT:
                    self.player.velocity[0] = -self.hero_move_speed

                elif event.key == K_RIGHT:
                    self.player.velocity[0] = self.hero_move_speed

                elif event.key == K_UP:
                    self.player.velocity[1] = -self.hero_move_speed

                elif event.key == K_DOWN:
                    self.player.velocity[1] = self.hero_move_speed

                elif event.key == K_SPACE:
                    for enemy in self.enemies:
                        enemy.attack()



            elif event.type == KEYUP:
                if event.key == K_LEFT or event.key == K_RIGHT:
                    self.player.velocity[0] = 0
                elif event.key == K_UP or event.key == K_DOWN:
                    self.player.velocity[1] = 0
        elif self.field_mode == "MENU":
            self.menu.handle_input(event)

    def update(self, dt):

        if self.field_mode == "FIELD":

            self.group.update(dt)

            # check if the sprite's feet are colliding with wall
            # sprite must have a rect called feet, and move_back method,
            # otherwise this will fail
            for sprite in self.group.sprites():
                if isinstance(sprite, Player):

                    if sprite.feet.collidelist(self.walls) > -1:
                        sprite.move_back(dt)
                    # elif sprite.rect.collidelist(self.npcs) > -1:
                    #     sprite.move_back(dt)

                    for name, warp in self.warps.items():
                        if sprite.feet.colliderect(warp.get_rect()):
                            self.warps[name].go_inside(self.player)
                        else:
                            self.warps[name].go_outisde()

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

            if self.fading == "IN":
                fade_speed = 1
                self.alpha += fade_speed
                if self.alpha >= 255:
                    self.fading = None
                    self.fade_end = True

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
        self.group.add(bullet)

    def change_field(self, name):
        self.fading = "IN"
        self.map_name = name
