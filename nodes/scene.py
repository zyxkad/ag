# Copyright (C) 2023 zyxkad@gmail.com

from ..event import on
from ..resources import Vec2
from .node import Node

__all__ = [
	'Layer',
	'UILayer',
	'Scene',
]

class Layer(Node):
	pass

class UILayer(Layer):
	pass

class Scene(Node):
	@property
	def is_active(self) -> bool:
		return self.loaded

	def _get_reachable_ui_by_pos(self, pos: Vec2) -> list[tuple[Node, Vec2]] | None:
		if self.visible:
			for c in reversed(self._children):
				if isinstance(c, UILayer):
					npos = pos - c.pos
					n = c._get_reachable_nodes_by_pos(npos)
					if n is not None:
						n.append((self, pos))
						return n
		return None

	def _get_reachable_nodes_by_pos(self, pos: Vec2) -> list[tuple[Node, Vec2]] | None:
		if self.visible:
			for c in reversed(self._children):
				if not isinstance(c, UILayer):
					npos = pos - c.pos
					n = c._get_reachable_nodes_by_pos(npos)
					if n is not None:
						n.append((self, pos))
						return n
		return None
