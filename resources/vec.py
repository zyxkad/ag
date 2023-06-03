# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

from typing import final, no_type_check, TypeVar
import math

__all__ = [
	'Vec2',
	'Rect',
]

@final
class Vec2:
	ZERO: Vec2

	__slots__ = ('_x', '_y')

	_x: float
	_y: float

	def __init__(self, x_xy: float | tuple[float, float] | Vec2, y: float | None = None, /):
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

	@property
	def y(self) -> float:
		return self._y

	@property
	def xy(self) -> tuple[float, float]:
		return self.x, self.y

	def __iter__(self):
		return iter((self.x, self.y))

	def copy(self) -> Vec2:
		return Vec2(self)

	def __str__(self) -> str:
		return f'({self.x}, {self.y})'

	def __repr__(self) -> str:
		return f'Vec2(x={self.x}, y={self.y})'

	def __eq__(self, other: object) -> bool:
		if isinstance(other, tuple):
			other = Vec2(other[0:1]) # type: ignore
		elif not isinstance(other, Vec2):
			return False
		return self.x == other.x and self.y == other.y

	def __hash__(self) -> int:
		return hash(self.xy)

	def __lt__(self, other: tuple[float, float] | Vec2) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return self.x < other.x and self.y < other.y

	def __le__(self, other: tuple[float, float] | Vec2) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return self.x <= other.x and self.y <= other.y

	def __gt__(self, other: tuple[float, float] | Vec2) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return self.x > other.x and self.y > other.y

	def __ge__(self, other: tuple[float, float] | Vec2) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return self.x >= other.x and self.y >= other.y

	def __add__(self, other: float | tuple[float, float] | Vec2) -> Vec2:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x + other.x, self.y + other.y)

	def __sub__(self, other: float | tuple[float, float] | Vec2) -> Vec2:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x - other.x, self.y - other.y)

	def __mul__(self, other: float | tuple[float, float] | Vec2) -> Vec2:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x * other.x, self.y * other.y)

	def __truediv__(self, other: float | tuple[float, float] | Vec2) -> Vec2:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x / other.x, self.y / other.y)

	def __mod__(self, other: float | tuple[float, float] | Vec2) -> Vec2:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		return Vec2(self.x % other.x, self.y % other.y)

	def distance_to(self, other: float | tuple[float, float] | Vec2) -> float:
		return math.sqrt(self.distance_to2(other))

	def distance_to2(self, other: float | tuple[float, float] | Vec2) -> float:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		dx, dy = self.x - other.x, self.y - other.y
		return dx * dx + dy * dy

	def in_range(self, other: float | tuple[float, float] | Vec2, range: float) -> bool:
		if not isinstance(other, Vec2):
			other = Vec2(other)
		dx, dy = self.x - other.x, self.y - other.y
		return dx <= range and dy <= range and dx * dx + dy * dy <= range * range

Vec2.ZERO = Vec2(0, 0)

@final
class Rect:
	__slots__ = ('_x', '_y', '_w', '_h')

	_x: float
	_y: float
	_w: float
	_h: float

	@no_type_check
	def __init__(self,
			x_xy_xywh: float | tuple[float, float] | Vec2 | tuple[float, float, float, float] | Rect,
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

	@property
	def y(self) -> float:
		return self._y

	@property
	def xy(self) -> tuple[float, float]:
		return self.x, self.y

	@property
	def pos(self) -> Vec2:
		return Vec2(self.x, self.y)

	@property
	def w(self) -> float:
		return self._w

	@property
	def h(self) -> float:
		return self._h

	@property
	def wh(self) -> tuple[float, float]:
		return self.w, self.h

	@property
	def size(self) -> Vec2:
		return Vec2(self.w, self.h)

	def __iter__(self):
		return iter((self.x, self.y, self.w, self.h))

	def copy(self) -> Rect:
		return Rect(self)

	def __str__(self) -> str:
		return f'({self.x}, {self.y}, {self.w}, {self.h})'

	def __repr__(self) -> str:
		return f'Rect(x={self.x}, y={self.y}, w={self.w}, h={self.h})'

	def __eq__(self, other: object) -> bool:
		if isinstance(other, tuple):
			other = Rect(other[0:4])
		elif not isinstance(other, Rect):
			return False
		return self.x == other.x and self.y == other.y and self.w == other.w and self.h == other.h

	def __hash__(self) -> int:
		return hash((self.x, self.y, self.w, self.h))

	def sub_xy(self, other: float | tuple[float, float] | Vec2) -> Rect:
		return Rect(self.pos - other, self.size)

	def sub_wh(self, other: float | tuple[float, float] | Vec2) -> Rect:
		return Rect(self.pos, self.size - other)
