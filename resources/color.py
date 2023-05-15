# Copyright (C) 2023 zyxkad@gmail.com

from typing import TypeVar

__all__ = [
	'Color',
	'Colors',
]

Self = TypeVar('Self', bound='Color')

class Color:
	def __init__(self, r: int, g: int, b: int, a: int = 0xff):
		assert isinstance(r, int) and 0 <= r and r <= 0xff
		assert isinstance(g, int) and 0 <= g and g <= 0xff
		assert isinstance(b, int) and 0 <= b and b <= 0xff
		assert isinstance(a, int) and 0 <= a and a <= 0xff
		self._r = r
		self._g = g
		self._b = b
		self._a = a

	@classmethod
	def from_rgb(cls, r, g, b):
		if isinstance(r, float):
			assert 0.0 <= r and r <= 1.0
			r = int(r * 0xff)
		if isinstance(g, float):
			assert 0.0 <= g and g <= 1.0
			g = int(g * 0xff)
		if isinstance(b, float):
			assert 0.0 <= b and b <= 1.0
			b = int(b * 0xff)
		return cls(r, g, b, 0xff)

	@classmethod
	def from_rgba(cls, r, g, b, a):
		if isinstance(r, float):
			assert 0.0 <= r and r <= 1.0
			r = int(r * 0xff)
		if isinstance(g, float):
			assert 0.0 <= g and g <= 1.0
			g = int(g * 0xff)
		if isinstance(b, float):
			assert 0.0 <= b and b <= 1.0
			b = int(b * 0xff)
		if isinstance(a, float):
			assert 0.0 <= a and a <= 1.0
			a = int(a * 0xff)
		return cls(r, g, b, a)

	@classmethod
	def from_html_rgb(cls, rgb):
		assert isinstance(v, int) and 0 <= rgb and rgb <= 0xffffff
		return cls(rgb >> 16, (rgb >> 8) & 0xff, rgb & 0xff, 0xff)

	@classmethod
	def from_html_rgba(cls, rgba):
		assert isinstance(v, int) and 0 <= rgba and rgba <= 0xffffffff
		return cls(rgba >> 24, (rgba >> 16) & 0xff, (rgba >> 8) & 0xff, rgba & 0xff)

	def copy(self) -> Self:
		return self.__class__(self.r, self.g, self.b, self.a)

	@property
	def r(self) -> int:
		return self._r

	def set_r(self, v: int) -> Self:
		assert isinstance(v, int) and 0 <= v and v <= 0xff
		c = self.copy()
		c._r = v
		return c

	@property
	def g(self) -> int:
		return self._g

	def set_g(self, v: int) -> Self:
		assert isinstance(v, int) and 0 <= v and v <= 0xff
		c = self.copy()
		c._g = v
		return c

	@property
	def b(self) -> int:
		return self._b

	def set_b(self, v: int) -> Self:
		assert isinstance(v, int) and 0 <= v and v <= 0xff
		c = self.copy()
		c._b = v
		return c

	@property
	def a(self) -> int:
		return self._a

	def set_a(self, v: int) -> Self:
		assert isinstance(v, int) and 0 <= v and v <= 0xff
		c = self.copy()
		c._a = v
		return c

	@property
	def visible(self) -> bool:
		return self._a != 0

	@property
	def rgb(self) -> tuple[int, int, int]:
		return self.r, self.g, self.b

	@property
	def rgba(self) -> tuple[int, int, int, int]:
		return self.r, self.g, self.b, self.a

	@property
	def html_rgb(self) -> int:
		return (self.r << 16) | (self.g << 8) | self.b

	@property
	def html_rgba(self) -> int:
		return (self.r << 24) | (self.g << 16) | (self.b << 8) | self.a

	def __int__(self) -> int:
		return self.html_rgba

	def __str__(self) -> str:
		return f'({self.r}, {self.g}, {self.b}, {self.a})'

	def __repr__(self) -> str:
		return f'<Color({self.r}, {self.g}, {self.b}, {self.a})>'

	def __eq__(self, other) -> bool:
		return other is self or (isinstance(other, Color) and
			(not other.visible and not self.visible or 
			 (other.r == self.r and other.g == self.g and other.b == self.b and other.a == self.a)))

	def __hash__(self) -> int:
		return hash(self.rgba)

	def __ne__(self, other) -> bool:
		return not isinstance(other, Color) or ((other.visible or self.visible) and
			(other.r != self.r or other.g != self.g or other.b != self.b or other.a != self.a))

	def __lt__(self, other: Self) -> bool:
		assert isinstance(other, Color)
		return (self.visible or other.visible) and self.a < other.a or (self.a == other.a and self.html_rgb < other.html_rgb)

	def __le__(self, other: Self) -> bool:
		assert isinstance(other, Color)
		return not (self.visible or other.visible) or (self.a <= other.a and self.html_rgb <= other.html_rgb)

	def __gt__(self, other: Self) -> bool:
		assert isinstance(other, Color)
		return (self.visible or other.visible) and self.a > other.a or (self.a == other.a and self.html_rgb > other.html_rgb)

	def __ge__(self, other: Self) -> bool:
		assert isinstance(other, Color)
		return not (self.visible or other.visible) or (self.a >= other.a and self.html_rgb >= other.html_rgb)

	def __and__(self, other: Self) -> Self:
		return Color(self.r & other.r, self.g & other.g, self.b & other.b, self.a & other.a)

	def __or__(self, other: Self) -> Self:
		return Color(self.r | other.r, self.g | other.g, self.b | other.b, self.a | other.a)

class Colors:
	black  = Color(0, 0, 0)
	gray   = Color(0x7f, 0x7f, 0x7f)
	white  = Color(0xff, 0xff, 0xff)
	red    = Color(0xff, 0, 0)
	green  = Color(0, 0xff, 0)
	blue   = Color(0, 0, 0xff)
	yellow = Color(0xff, 0xff, 0)
	purple = Color(0xff, 0, 0xff)
	aqua   = Color(0, 0xff, 0xff)

	transparent      = Color(0xff, 0xff, 0xff, 0)
	hald_transparent = Color(0xff, 0xff, 0xff, 0x7f)
