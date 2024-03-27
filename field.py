import os

import oyaml as yaml
import pygame

import pyscroll
import pyscroll.data
from pyscroll.group import PyscrollGroup

from pygame import Rect, JOYAXISMOTION, JOYBUTTONDOWN, JOYBUTTONUP, KEYUP, KEYDOWN
from pygame.locals import K_UP, K_DOWN, K_LEFT, K_RIGHT, K_MINUS, K_PLUS, K_ESCAPE, K_BACKSPACE

from pytmx import load_pygame

from constants import ROOT_PATH, RESOURCE_DIR, RED
from menu import Menu
from pet import Pet
from warp_point import WarpPoint
from player import Player
from npc import Npc


class Field(object):
    def __init__(self, name, screen_size, music):

        self.menu = None
        self.spawns = None
        self.warps = None
        self.walls = None
        self.npc_1 = None
        self.pet = None
        self.npcs = None
        self.map_name = name
        self.screen_size = screen_size
        self.music = music

        self.field_mode = "FIELD"
        self.fading = None
        self.fade_end = False

        self.alpha = 0
        sr = Rect(0, 0, screen_size[0], screen_size[1])

        self.fade_rect = pygame.Surface(sr.size)
        self.fade_rect.fill((0, 0, 0))
        self.initialize()
        self.init_menu()

    def initialize(self):

        # self.music.change_music(2)
        # self.music.play_music()

        self.file_path = os.path.join(ROOT_PATH, RESOURCE_DIR, "maps", self.map_name)

        # load data from pytmx
        self.tmx_data = load_pygame(self.file_path)

        # create new data source for pyscroll
        self.map_data = pyscroll.data.TiledMapData(self.tmx_data)

        # create new renderer (camera)
        self.map_layer = pyscroll.BufferedRenderer(self.map_data,
                                                   self.screen_size,
                                                   clamp_camera=False,
                                                   tall_sprites=0
                                                   )
        self.map_layer.zoom = 2

        # pyscroll supports layered rendering.  our map has 3 'under' layers
        # layers begin with 0, so the layers are 0, 1, and 2.
        # since we want the sprite to be on top of layer 1, we set the default
        # layer for sprites as 2
        self.group = PyscrollGroup(map_layer=self.map_layer, default_layer=8)

        self.hero_move_speed = 200  # pixels per second

        self.player = Player(self, image="Izzy.png")

        self.npcs = []

        self.pet = Pet(self, self.player, "gengar.png", 0, 0, 48, 48, follower=True, wanderer=False)

        self.npc_1 = Npc(self, self.player, "Furro.png", 0, 0, 64, 64, follower=False, wanderer=True)
        # self.npc_2 = Npc(self, self.player, "Furro.png", 0, 0, 64, 64, follower=False, wanderer=True)

        self.npcs.append(self.pet)
        self.npcs.append(self.npc_1)
        # self.npcs.append(self.npc_2)

        # put the hero in the center of the map
        self.npc_1.position = [300, 300]

        # add our hero to the group
        self.group.add(self.pet)
        self.group.add(self.npc_1)
        # self.group.add(self.npc_2)
        self.group.add(self.player)

        # setup level geometry with simple pygame rects, loaded from pytmx
        self.walls = []
        self.warps = dict()
        self.spawns = dict()

        for obj in self.tmx_data.objects:

            # pprint(obj)

            if obj.type == "warp":
                warp = WarpPoint(obj, "warp.png", 10)
                self.warps[obj.name] = warp
                self.group.add(warp)
            elif obj.type == "spawn":
                # print("SPAWN FOUND")
                self.spawns[obj.name] = (int(obj.x), int(obj.y))
            elif obj.type == "player":
                # print("PLAYER SPAWN FOUND")
                self.player.position = [int(obj.x), int(obj.y)]
                self.pet.position = [int(obj.x), int(obj.y)]
            else:
                self.walls.append(Rect(int(obj.x), int(obj.y), int(obj.width), int(obj.height)))

        for name, spawn in self.spawns.items():
            self.npc_1.position = self.spawns[name]

    def init_menu(self):
        file_path = os.path.join(ROOT_PATH, RESOURCE_DIR, "menu", "field.yml")
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

            if self.fading == "IN":
                fade_speed = 0.25
                self.alpha += fade_speed
                if self.alpha >= 255:
                    self.fading = None
                    self.fade_end = True

            elif self.fading == "OUT":
                fade_speed = 0.25
                self.alpha -= fade_speed
                if self.alpha <= 0:
                    self.fading = None

            if self.fade_end is True:
                self.initialize()
                self.fade_end = False
                self.fading = "OUT"

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
