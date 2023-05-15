# Copyright (C) 2023 zyxkad@gmail.com

from .node import Node

__all__ = [
	'SpriteFrame',
	'Sprite',
]

class SpriteFrame:
	def __init__(self, textrue, keep: float = 0.1):
		self._textrue = textrue
		self._keep = keep

	@property
	def keep(self) -> float:
		return self._keep

class Sprite(Node):
	def __init__(self, parent: Node | None = None, **kwargs):
		super().__init__(parent, **kwargs)
		self._frames = []

	@property
	def frames(self) -> list[SpriteFrame]:
		return self._frames
