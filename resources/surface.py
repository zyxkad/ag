# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

import enum
from typing import TypeVar, Iterable

from .color import *
from .vec import *

import pygame

__all__ = [
	'Anchor',
	'Surface',
]

class Anchor(enum.Enum):
	TOP_LEFT = enum.auto()
	TOP_CENTER = enum.auto()
	TOP_RIGHT = enum.auto()
	LEFT_CENTER = enum.auto()
	CENTER = enum.auto()
	RIGHT_CENTER = enum.auto()
	BOTTOM_LEFT = enum.auto()
	BOTTOM_CENTER = enum.auto()
	BOTTOM_RIGHT = enum.auto()

	def convert_pos(self, pos: Vec2 | tuple[float, float], size: Vec2) -> Vec2:
		if isinstance(pos, tuple):
			pos = Vec2(pos)
		if self is Anchor.TOP_LEFT:
			return pos
		if self is Anchor.TOP_CENTER:
			return Vec2(pos.x - size.x / 2, pos.y)
		if self is Anchor.TOP_RIGHT:
			return Vec2(pos.x - size.x, pos.y)
		if self is Anchor.BOTTOM_LEFT:
			return Vec2(pos.x, pos.y - size.y)
		if self is Anchor.BOTTOM_CENTER:
			return Vec2(pos.x - size.x / 2, pos.y - size.y)
		if self is Anchor.BOTTOM_RIGHT:
			return pos - size
		if self is Anchor.LEFT_CENTER:
			return Vec2(pos.x, pos.y - size.y / 2)
		if self is Anchor.CENTER:
			return pos - size / 2
		if self is Anchor.RIGHT_CENTER:
			return Vec2(pos.x - size.x, pos.y - size.y / 2)
		raise RuntimeError('Unexpect status')

Self = TypeVar('Self', bound='Surface')

class Surface:
	def __init__(self, size: Vec2 | tuple[float, float] | pygame.Surface):
		if isinstance(size, pygame.Surface):
			self._size = Vec2(size.get_size())
			self._obj = size
		else:
			if isinstance(size, tuple):
				size = Vec2(size)
			self._size = size.copy()
			self._obj = pygame.Surface(size.xy, flags=pygame.constants.SRCALPHA)

	@property
	def size(self) -> Vec2:
		return self._size

	@size.setter
	def size(self, size: Vec2):
		self._size = size

	@property
	def alpha(self) -> int:
		alpha = self._obj.get_alpha()
		return 0xff if alpha is None else alpha

	@alpha.setter
	def alpha(self, alpha: int):
		self._obj.set_alpha(alpha)

	def copy(self) -> Surface:
		return Surface(self._obj.copy())

	def clone_from(self, other: Self):
		assert self.size == other.size, f'Surface size {self.size} is not equals {other.size}'
		self._obj.get_buffer().write(other._obj.get_buffer().raw)

	def fill(self, color: Color, dest: Rect | None = None):
		if dest is None:
			dest = Rect(0, 0, self.size)
		self._obj.fill(color.rgba, tuple(dest))

	def circle(self, color: Color, center: tuple[float, float], radius: float,
		width: int = 0,
		draw_top_right: bool = True, draw_top_left: bool = True,
		draw_bottom_left: bool = True, draw_bottom_right: bool = True):
		pygame.draw.circle(self._obj, color.rgba, center, radius,
			width=width,
			draw_top_right=draw_top_right, draw_top_left=draw_top_left,
			draw_bottom_left=draw_bottom_left, draw_bottom_right=draw_bottom_right)

	def polygon(self, color: Color, points: Iterable[Vec2], width: int = 0):
		pygame.draw.polygon(self._obj, color.rgba, [p.xy for p in points], width=width)

	def blit(self, src: Surface | pygame.Surface, dest: Vec2 | tuple[float, float], anchor: Anchor = Anchor.CENTER):
		if not isinstance(src, Surface):
			src = Surface(src)
		self._obj.blit(src._obj, anchor.convert_pos(dest, src.size).xy)

	def get_at(self, pos: tuple[int, int]) -> Color:
		c = self._obj.get_at(pos)
		return Color(c.r, c.g, c.b, c.a)

	def set_at(self, pos: tuple[int, int], color: Color):
		self._obj.set_at(pos, color.rgba)
