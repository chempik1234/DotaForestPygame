import pygame.sprite

from sprite import CustomSprite


class Hero:
    def __init__(self, sprite: CustomSprite, background_group,
                 pickups_group=None, heroes_group=None, speed=10, is_player=False, bounds=()):
        self.sprite = sprite
        self.sprite.parent = self
        self.x_acceleration = self.y_acceleration = 0
        self.speed = speed
        self.score = 0
        self.alive = True
        self.bounds = bounds
        self.background_group = background_group
        self.pickups_group = pickups_group
        self.heroes_group = heroes_group

        self.mixer = pygame.mixer
        self.mixer.init()
        self.attack_sound = self.mixer.Sound("sounds/attack.mp3")
        self.is_player = is_player

    def update(self):
        x_bounce, y_bounce = self.get_bounce()
        if x_bounce != 0:
            x_offset = x_bounce
        else:
            x_offset = self.speed * self.x_acceleration
        if y_bounce != 0:
            y_offset = y_bounce
        else:
            y_offset = self.speed * self.y_acceleration
        self.sprite.rect.move_ip(x_offset, y_offset)
        x_bounce, y_bounce = self.get_bounce()
        self.sprite.rect.move_ip(x_bounce, y_bounce)
        if self.sprite.rect.left < 0:
            self.sprite.rect.left = 0
        if self.sprite.rect.right > self.bounds[0]:
            self.sprite.rect.right = self.bounds[0]
        if self.sprite.rect.top < 0:
            self.sprite.rect.top = 0
        if self.sprite.rect.bottom > self.bounds[1]:
            self.sprite.rect.bottom = self.bounds[1]
        if self.pickups_group:
            for pickup in self.pickups_group:
                if pygame.sprite.collide_rect(self.sprite, pickup):
                    pickup.kill()
                    self.score_up()
        if self.heroes_group:
            for hero_sprite in self.heroes_group:
                if hero_sprite == self.sprite:
                    continue
                if pygame.sprite.collide_rect(self.sprite, hero_sprite) and isinstance(hero_sprite.parent,
                                                                                       Hero):
                    self.attack(hero_sprite.parent)
                    self.score_up()

    def score_up(self):
        self.score += 1

    def set_x_acceleration(self, multiplier):
        self.x_acceleration = multiplier

    def set_y_acceleration(self, multiplier):
        self.y_acceleration = multiplier

    def attack(self, other_hero):
        self.attack_sound.play()
        if self.is_player:
            self.die()
        else:
            other_hero.die()

    def die(self):
        self.alive = False
        self.sprite.kill()

    def get_bounce(self):
        x = y = 0
        for wall in self.background_group:
            if pygame.sprite.collide_rect(self.sprite, wall):
                x = y = 0
                if self.sprite.rect.left < wall.rect.left < self.sprite.rect.right:
                    x = wall.rect.left - self.sprite.rect.right
                if self.sprite.rect.left < wall.rect.right < self.sprite.rect.right:
                    x = wall.rect.right - self.sprite.rect.left
                if wall.rect.top < self.sprite.rect.top:
                    y = wall.rect.bottom - self.sprite.rect.top
                if self.sprite.rect.top < wall.rect.top < self.sprite.rect.bottom:
                    y = wall.rect.top - self.sprite.rect.bottom
                if wall.rect.top < self.sprite.rect.top < self.sprite.rect.bottom < wall.rect.bottom:
                    y = 0
                if wall.rect.left < self.sprite.rect.left < self.sprite.rect.right < wall.rect.right:
                    x = 0
                if abs(x) < abs(y) and x != 0:
                    y = 0
                elif abs(x) > abs(y) and y != 0:
                    x = 0
                # return x, y
        return x, y
