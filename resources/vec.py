# Copyright (C) 2023 zyxkad@gmail.com

from typing import final, TypeVar
import math

__all__ = [
	'Vec2',
	'Rect',
]

Vec2Self = TypeVar('Vec2Self', bound='Vec2')

@final
class Vec2:
	__slots__ = ('_x', '_y')

	def __init__(self, x_xy: float | tuple[float, float] | Vec2Self, y: float | None = None, /):
		if isinstance(x_xy, Vec2):
			self._x, self._y = x_xy.x, x_xy.y
		elif isinstance(x_xy, tuple):
			self._x, self._y = x_xy
		else:
			self._x = x_xy
			self._y = x_xy if y is None else y

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

	@property
	def xy(self) -> tuple[float, float]:
		return self.x, self.y

	@xy.setter
	def xy(self, xy: tuple[float, float]):
		self.x, self.y = xy

	def __iter__(self):
		return iter((self.x, self.y))

	def copy(self) -> Vec2Self:
		return Vec2(self)

	def __str__(self) -> str:
		return f'({self.x}, {self.y})'

	def __repr__(self) -> str:
		return f'Vec2(x={self.x}, y={self.y})'

	def __eq__(self, other: tuple[float, float] | Vec2Self) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return self.x == other.x and self.y == other.y

	def __add__(self, other: float | tuple[float, float] | Vec2Self) -> Vec2Self:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x + other.x, self.y + other.y)

	def __sub__(self, other: float | tuple[float, float] | Vec2Self) -> Vec2Self:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x - other.x, self.y - other.y)

	def __mul__(self, other: float | tuple[float, float] | Vec2Self) -> Vec2Self:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x * other.x, self.y * other.y)

	def __truediv__(self, other: float | tuple[float, float] | Vec2Self) -> Vec2Self:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x / other.x, self.y / other.y)

	def __mod__(self, other: float | tuple[float, float] | Vec2Self) -> Vec2Self:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x % other.x, self.y % other.y)

	def distance_to(self, other: float | tuple[float, float] | Vec2Self) -> float:
		return math.sqrt(self.distance_to2(other))

	def distance_to2(self, other: float | tuple[float, float] | Vec2Self) -> float:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		dx, dy = self.x - other.x, self.y - other.y
		return dx * dx + dy * dy

	def in_range(self, other: float | tuple[float, float] | Vec2Self, range: float) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		dx, dy = self.x - other.x, self.y - other.y
		return dx <= range and dy <= range and dx * dx + dy * dy <= range * range


RectSelf = TypeVar('RectSelf', bound='Rect')

@final
class Rect:
	__slots__ = ('_x', '_y', '_w', '_h')

	def __init__(self,
			x_xy_xywh: float | tuple[float, float] | Vec2 | tuple[float, float, float, float] | RectSelf,
			y_w_wh: float | tuple[float, float] | Vec2 | None = None,
			w_h_wh: float | tuple[float, float] | Vec2 | None = None,
			h: float | None = None, /):
		"""
		Usage:
			Rect(x, y, w, h) ==
			Rect((x, y, w, h)) ==
			Rect((x, y), w, h) ==
			Rect(x, y, (w, h)) ==
		"""
		if isinstance(x_xy_xywh, Rect):
			self._x, self._y, self._w, self._h = x_xy_xywh.x, x_xy_xywh.y, x_xy_xywh.w, x_xy_xywh.h
		elif isinstance(x_xy_xywh, tuple):
			if len(x_xy_xywh) == 4:
				self._x, self._y, w_h_wh, h = x_xy_xywh
			else:
				self._x, self._y = x_xy_xywh
				w_h_wh, h = y_w_wh, w_h_wh
		else:
			self._x, self._y = x_xy_xywh, y_w_wh
		if isinstance(w_h_wh, Vec2):
			self._w, self._h = w_h_wh.x, w_h_wh.y
		elif isinstance(w_h_wh, tuple):
			self._w, self._h = w_h_wh
		else:
			self._w = w_h_wh
			self._h = h

	@property
	def x(self) -> float:
		return self._x

	@x.setter
	def x(self, x: float):
		assert isinstance(x, float)
		self._x = x

	@property
	def y(self) -> float:
		return self._y

	@y.setter
	def y(self, y: float):
		assert isinstance(y, float)
		self._y = y

	@property
	def xy(self) -> tuple[float, float]:
		return self.x, self.y

	@xy.setter
	def xy(self, xy: tuple[float, float]):
		self.x, self.y = xy

	def get_pos(self) -> Vec2:
		return Vec2(self.x, self.y)

	@property
	def w(self) -> float:
		return self._w

	@w.setter
	def w(self, w: float):
		assert isinstance(w, float)
		self._w = w

	@property
	def h(self) -> float:
		return self._h

	@h.setter
	def h(self, h: float):
		assert isinstance(h, float)
		self._h = h

	@property
	def wh(self) -> tuple[float, float]:
		return self.w, self.h

	@wh.setter
	def wh(self, wh: tuple[float, float]):
		self.w, self.h = wh

	def get_size(self) -> Vec2:
		return Vec2(self.w, self.h)

	def __iter__(self):
		return iter((self.x, self.y, self.w, self.h))

	def copy(self) -> RectSelf:
		return Rect(self)

	def __str__(self) -> str:
		return f'({self.x}, {self.y}, {self.w}, {self.h})'

	def __repr__(self) -> str:
		return f'Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})'

	def __eq__(self, other: tuple[float, float, float, float] | RectSelf) -> bool:
		if not isinstance(other, Rect):
			other = Rect(other)
		return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h
