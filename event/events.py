# Copyright (C) 2023 zyxkad@gmail.com

from typing import final, Any

from .base import *

__all__ = [
	'CustomEvent',
	'QuitEvent',
	'UIEvent',
	'LoadEvent',
	'KeyboardEvent',
	'MOUSE_MAIN_BUTTON', 'MOUSE_MIDDLE_BUTTON', 'MOUSE_SECONDARY_BUTTON',
	'MouseEvent', 'MouseClickEvent', 'MouseMoveEvent', 'MouseOverEvent',
]

@final
class CustomEvent(Event):
	def __init__(self, etype: str, details: Any = None):
		super().__init__(etype)
		self._details = details

	@property
	def details(self) -> Any:
		return self._details

@final
class QuitEvent(Event):
	def __init__(self):
		super().__init__('quit', bubbles=False, cancelable=True)

class UIEvent(Event):
	def __init__(self, etype: str, target: EventTarget | None, *,
		bubbles: bool = True, cancelable: bool = False):
		super().__init__(etype, bubbles=bubbles, cancelable=cancelable)
		self._target = target

	@property
	def target(self) -> EventTarget | None:
		return self._target

class LoadEvent(UIEvent):
	def __init__(self, etype: str, target: EventTarget | None, *,
		bubbles: bool = True, cancelable: bool = False):
		assert etype in ('load', 'unload')
		super().__init__(etype, target, bubbles=bubbles, cancelable=cancelable)

class _KeyEvent(UIEvent):
	def __init__(self, etype: str, target: EventTarget | None, *,
		alt: bool, ctrl: bool, meta: bool, shift: bool,
		bubbles: bool = True, cancelable: bool = True):
		super().__init__(etype, target, bubbles=bubbles, cancelable=cancelable)
		self._alt = alt
		self._ctrl = ctrl
		self._meta = meta
		self._shift = shift

	@property
	def alt(self) -> bool:
		return self._alt

	@property
	def ctrl(self) -> bool:
		return self._ctrl

	@property
	def meta(self) -> bool:
		return self._meta

	@property
	def shift(self) -> bool:
		return self._shift

@final
class KeyboardEvent(_KeyEvent):
	def __init__(self, etype: str, target: EventTarget | None, key: int,
		alt: bool, ctrl: bool, meta: bool, shift: bool,
		bubbles: bool = True, cancelable: bool = True):
		assert etype in ('keydown', 'keyup')
		super().__init__(etype, target,
			alt=alt, ctrl=ctrl, meta=meta, shift=shift,
			bubbles=bubbles, cancelable=cancelable)
		self._key = key

	@property
	def key(self) -> int:
		return self._key

MOUSE_MAIN_BUTTON = 0
MOUSE_MIDDLE_BUTTON = 1
MOUSE_SECONDARY_BUTTON = 2

class MouseEvent(_KeyEvent):
	def __init__(self, etype: str, target: EventTarget, *,
		x: float, y: float,
		viewX: float, viewY: float, screenX: int, screenY: int,
		buttons: int,
		alt: bool, ctrl: bool, meta: bool, shift: bool,
		bubbles: bool = True, cancelable: bool = True):
		assert etype in (
			'click', 'dbclick', 'mouseup', 'mousedown',
			'mousemove',
			'mouseenter', 'mouseover', 'mouseleave', 'mouseout')
		super().__init__(etype, target,
			alt=alt, ctrl=ctrl, meta=meta, shift=shift,
			bubbles=bubbles, cancelable=cancelable)
		self._x = x
		self._y = y
		self._viewX = viewX
		self._viewY = viewY
		self._screenX = screenX
		self._screenY = screenY
		self._buttons = buttons

	@property
	def buttons(self) -> int:
		return self._buttons

	@property
	def x(self) -> float:
		return self._x

	@property
	def y(self) -> float:
		return self._y

	@property
	def viewX(self) -> float:
		return self._viewX

	@property
	def viewY(self) -> float:
		return self._viewY

	@property
	def screenX(self) -> int:
		return self._screenX

	@property
	def screenY(self) -> int:
		return self._screenY

@final
class MouseClickEvent(MouseEvent):
	def __init__(self, etype: str, target: EventTarget, button: int, **kwargs):
		assert etype in ('click', 'dbclick', 'mouseup', 'mousedown')
		super().__init__(etype, target, **kwargs)
		self._button = button

	@property
	def button(self) -> int:
		return self._button

@final
class MouseMoveEvent(MouseEvent):
	def __init__(self, target: EventTarget, *, dx: int, dy: int, **kwargs):
		super().__init__('mousemove', target, **kwargs)
		self._dx = dx
		self._dy = dy

	@property
	def dx(self) -> int:
		return self._dx

	@property
	def dy(self) -> int:
		return self._dy

@final
class MouseOverEvent(MouseEvent):
	def __init__(self, etype: str, target: EventTarget, related_target: EventTarget | None,
		bubbles: bool = False, cancelable: bool = False,
		**kwargs):
		assert etype in ('mouseenter', 'mouseover', 'mouseleave', 'mouseout')
		super().__init__(etype, target,
			bubbles=bubbles, cancelable=cancelable, **kwargs)
		self._related_target = related_target

	@property
	def related_target(self) -> EventTarget | None:
		return self._related_target
