# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

from typing import Self
from weakref import WeakValueDictionary

from .color import *
from .surface import *

import pygame

__all__ = [
	'Font',
	'FontSet',
]

class Font:
	_SYS_CACHE = WeakValueDictionary[tuple[str, int], 'Font']()
	_LOCAL_CACHE = WeakValueDictionary[tuple[str, int], 'Font']()

	def __new__(cls, *, sysname: str | None = None, path: str | None = None,
		size: int = 10,
		font_obj: pygame.font.Font | None = None, cached: bool = True):
		assert isinstance(sysname, (str, type(None)))
		assert isinstance(path, (str, type(None)))
		assert (sysname, path, font_obj).count(None) == 2
		assert isinstance(size, (int, )) and size > 0
		if cached and font_obj is None:
			if sysname is not None:
				c = cls._SYS_CACHE.get((sysname, size), None)
				if c is not None:
					return c
			elif path is not None:
				c = cls._LOCAL_CACHE.get((path, size), None)
				if c is not None:
					return c
		o = super().__new__(cls)
		cls.__init(o, sysname=sysname, path=path, size=size, font_obj=font_obj)
		if cached and font_obj is None:
			if sysname is not None:
				cls._SYS_CACHE[(sysname, size)] = o
			elif path is not None:
				cls._LOCAL_CACHE[(path, size)] = o
		return o

	_sysname: str | None
	_path: str | None
	_size: int
	__font_obj: pygame.font.Font
	_cache: dict[str, Font]

	@classmethod
	def __init(cls, self, *, sysname: str | None, path: str | None,
		size: int, font_obj: pygame.font.Font | None):
		self._sysname = sysname
		self._path = path
		self._size = size
		self.__font_obj = font_obj
		self._cache = {
			'': self,
		}

		if self.__font_obj is None:
			self._load()

	@classmethod
	def default(cls, size: int = 10) -> Self:
		return cls(sysname=pygame.font.get_default_font(), size=size)

	@property
	def issys(self) -> bool:
		return self._sysname is not None

	@property
	def islocal(self) -> bool:
		return self._path is not None

	@property
	def isnative(self) -> bool:
		return not (self.issys or self.islocal)

	@property
	def sysname(self) -> str:
		assert self._sysname is not None
		return self._sysname

	@property
	def path(self) -> str:
		assert self._path is not None
		return self._path

	@property
	def size(self) -> int:
		return self._size

	@property
	def native(self) -> object:
		return self.__font_obj

	def _load(self):
		if self.issys:
			self.__font_obj = pygame.font.SysFont(self.sysname, self.size)
		elif self.islocal:
			self.__font_obj = pygame.font.Font(self.path, self.size)

	def copy(self) -> Self:
		cls = self.__class__
		o = None
		if self.issys:
			o = cls(sysname=self.sysname, size=self._size, cached=False)
		elif self.islocal:
			o = cls(path=self.path, size=self._size, cached=False)
		else:
			raise RuntimeError('Cannot copy native font obj')
		return o

	@property
	def fontsize(self) -> int:
		return self._size

	def set_fontsize(self, size: int):
		if size == self._size:
			return self
		cls = self.__class__
		o = None
		if self.issys:
			o = cls(sysname=self.sysname, size=size)
		elif self.islocal:
			o = cls(path=self.path, size=size)
		else:
			raise RuntimeError('Cannot copy native font obj')
		return

	def get_size(self, text: str) -> tuple[int, int]:
		assert isinstance(text, str)
		return self.__font_obj.size(text)

	def _get_style_or_set(self, key, setter):
		f = self._cache.get(key, None)
		if f is not None:
			return f
		f = self.copy()
		setter(f)
		f._cache = self._cache
		self._cache[key] = f
		return f

	@property
	def style_codes(self) -> str:
		s = ''
		if self.is_bold:
			s += 'b'
		if self.is_italic:
			s += 'i'
		if self.is_striketh:
			s += 's'
		if self.is_underlined:
			s += 'u'
		return s

	@property
	def is_bold(self) -> bool:
		return self.__font_obj.bold

	@property
	def bold(self) -> Self:
		if self.is_bold:
			return self
		def setter(f):
			f.__font_obj.bold = True
		return self._get_style_or_set('b' + self.style_codes, setter)

	@property
	def is_italic(self) -> bool:
		return self.__font_obj.italic

	@property
	def italic(self) -> Self:
		if self.is_italic:
			return self
		def setter(f):
			f.__font_obj.italic = True
		return self._get_style_or_set(''.join(sorted(set(self.style_codes) | {'i'})), setter)

	@property
	def is_underlined(self) -> bool:
		return self.__font_obj.underline

	@property
	def underlined(self) -> Self:
		if self.is_underlined:
			return self
		def setter(f):
			f.__font_obj.underline = True
		return self._get_style_or_set(self.style_codes + 'u', setter)

	@property
	def is_striketh(self) -> bool:
		return self.__font_obj.strikethrough

	@property
	def striketh(self) -> Self:
		if self.is_striketh:
			return self
		def setter(f):
			f.__font_obj.strikethrough = True
		return self._get_style_or_set(''.join(sorted(set(self.style_codes) | {'s'})), setter)

	def render(self, text: str, /, color: Color, antialias: bool = False, background: Color | None = None, *,
		bold: bool = False, italic: bool = False, underlined: bool = False, striketh: bool = False) -> Surface:
		assert isinstance(color, Color)
		pcolor = pygame.Color(color.rgba)
		pbackground = None if background is None else pygame.Color(background.rgba)
		f = self
		if bold:
			f = f.bold
		if italic:
			f = f.italic
		if striketh:
			f = f.striketh
		if underlined:
			f = f.underlined
		s = Surface(f.__font_obj.render(text, antialias, pcolor, pbackground))
		return s

