# Copyright (C) 2023 zyxkad@gmail.com

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
	def __init__(self, *layers: list[Layer], **kwargs):
		super().__init__(**kwargs)
		self._active = False
		for l in layers:
			self.add_child(l)

	@property
	def is_active(self) -> bool:
		return self._active

	def on_entered(self):
		super().on_entered()
		self._active = True

	def on_exit(self):
		super().on_exit()
		self._active = False
