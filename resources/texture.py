# Copyright (C) 2023 zyxkad@gmail.com

from .vec import Vec2
from .surface import Surface, Anchor

import pygame

__all__ = [
	'Texture',
]

class Texture:
	def __init__(self, path: str):
		self.__img_obj = pygame.image.load(path)

	@property
	def native(self) -> pygame.Surface:
		return self.__img_obj

	def draw_at(self, surface: Surface, size: Vec2 | None = None):
		s = self.__img_obj
		if size is not None:
			s = pygame.transform.scale(s, size.xy)
		surface.blit(s, (0, 0), anchor=Anchor.TOP_LEFT)
