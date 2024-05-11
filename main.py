import math
import random
from random import randint

import pygame

from functions import quick_text, image_max_size, image_min_size
from hero import Hero
from sprite import load_image, CustomSprite

SCREEN_SIZE = (1000, 1000)
FPS = 60


class Game:
    def __init__(self, screen_size=SCREEN_SIZE, fps=FPS, hero_max_size=70):
        self.screen_size = screen_size
        pygame.init()
        pygame.display.set_caption('Dota Runes')
        self.screen = pygame.display.set_mode(self.screen_size)
        self.display = pygame.display

        self.fps = fps
        self.clock = pygame.time.Clock()

        self.background_group = pygame.sprite.Group()
        self.heroes_group = pygame.sprite.Group()
        self.pickups_group = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()

        self.game_mode = None
        self.character_id = None

        self.loading_image = image_min_size(load_image("screen.png"), self.screen_size[1])
        self.forest_background_image = pygame.transform.scale(load_image("background.png"), self.screen_size)
        self.accept_image = load_image("accept.png")

        self.hero_max_size = hero_max_size

        self.hero_image = image_max_size(load_image("hero.png"), self.hero_max_size)
        self.enemy_images = [image_max_size(load_image(f"enemy{i}.png"), self.hero_max_size) for i in range(4)]
        self.tree_images = [image_max_size(load_image(f"tree{i}.png"), self.hero_max_size * 2) for i in range(3)]
        self.pickup_image = image_max_size(load_image("pickup.png"), self.hero_max_size * 0.8)

        self.score = None

        self.run_loading_screen()

        self.mixer = pygame.mixer
        self.mixer.init()
        self.loading_music = self.mixer.Sound("sounds/loading_music.mp3")
        self.gameplay_music = "sounds/gameplay_music.mp3"

        self.track_end = pygame.USEREVENT+1
        pygame.mixer.music.set_endevent(self.track_end)
        pygame.mixer.music.load(self.gameplay_music)

    def run(self):
        self.game_mode = 1
        running = True
        while running:
            for sprite in self.all_sprites:
                sprite.kill()
            self.all_sprites.empty()
            if self.game_mode == 0:
                self.run_gameplay()
            elif self.game_mode == 1:
                self.run_menu()
            elif self.game_mode == 2:
                running = False

    def run_loading_screen(self):
        self.screen.blit(self.loading_image, (self.screen_size[0] // 2 - self.loading_image.get_width() // 2, 0))
        quick_text(["загрузка..."], self.screen_size[0] // 2 - self.screen_size[0] // 3,
                   self.screen_size[1] * 2 // 3, self.screen, font_size=48)
        quick_text(["загрузка..."], self.screen_size[0] // 2 - self.screen_size[0] // 3,
                   self.screen_size[1] * 2 // 3 + 5, self.screen, color=pygame.Color("yellow"), font_size=48)
        self.display.flip()

    def run_gameplay(self):
        self.loading_music.stop()
        pygame.mixer.music.load(self.gameplay_music)
        pygame.mixer.music.play()
        running = True
        local_hero = Hero(CustomSprite(self.hero_image, (self.all_sprites, self.heroes_group),
                                       0, self.screen_size[1] - self.hero_max_size),
                          self.background_group, bounds=self.screen_size,
                          pickups_group=self.pickups_group, heroes_group=self.heroes_group,
                          is_player=True)
        self.generate_sprites(self.tree_images, self.background_group, amount=15)
        enemies = self.generate_enemies()
        pickups = self.generate_sprites(self.pickup_image, self.pickups_group)
        seconds = 0
        ready_to_end = False
        while running:
            seconds += self.clock.tick(self.fps) / 1000
            for event in pygame.event.get():
                if event.type == self.track_end:
                    # self.background_music.track = (self.background_music.track + 1) % len(self.background_music.tracks)
                    pygame.mixer.music.load(self.gameplay_music)
                    pygame.mixer.music.play()
                if event.type == pygame.QUIT:
                    running = False
                    self.game_mode = 2
                if event.type == pygame.KEYDOWN:
                    if ready_to_end:
                        running = False
                        self.game_mode = 1
                    if event.key == pygame.K_UP:
                        local_hero.set_y_acceleration(-1)
                    if event.key == pygame.K_DOWN:
                        local_hero.set_y_acceleration(1)
                    if event.key == pygame.K_LEFT:
                        local_hero.set_x_acceleration(-1)
                    if event.key == pygame.K_RIGHT:
                        local_hero.set_x_acceleration(1)
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                        local_hero.set_y_acceleration(0)
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        local_hero.set_x_acceleration(0)
            if seconds > .5:
                seconds = 0
                for enemy in enemies:
                    enemy.set_x_acceleration(randint(-1, 1))
                    enemy.set_y_acceleration(randint(-1, 1))
            # bulat.update()
            for hero_sprite in self.heroes_group:
                if not hero_sprite.parent:
                    continue
                hero_sprite.parent.update()
            self.screen.blit(self.forest_background_image, (0, 0))
            # self.background_group.draw(self.screen)
            # self.heroes_group.draw(self.screen)
            # self.pickups_group.draw(self.screen)
            self.all_sprites.draw(self.screen)
            if not local_hero.alive:
                ready_to_end = True

                first_string = 'ПОБЕДА СИЛ ТЬМЫ!'
                second_string = 'ОЧКИ: ' + str(local_hero.score)
                second_string = ' ' * ((len(first_string) - len(second_string))) + second_string
                quick_text([first_string, second_string], self.screen_size[0] // 4,
                           self.screen_size[1] * 0.2, self.screen, color=pygame.Color("black"))
                quick_text([first_string, second_string], self.screen_size[0] // 4,
                           self.screen_size[1] * 0.2 - 2, self.screen, color=pygame.Color("red"))
                quick_text(["нажмите любую кнопку"], 0,
                           self.screen_size[1] * 0.8, self.screen, color=pygame.Color("white"),
                           font_size=36)
            if not any(i.alive() for i in pickups):
                ready_to_end = True

                first_string = 'ПОБЕДА СИЛ СВЕТА!'
                second_string = 'ОЧКИ: ' + str(local_hero.score)
                second_string = ' ' * ((len(first_string) - len(second_string))) + second_string

                quick_text([first_string, second_string], self.screen_size[0] // 4,
                           self.screen_size[1] * 0.2, self.screen, color=pygame.Color("white"))
                quick_text([first_string, second_string], self.screen_size[0] // 4,
                           self.screen_size[1] * 0.2 - 2, self.screen, color=pygame.Color("green"))
                quick_text(["нажмите любую кнопку"], 0,
                           self.screen_size[1] * 0.8, self.screen, color=pygame.Color("white"),
                           font_size=36)
            else:
                quick_text([f"осталось: {len([i for i in pickups if i.alive()])}/{len(pickups)}"], 10, 10,
                           screen=self.screen)
            self.display.flip()

    def run_menu(self):
        self.loading_music.stop()
        pygame.mixer.music.stop()
        self.loading_music.play()
        running = True
        transit_0_255 = stage = 0
        loading_image_x, loading_image_y = self.screen_size[0] // 2 - self.loading_image.get_width() // 2, 0
        while running:
            self.screen.blit(self.loading_image, (loading_image_x, loading_image_y))
            transit_0_255 = min(255, transit_0_255 + self.clock.tick(self.fps) / 50 * (30 * stage + 1))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    self.game_mode = 2
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if stage < 2:
                        stage += 1
                        transit_0_255 = 0
                    if stage == 2:
                        running = False
                        self.game_mode = 0
                # if event.type == pygame.KEYDOWN:
                #     running = False
                #     self.game_mode = 0
            if stage == 0:
                quick_text(["нажмите любую кнопку"], self.screen_size[0] // 3, self.screen_size[1] * 0.8,
                           self.screen, font_size=36, color=(int(transit_0_255),
                                                             int(transit_0_255),
                                                             int(transit_0_255)))
            else:
                accept_image = image_max_size(self.accept_image,
                                              max(self.screen_size[1] * transit_0_255 / 255 * 0.6, 1))
                self.screen.blit(accept_image,
                                 dest=(self.screen_size[0] // 2 - accept_image.get_width() // 2,
                                       self.screen_size[1] // 2))
            self.display.flip()

    def generate_enemies(self):
        res = []
        for i in range(4):
            hero = Hero(CustomSprite(random.choice(self.enemy_images), (self.heroes_group, self.all_sprites),
                                     0, 0), self.background_group, bounds=self.screen_size,
                        speed=3)
            good = False
            while not good:
                good = True
                for sprite in self.all_sprites:
                    if sprite == hero.sprite:
                        continue
                    if pygame.sprite.collide_rect(hero.sprite, sprite):
                        good = False
                        hero.sprite.rect.left = randint(0, self.screen_size[0] - hero.sprite.rect.w)
                        hero.sprite.rect.top = randint(0, self.screen_size[1] - hero.sprite.rect.h)
                        break
            res.append(hero)
        return res

    def generate_sprites(self, image, group, amount=5):
        res = []
        for i in range(amount):
            selected_image = image
            if isinstance(image, list):
                selected_image = random.choice(image)
            spawned_object = (CustomSprite(selected_image, (group, self.all_sprites), 0, 0))
            good = False
            while not good:
                good = True
                for sprite in self.all_sprites:
                    if sprite == spawned_object:
                        continue
                    if pygame.sprite.collide_rect(spawned_object, sprite):
                        good = False
                        spawned_object.rect.left = randint(0, self.screen_size[0] - spawned_object.rect.w)
                        spawned_object.rect.top = randint(0, self.screen_size[1] - spawned_object.rect.h)
                        break
            res.append(spawned_object)
        return res


if __name__ == '__main__':
    game = Game()
    game.run()
