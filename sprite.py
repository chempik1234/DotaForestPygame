import math
import os
import pygame


def load_image(name, color_key=None):
    fullname = os.path.join('sprites', name)
    try:
        image = pygame.image.load(fullname)
    except pygame.error as message:
        raise SystemExit(message)
    if color_key is not None:
        if color_key == -1:
            color_key = image.get_at((0, 0))
            image.set_colorkey(color_key)
        else:
            image.set_colorkey(image.get_at((49, 0)))
    else:
        image = image.convert_alpha()
    return image


class CustomSprite(pygame.sprite.Sprite):
    def __init__(self, image, groups, x, y, parent=None):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect().move(x, y)
        self.parent = parent

    def get_event(self, event):
        pass


# class RotatingSprite(CustomSprite):
#     def __init__(self, image, groups, x, y, parent=None):
#         super().__init__(image, groups, x, y, parent)
#         self.original_image = image
#         self.angle = 0
#
#     def rotate(self, angle):
#         self.angle = (self.angle + angle) % 360
#         print(math.radians(self.angle))
#         self.image = pygame.transform.rotate(self.original_image, math.radians(self.angle))
