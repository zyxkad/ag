# Copyright (C) 2023 zyxkad@gmail.com

import abc
from abc import abstractmethod
import functools
from threading import RLock

from .utils import *

__all__ = [
	'LOWEST_PRIORITY', 'HIGHEST_PRIORITY',
	'EventEmitter', 'Event', 'Events',
]

LOWEST_PRIORITY = object()
HIGHEST_PRIORITY = object()

class _Subscriber:
	def __init__(self, cb, priority: int):
		self._cb = cb
		assert isinstance(priority, int) or priority is LOWEST_PRIORITY or priority is HIGHEST_PRIORITY
		self._priority = priority

	@property
	def callback(self):
		return self._cb

	@property
	def priority(self) -> int:
		return self._priority

	def __lt__(self, other) -> bool:
		return self.priority is LOWEST_PRIORITY or (self.priority is not HIGHEST_PRIORITY and self.priority < other.priority)

	def __eq__(self, other) -> bool:
		return self.priority is not LOWEST_PRIORITY and self.priority is not HIGHEST_PRIORITY and self.priority == other.priority

	def __gt__(self, other) -> bool:
		return self.priority is HIGHEST_PRIORITY or (self.priority is not LOWEST_PRIORITY and self.priority > other.priority)

class EventEmitter:
	def __init__(self, name: str, *, cancelable: bool = False):
		assert isinstance(name, str)
		assert isinstance(cancelable, bool)
		self._name = name
		self._cancelable = cancelable
		self._lock = RLock()
		self._subscribers = []

	@property
	def name(self) -> str:
		return self._name

	@property
	def cancelable(self) -> bool:
		return self._cancelable

	def register(self, cb, *, priority: int = 0):
		assert callable(cb)
		s = _Subscriber(cb, priority)
		with self._lock:
			if priority is HIGHEST_PRIORITY:
				self._subscribers.append(s)
			else:
				i = 0
				if priority is not LOWEST_PRIORITY:
					i = binSearch(self._subscribers, target=s)
				self._subscribers.insert(i, s)
		return cb

	def unregister(self, key):
		with self._lock:
			for i, s in enumerate(self._subscribers):
				if s.callback is key:
					self._subscribers.pop(i)
					return
		raise LookupError('Subscriber not found')

	def emit(self, data=None):
		from inspect import signature
		e = Event(self, data)
		for s in reversed(self._subscribers.copy()):
			sig = signature(s.callback)
			if len(sig.parameters) == 0:
				s.callback()
			else:
				s.callback(e)
				if self.cancelable and e._canceled:
					return True

_EMPTY_DICT = DictWrapper({}, readonly=True)

class Event:
	def __init__(self, event: EventEmitter, data):
		assert isinstance(event, EventEmitter)
		self._event = event
		if data is None:
			data = _EMPTY_DICT
		elif isinstance(data, dict):
			data = DictWrapper(data, readonly=True)
		self._data = data
		self._canceled = False

	@property
	def event(self) -> str:
		return self._event

	@property
	def data(self):
		return self._data

	@property
	def cancelable(self) -> bool:
		return self.event.cancelable

	@property
	def canceled(self) -> bool:
		return self._canceled

	def cancel(self):
		if self.cancelable:
			self._canceled = True

class Events:
	# normal events
	QUIT      = EventEmitter('on.quit', cancelable=True)
	KEYDOWN   = EventEmitter('on.key.down', cancelable=True)
	KEYUP     = EventEmitter('on.key.up', cancelable=True)
	MOUSEMOVE = EventEmitter('on.mouse.move', cancelable=True)
	MOUSEDOWN = EventEmitter('on.mouse.down', cancelable=True)
	MOUSEUP   = EventEmitter('on.mouse.up', cancelable=True)
	# pygame other events
	EVENT     = EventEmitter('on.event', cancelable=True)
