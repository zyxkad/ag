# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

import abc
from abc import abstractmethod
import functools
from threading import Lock
from typing import Callable, TypeAlias, TypeVar

from ..utils import *

__all__ = [
	'LOWEST_PRIORITY', 'HIGHEST_PRIORITY',
	'on',
	'EventTarget', 'Event',
]

class _EndlessPriority:
	pass

LOWEST_PRIORITY = _EndlessPriority()
HIGHEST_PRIORITY = _EndlessPriority()

class Event:
	def __init__(self, etype: str, *,
		bubbles: bool = False, cancelable: bool = False):
		self._etype = etype
		self._bubbles = bubbles
		self._cancelable = cancelable
		self._canceled = False
		self._current_target: EventTarget | None = None

	@property
	def type(self) -> str:
		return self._etype

	@property
	def bubbles(self) -> bool:
		return self._bubbles

	@property
	def cancelable(self) -> bool:
		return self._cancelable

	@property
	def canceled(self) -> bool:
		return self._canceled

	def cancel(self):
		if self.cancelable:
			self._canceled = True

	@property
	def current_target(self) -> EventTarget | None:
		return self._current_target

EventT = TypeVar('EventT', bound=Event)
EventCallback: TypeAlias = Callable[[EventT], None]

class _Subscriber:
	def __init__(self, cb: EventCallback, priority: int | _EndlessPriority, *, once: bool):
		self._cb = cb
		assert isinstance(priority, (int, _EndlessPriority))
		self._priority = priority
		self._once = once

	@property
	def callback(self) -> EventCallback:
		return self._cb

	@property
	def priority(self) -> int | _EndlessPriority:
		return self._priority

	@property
	def once(self) -> bool:
		return self._once

	def __lt__(self, other) -> bool:
		return self.priority is LOWEST_PRIORITY or (self.priority is not HIGHEST_PRIORITY and self.priority < other.priority)

	def __eq__(self, other) -> bool:
		return self.priority is not LOWEST_PRIORITY and self.priority is not HIGHEST_PRIORITY and self.priority == other.priority

	def __gt__(self, other) -> bool:
		return self.priority is HIGHEST_PRIORITY or (self.priority is not LOWEST_PRIORITY and self.priority > other.priority)

class _WrappedMethod:
	def __init__(self, etype: str, cb: EventCallback,
		capture: bool = False, *,
		priority: int | _EndlessPriority = 0, once: bool = False):
		self.etype = etype
		self.iscapture = capture
		self.subscriber = _Subscriber(cb, priority, once=once)

	def __call__(self, *args, **kwargs):
		return self.subscriber.callback(*args, **kwargs)

def on(etype: str,
	capture: bool = False, *,
	priority: int | _EndlessPriority = 0, once: bool = False):
	def wrapper(cb: EventCallback):
		return functools.wraps(cb)(_WrappedMethod(etype, cb, capture, priority=priority, once=once))
	return wrapper

class EventTarget:
	__cls_listeners: list[_WrappedMethod]

	def __init_subclass__(cls, **kwargs):
		super().__init_subclass__(**kwargs)
		cls.__cls_listeners = [f for f in vars(cls).values() if isinstance(f, _WrappedMethod)]

	def __init__(self):
		cls = self.__class__
		self._lock = Lock()
		self._listeners: dict[str, tuple[list[_Subscriber], list[_Subscriber]]] = {}

		for f in cls.__cls_listeners:
			listeners2 = self._listeners.get(f.etype, None)
			if listeners2 is None:
				self._listeners[f.etype] = ([f.subscriber], []) if f.iscapture else ([], [f.subscriber])
			else:
				listeners = listeners2[0 if f.iscapture else 1]
				if f.subscriber.priority is HIGHEST_PRIORITY:
					listeners.append(f.subscriber)
				else:
					i = 0
					if f.subscriber.priority is not LOWEST_PRIORITY:
						i = binSearch(listeners, target=f.subscriber)
					listeners.insert(i, f.subscriber)

	def dispatch(self, event: Event, capture: bool | None = None) -> bool:
		if event.type not in self._listeners:
			return True
		event._current_target = self
		captures, bubbles = self._listeners[event.type]
		if capture is not False:
			for s in captures:
				dyn_call(s.callback, event)
				if event.cancelable and event.canceled:
					return False
		if capture is not True:
			for s in bubbles:
				dyn_call(s.callback, event)
				if event.cancelable and event.canceled:
					return False
		return True

	def register(self, etype: str, cb: EventCallback, *,
		priority: int | _EndlessPriority = 0, once: bool = False,
		capture: bool = False) -> EventCallback:
		s = _Subscriber(cb, priority, once=once)
		with self._lock:
			listeners2 = self._listeners.get(etype, None)
			if listeners2 is None:
				self._listeners[etype] = ([s], []) if capture else ([], [s])
			else:
				listeners = listeners2[0 if capture else 1]
				if priority is HIGHEST_PRIORITY:
					listeners.append(s)
				else:
					i = 0
					if priority is not LOWEST_PRIORITY:
						i = binSearch(listeners, target=s)
					listeners.insert(i, s)
		return cb

	def unregister(self, etype: str, cb: EventCallback | None = None, capture: bool = False) -> None:
		with self._lock:
			if cb is None:
				self._listeners.pop(etype, None)
				return
			if etype in self._listeners:
				listeners = self._listeners[etype][0 if capture else 1]
				for i, s in enumerate(listeners):
					if s.callback is cb:
						listeners.pop(i)
						return
		raise LookupError('Listener not found')

	def unregister_all(self) -> None:
		with self._lock:
			self._listeners.clear()
