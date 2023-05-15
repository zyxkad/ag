# Copyright (C) 2023 zyxkad@gmail.com

from typing import Self

from ..event import *
from ..scheduler import *
from ..resources import *
from ..utils import *

__all__ = [
	'Node',
	'foreach_call',
]

class Node(EventEmitter):
	def __init__(self, parent: Self | None = None, *,
		tag: int | None = None, name: str | None = None,
		scheduler: Scheduler | None = None,
		x: float = 0, y: float = 0, width: float = 0, height: float = 0, 
		z_index: int = 0, scale: tuple[float, float] = (1, 1),
		visible: bool = True, rotation: float = 0):
		assert isinstance(parent, (Node, type(None)))
		self._parent = parent
		self._children = []
		self._tag = tag
		self._name = name

		self._scheduler = scheduler

		self._x = x
		self._y = y
		self._width = width
		self._height = height
		self._z_index = z_index
		self._scaleX = scale[0]
		self._scaleY = scale[1]
		self._visible = visible
		self._rotation = rotation
		self._event_cbs = {}

	@property
	def parent(self) -> Self | None:
		return self._parent

	@property
	def children(self) -> list:
		return self._children.copy()

	@property
	def children_len(self) -> int:
		return len(self._children)

	def add_child(self, child: Self, z_index: int | None = None, tag: int | None = None, name: str | None = None):
		assert isinstance(child, Node)
		if child.parent is not None:
			raise RuntimeError('Target already have a parent')
		if z_index is None:
			z_index = child.z_index
		else:
			child.z_index = z_index
		if tag is not None:
			child.tag = tag
		if name is not None:
			child.name = name
		i = binSearch(self._children, lambda c: -1 if c.z_index <= z_index else 1)
		child._parent = self
		self._children.insert(i, child)

	def get_child_by_tag(self, tag: int, grandchild: bool = False) -> Self:
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

	def get_child_by_name(self, name: str, grandchild: bool = False) -> Self:
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

	def _remove_child_by_index(self, i: int):
		c = self._children[i]
		foreach_call(c, lambda n: n.on_exit())
		self._children.pop(i)
		c._parent = None
		foreach_call(c, lambda n: n.on_exited())
		return True

	def remove_child(self, child: Self):
		assert isinstance(child, Node)
		assert child.parent is self
		for i, c in enumerate(self._children):
			if c is child:
				return self._remove_child_by_index(i)
		raise RuntimeError('Unreachable statement')

	def remove_child_by_tag(self, tag: int):
		assert isinstance(tag, int)
		for i, c in enumerate(self._children):
			if c.tag == tag:
				return self._remove_child_by_index(i)
		raise RuntimeError('Tag not exists')

	def remove_child_by_name(self, name: str):
		assert isinstance(name, str)
		for i, c in enumerate(self._children):
			if c.name == name:
				return self._remove_child_by_index(i)
		raise RuntimeError('Name not exists')

	def remove_all_children(self):
		for c in self._children:
			pass
		self._children.clear()

	def remove_from_parent(self):
		return self.parent.remove_child(self)

	@property
	def tag(self) -> int:
		return self._tag

	@tag.setter
	def tag(self, tag: int):
		self._tag = tag

	@property
	def name(self) -> str:
		return self._name

	@name.setter
	def name(self, name: str):
		self._name = name

	@property
	def scheduler(self) -> Scheduler:
		return self._scheduler or (None if self.parent is None else self.parent.scheduler)

	@scheduler.setter
	def scheduler(self, scheduler: Scheduler):
		self._scheduler = scheduler

	def schedule_update(self, interval: float = 0.05):
		self.scheduler.add_interval(self.on_update, interval)

	@property
	def x(self) -> float:
		return self._x

	@x.setter
	def x(self, x: float):
		assert isinstance(x, (int, float))
		self._x = x

	@property
	def y(self) -> float:
		return self._y

	@y.setter
	def y(self, y: float):
		assert isinstance(y, (int, float))
		self._y = y

	@property
	def pos(self) -> Vec2:
		return Vec2(self.x, self.y)

	@property
	def width(self) -> float:
		return self._width

	@width.setter
	def width(self, width: float):
		assert isinstance(width, (int, float))
		self._width = width

	@property
	def height(self) -> float:
		return self._height

	@height.setter
	def height(self, height: float):
		assert isinstance(height, (int, float))
		self._height = height

	@property
	def size(self) -> Vec2:
		return Vec2(self.width, self.height)

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

	def register_event(self, event, cb):
		ls = self._event_cbs.get(event, None)
		if ls is None:
			self._event_cbs[event] = [cb]
		else:
			ls.append(cb)

	def on_draw(self, surface: Surface):
		pass

	def on_update(self, dt: float):
		pass

	def on_enter(self):
		pass

	def on_entered(self):
		for e, l in self._event_cbs.items():
			for cb in l:
				e.register(cb)

	def on_exit(self):
		for e, l in self._event_cbs.items():
			for cb in l:
				e.unregister(cb)

	def on_exited(self):
		pass

def foreach_call(node: Node, callback, /, *, reverse: bool = False):
	assert isinstance(node, Node)
	assert callable(callback)
	if reverse:
		stk = [[True, node]]
		while len(stk) > 0:
			flag, n = stk[0]
			if flag and n.children_len > 0:
				stk.extend(n.children)
				stk[0][0] = False
			else:
				stk.pop(0)
				callback(n)
	else:
		que = [node]
		while len(que) > 0:
			n = que.pop(0)
			callback(n)
			que.extend(n.children)
