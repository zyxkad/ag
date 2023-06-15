# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

from typing import Self, Iterable
import pygame

from .resources import Color, Rect, Vec2, Anchor, Surface

__all__ = [
	'Camera',
	'CameraSurface',
]

class Camera:
	def __init__(self, x: float, y: float):
		self._x = x
		self._y = y

	@property
	def x(self) -> float:
		return self._x

	@x.setter
	def x(self, x: float):
		self._x = x

	@property
	def y(self) -> float:
		return self._y

	@y.setter
	def y(self, y: float):
		self._y = y

	def copy(self) -> Self:
		return self.__class__(self.x, self.y)

class CameraSurface(Surface):
	def __init__(self, camera: Camera, size):
		super().__init__(size)
		self._camera = camera.copy()

	@property
	def camera(self) -> Camera:
		return self._camera

	def get_origin(self) -> Surface:
		return Surface(self._obj)

	def copy(self) -> CameraSurface:
		return CameraSurface(self.camera, self._obj.copy())

	@property
	def camera_center_pos(self) -> Vec2:
		return Vec2(self.camera.x - self.size.x // 2, self.camera.y - self.size.y // 2)

	def fill(self, color: Color, dest: Rect | None = None):
		cdx, cdy = self.camera_center_pos
		if dest is not None:
			dest = dest.sub_xy((cdx, cdy))
		super().fill(color, dest)

	def circle(self, color: Color, center: tuple[float, float], *args, **kwargs):
		cdx, cdy = self.camera_center_pos
		x, y = center
		x -= cdx
		y -= cdy
		super().circle(color, (x, y), *args, **kwargs)

	def polygon(self, color: Color, points: Iterable[Vec2], width: int = 0):
		cdx, cdy = self.camera_center_pos
		super().polygon(color,
			[Vec2(p.x - cdx, p.y - cdy) for p in points],
			width=width)

	def blit(self, src: Surface | pygame.Surface, dest: Vec2 | tuple[float, float], anchor: Anchor = Anchor.CENTER):
		cdx, cdy = self.camera_center_pos
		if isinstance(dest, tuple):
			dest = Vec2(dest)
		dest -= (cdx, cdy)
		super().blit(src, dest, anchor=anchor)

	def get_at(self, pos: tuple[int, int]) -> Color:
		cdx, cdy = self.camera_center_pos
		x, y = pos
		return super().get_at((int(x - cdx), int(y - cdy)))

	def set_at(self, pos: tuple[int, int], color: Color):
		cdx, cdy = self.camera_center_pos
		x, y = pos
		super().set_at((int(x - cdx), int(y - cdy)), color)
