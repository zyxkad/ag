# Copyright (C) 2023 zyxkad@gmail.com

from __future__ import annotations

from typing import TypeVar, Generic, Callable

from ..event import on, Event, EventTarget, LoadEvent
from ..scheduler import *
from ..resources import Vec2, Surface, Anchor
from ..utils import *

import pygame

__all__ = [
	'Node',
]

class Node(EventTarget):
	def __init__(self, *,
		tag: int | None = None, name: str | None = None,
		scheduler: Scheduler | None = None,
		x: float = 0, y: float = 0, width: float = 0, height: float = 0,
		anchor: Anchor = Anchor.CENTER,
		z_index: int = 0, scale: tuple[float, float] = (1, 1),
		visible: bool = True, rotation: float = 0,
		selectable: bool = True):
		super().__init__()
		self._parent: Node | None = None
		self._children: list[Node] = []
		self._tag = tag
		self._name = name

		self._scheduler = scheduler

		self.__x = x
		self.__y = y
		self.__width = width
		self.__height = height
		self.__anchor = anchor
		self._z_index = z_index
		self._scaleX = scale[0]
		self._scaleY = scale[1]
		self._visible = visible
		self._rotation = rotation
		self._selectable = selectable
		self._focusing = False
		self._loaded = False
		self._cursors: list[pygame.Cursor] = []

		self._schedule_upadate_interval: float | None = None
		self._update_task = None

	def dispatch(self, event: Event, capture: bool | None = None):
		nodes = self.parents
		if capture is not False:
			for n in reversed(nodes):
				EventTarget.dispatch(n, event, capture=True)
		super().dispatch(event, capture=capture)
		if event.bubbles and capture is not True:
			for n in nodes:
				EventTarget.dispatch(n, event, capture=False)

	@property
	def tag(self) -> int | None:
		return self._tag

	@tag.setter
	def tag(self, tag: int | None):
		self._tag = tag

	@property
	def name(self) -> str | None:
		return self._name

	@name.setter
	def name(self, name: str | None):
		self._name = name

	@property
	def scheduler(self) -> Scheduler | None:
		return self._scheduler or (None if self.parent is None else self.parent.scheduler)

	@scheduler.setter
	def scheduler(self, scheduler: Scheduler):
		self._scheduler = scheduler

	def schedule_update(self, interval: float | None = 0.05):
		self._schedule_upadate_interval = interval

	@property
	def x(self) -> float:
		return self.__x

	@x.setter
	def x(self, x: float):
		assert isinstance(x, (int, float))
		self.__x = x

	@property
	def y(self) -> float:
		return self.__y

	@y.setter
	def y(self, y: float):
		assert isinstance(y, (int, float))
		self.__y = y

	@property
	def pos(self) -> Vec2:
		return Vec2(self.x, self.y)

	@property
	def width(self) -> float:
		return self.__width

	@width.setter
	def width(self, width: float):
		assert isinstance(width, (int, float))
		self.__width = width

	@property
	def height(self) -> float:
		return self.__height

	@height.setter
	def height(self, height: float):
		assert isinstance(height, (int, float))
		self.__height = height

	@property
	def size(self) -> Vec2:
		return Vec2(self.width, self.height)

	@property
	def anchor(self) -> Anchor:
		return self.__anchor

	@anchor.setter
	def anchor(self, anchor: Anchor):
		self.__anchor = anchor

	@property
	def z_index(self) -> int:
		return self._z_index

	@z_index.setter
	def z_index(self, z_index: int):
		assert isinstance(z_index, int)
		self._z_index = z_index

	@property
	def scaleX(self) -> float:
		return self._scaleX

	@scaleX.setter
	def scaleX(self, scaleX: float):
		assert isinstance(scaleX, (int, float))
		self._scaleX = scaleX

	@property
	def scaleY(self) -> float:
		return self._scaleY

	@scaleY.setter
	def scaleY(self, scaleY: float):
		assert isinstance(scaleY, (int, float))
		self._scaleY = scaleY

	@property
	def scale(self) -> Vec2:
		return Vec2(self._scaleX, self._scaleY)

	@property
	def visible(self) -> bool:
		return self._visible

	@visible.setter
	def visible(self, visible: bool):
		assert isinstance(visible, bool)
		self._visible = visible

	@property
	def rotation(self) -> float:
		return self._rotation

	@rotation.setter
	def rotation(self, rotation: float):
		self._rotation = rotation

	@property
	def selectable(self) -> bool:
		return self._selectable

	@selectable.setter
	def selectable(self, selectable: bool):
		self._selectable = selectable

	@property
	def focusing(self) -> bool:
		return self._focusing

	@property
	def loaded(self) -> bool:
		return self._loaded

	@property
	def parent(self) -> Node | None:
		return self._parent

	@property
	def root(self) -> Node | None:
		n = self.parent
		if n is None:
			return None
		while n.parent is not None:
			n = n.parent
		return n

	@property
	def parents(self) -> list[Node]:
		nodes = []
		n = self
		while n.parent is not None:
			n = n.parent
			nodes.append(n)
		return nodes

	@property
	def children(self) -> list[Node]:
		return self._children.copy()

	@property
	def children_len(self) -> int:
		return len(self._children)

	def add_child(self, child: Node, z_index: int | None = None, tag: int | None = None, name: str | None = None):
		assert isinstance(child, Node)
		if child.parent is not None:
			raise RuntimeError('Target already have a parent')
		if z_index is not None:
			child.z_index = z_index
		if tag is not None:
			child.tag = tag
		if name is not None:
			child.name = name
		i = binSearch(self._children, lambda c: -1 if c.z_index <= child.z_index else 1)
		child._parent = self
		self._children.insert(i, child)
		if self.loaded:
			child.dispatch(LoadEvent('load', child))

	def get_child_by_tag(self, tag: int, grandchild: bool = False) -> Node | None:
		assert isinstance(tag, int)
		for c in self._children:
			if c.tag == tag:
				return c
		if grandchild:
			for c in self._children:
				g = c.get_child_by_tag(tag, grandchild=True)
				if g:
					return g
		return None

	def get_child_by_name(self, name: str, grandchild: bool = False) -> Node | None:
		assert isinstance(name, str)
		for c in self._children:
			if c.name == name:
				return c
		if grandchild:
			for c in self._children:
				g = c.get_child_by_name(name, grandchild=True)
				if g:
					return g
		return None

	def reachable(self, pos: Vec2) -> bool:
		if not self.visible:
			return False
		pos = self.anchor.convert_pos(pos, self.size, reversed=True)
		return Vec2.ZERO <= pos and pos <= self.size

	def _get_reachable_nodes_by_pos(self, pos: Vec2) -> list[tuple[Node, Vec2]] | None:
		if not self.visible:
			return None
		for c in reversed(self._children):
			npos = pos - c.pos
			n = c._get_reachable_nodes_by_pos(npos)
			if n is not None:
				n.append((self, pos))
				return n
		return [(self, pos)] if self.reachable(pos) else None

	def __remove_child_by_index(self, i: int):
		child = self._children[i]
		child.dispatch(LoadEvent('unload', child))
		self._children.pop(i)
		child._parent = None

	def remove_child(self, child: Node):
		assert isinstance(child, Node)
		assert child.parent is self
		for i, c in enumerate(self._children):
			if c is child:
				self.__remove_child_by_index(i)
				return
		raise RuntimeError('Unreachable statement')

	def remove_child_by_tag(self, tag: int):
		assert isinstance(tag, int)
		for i, c in enumerate(self._children):
			if c.tag == tag:
				return self.__remove_child_by_index(i)
		raise RuntimeError('Tag not exists')

	def remove_child_by_name(self, name: str):
		assert isinstance(name, str)
		for i, c in enumerate(self._children):
			if c.name == name:
				return self.__remove_child_by_index(i)
		raise RuntimeError('Name not exists')

	def remove_all_children(self):
		while len(self._children) > 0:
			self.__remove_child_by_index(0)

	def remove_from_parent(self):
		assert self.parent is not None
		self.parent.remove_child(self)

	def push_cursor(self, cursor) -> pygame.Cursor:
		c = pygame.mouse.get_cursor()
		self._cursors.append(c)
		pygame.mouse.set_cursor(cursor)
		return c

	def pop_cursor(self) -> pygame.Cursor | None:
		if len(self._cursors) == 0:
			return None
		c = self._cursors.pop(-1)
		pygame.mouse.set_cursor(c)
		return c

	def on_draw(self, surface: Surface):
		pass

	def on_update(self, dt: float):
		pass

	@on('load')
	def __on_load(self, event: LoadEvent):
		self._loaded = True
		if self._schedule_upadate_interval is not None:
			print(self, 'loading')
			assert self.scheduler is not None
			self.scheduler.add_interval(self.on_update, self._schedule_upadate_interval)

	@on('unload')
	def __on_unload(self, event: LoadEvent):
		self._loaded = False
		if self._update_task is not None:
			self._update_task.cancel()
			self._update_task = None

	def foreach_child(self, callback: Callable[[Node], None], /, *, reverse: bool = False):
		if reverse:
			stk = [_Pack[bool, Node](True, self)]
			while len(stk) > 0:
				item = stk[-1]
				n = item.b
				if item.a and n.children_len > 0:
					item.a = False
					stk.extend(_Pack(True, c) for c in n.children)
				else:
					callback(n)
					stk.pop(-1)
		else:
			que = [self]
			while len(que) > 0:
				n = que.pop(0)
				callback(n)
				que.extend(n.children)

T1 = TypeVar('T1')
T2 = TypeVar('T2')

class _Pack(Generic[T1, T2]):
	def __init__(self, a: T1, b: T2):
		self.a = a
		self.b = b
