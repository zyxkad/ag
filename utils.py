# Copyright (C) 2023 zyxkad@gmail.com

import inspect
from types import MethodType
from typing import TypeVar, Callable, Iterable

__all__ = [
	'get_origin_func',
	'dyn_call',
	'compare',
	'binSearch',
	'DictWrapper',
]

def get_origin_func(fn, /, stop_at=None):
	while (stop_at is None or not stop_at(fn)) and hasattr(fn, '__wrapped__'):
		fn = fn.__wrapped__
	return fn

def dyn_call(fn, *args, src=None, kwargs: dict | None = None):
	if src is None:
		src = get_origin_func(fn)
	sig = inspect.signature(src)
	argspec = inspect.getfullargspec(src)
	if argspec.varargs is None:
		arg_len = len(argspec.args)
		if isinstance(src, MethodType):
			arg_len -= 1
		args = args[:arg_len]
	if kwargs is None:
		kwargs = {}
	try:
		sig.bind(*args, **kwargs)
	except TypeError:
		raise
	return fn(*args, **kwargs)

def compare(a, b):
	return 0 if a == b else -1 if a < b else 1

T = TypeVar('T')

def binSearch(arr: Iterable[T], comparator: Callable[[T], int] | None = None, *,
	target: T | None = None) -> int:
	assert isinstance(arr, (list, tuple))
	if comparator is None:
		assert target is not None, 'either comparator or target must not be None'
		comparator = lambda a: compare(a, target)
	else:
		assert callable(comparator)
	l, r = 0, len(arr) - 1
	m = 0
	while l <= r:
		m = int((l + r) / 2)
		n = comparator(arr[m])
		if n == 0:
			return m
		if n < 0:
			l = m + 1
		else:
			r = m - 1
	return l

class DictWrapper:
	def __init__(self, data: dict, *, readonly: bool = False):
		assert isinstance(data, dict)
		self.__data = data
		self.__readonly = readonly

	def __getattribute__(self, name: str, /):
		if name.startswith('_'):
			return super().__getattribute__(name)
		return self[name]

	def __setattr__(self, name: str, val, /):
		if name.startswith('_'):
			super().__setattr__(name, val)
		else:
			assert not self.__readonly, 'Dict is readonly'
			self[name] = val

	def __getitem__(self, key: str, /):
		return self.__data[key]

	def __setitem__(self, key: str, val, /):
		assert not self.__readonly, 'Dict is readonly'
		self.__data[key] = val

	def __iter__(self):
		return iter(self.__data)

	def __str__(self) -> str:
		return str(self.__data)

	def __repr__(self) -> str:
		return f'<DictWrapper{" readonly" if self.__readonly else ""} wrapped at 0x{id(self.__data):x}>'