class FontSet:
	def __init__(self, normal: Font | str, size: int | None = None, *,
		bold: Font | None = None, italic: Font | None = None, underlined: Font | None = None,
		bold_italic: Font | None = None, bold_underlined: Font | None = None, italic_underlined: Font | None = None,
		bold_italic_underlined: Font | None = None):
		if size is None:
			assert isinstance(normal, Font)
			size = normal.fontsize
		elif isinstance(normal, str):
			normal = Font(path=normal, size=size)
		else:
			normal = normal.set_fontsize(size)
		assert isinstance(normal, Font)
		if isinstance(bold, str):
			bold = Font(path=bold, size=size)
		elif bold is not None:
			assert isinstance(bold, Font)
			assert bold.fontsize == size
		if isinstance(italic, str):
			italic = Font(path=italic, size=size)
		elif italic is not None:
			assert isinstance(italic, Font)
			assert italic.fontsize == size
		if isinstance(underlined, str):
			underlined = Font(path=underlined, size=size)
		elif underlined is not None:
			assert isinstance(underlined, Font)
			assert underlined.fontsize == size
		if isinstance(bold_italic, str):
			bold_italic = Font(path=bold_italic, size=size)
		elif bold_italic is not None:
			assert isinstance(bold_italic, Font)
			assert bold_italic.fontsize == size
		if isinstance(bold_underlined, str):
			bold_underlined = Font(path=bold_underlined, size=size)
		elif bold_underlined is not None:
			assert isinstance(bold_underlined, Font)
			assert bold_underlined.fontsize == size
		if isinstance(italic_underlined, str):
			italic_underlined = Font(path=italic_underlined, size=size)
		elif italic_underlined is not None:
			assert isinstance(italic_underlined, Font)
			assert italic_underlined.fontsize == size
		if isinstance(bold_italic_underlined, str):
			bold_italic_underlined = Font(path=bold_italic_underlined, size=size)
		elif bold_italic_underlined is not None:
			assert isinstance(bold_italic_underlined, Font)
			assert bold_italic_underlined.fontsize == size
		self._normal = normal
		self._b = bold
		self._i = italic
		self._u = underlined
		self._bi = bold_italic
		self._bu = bold_underlined
		self._iu = italic_underlined
		self._biu = bold_italic_underlined

	@property
	def normal(self) -> Font:
		return self._normal

	@property
	def bold(self) -> Font:
		return self._b or self.normal.bold

	@property
	def italic(self) -> Font:
		return self._i or self.normal.italic

	@property
	def underlined(self) -> Font:
		return self._u or self.normal.underlined

	@property
	def bold_italic(self) -> Font:
		if self._bi is not None:
			return self._bi
		if self._b is not None and not self._b.isnative:
			return self._b.italic
		if self._i is not None and not self._i.isnative:
			return self._i.bold
		return self.normal.bold.italic

	@property
	def bold_underlined(self) -> Font:
		if self._bu is not None:
			return self._bu
		if self._b is not None and not self._b.isnative:
			return self._b.underlined
		if self._u is not None and not self._u.isnative:
			return self._u.bold
		return self.normal.bold.underlined

	@property
	def italic_underlined(self) -> Font:
		if self._iu is not None:
			return self._iu
		if self._i is not None and not self._i.isnative:
			return self._i.underlined
		if self._u is not None and not self._u.isnative:
			return self._u.italic
		return self.normal.italic.underlined

	@property
	def bold_italic_underlined(self) -> Font:
		if self._biu is not None:
			return self._biu
		if self._bi is not None and not self._bi.isnative:
			return self._bi.underlined
		if self._iu is not None and not self._iu.isnative:
			return self._iu.bold
		if self._bu is not None and not self._bu.isnative:
			return self._bu.italic
		if self._b is not None and not self._b.isnative:
			return self._b.italic.underlined
		if self._i is not None and not self._i.isnative:
			return self._i.bold.underlined
		if self._u is not None and not self._u.isnative:
			return self._u.bold.italic
		return self.normal.bold.italic.underlined

	def render(self, text: str, /, color: Color, antialias: bool = False, background: Color | None = None, *,
		bold: bool = False, italic: bool = False, underlined: bool = False, striketh: bool = False) -> Surface:
		assert isinstance(color, Color)
		pcolor = pygame.Color(color.rgba)
		pbackground = None if background is None else pygame.Color(background.rgba)
		f = self.normal
		sty = ''
		if bold:
			sty += 'b'
		if italic:
			sty += 'i'
		if underlined:
			sty += 'u'
		if sty == 'b':
			f = self.bold
		elif sty == 'i':
			f = self.italic
		elif sty == 'u':
			f = self.underlined
		elif sty == 'bi':
			f = self.bold_italic
		elif sty == 'bu':
			f = self.bold_underlined
		elif sty == 'iu':
			f = self.italic_underlined
		elif sty == 'biu':
			f = self.bold_italic_underlined
		if striketh:
			f = f.striketh
		s = Surface(f.__font_obj.render(text, antialias, pcolor, pbackground))
		return s
