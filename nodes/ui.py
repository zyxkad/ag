# Copyright (C) 2023 zyxkad@gmail.com

from typing import Callable

from ..event import MOUSE_MAIN_BUTTON, on, MouseOverEvent, MouseClickEvent
from ..resources import Surface, Texture
from .node import Node
from .scene import UILayer

import pygame

__all__ = [
	'UINode',
	'Button',
]

class UINode(Node):
	pass

class Button(UINode):
	def __init__(self, callback: Callable[[], None] | None = None, *,
		disabled: bool = False,
		idle_texture: Texture | None = None,
		disable_texture: Texture | None = None,
		hover_texture: Texture | None = None,
		click_texture: Texture | None = None,
		**kwargs):
		super().__init__(**kwargs)
		self.__callback = callback
		self.__disabled = disabled
		self._idle_texture = idle_texture
		self._disable_texture = disable_texture
		self._hover_texture = hover_texture
		self._click_texture = click_texture
		self.__hovering = False
		self.__clicking = False

	@property
	def disabled(self) -> bool:
		return self.__disabled

	@disabled.setter
	def disabled(self, disabled: bool):
		self.__disabled = disabled

	@property
	def hovering(self) -> bool:
		return self.__hovering

	@property
	def clicking(self) -> bool:
		return self.__clicking

	@property
	def idle_texture(self) -> Texture | None:
		return self._idle_texture

	@idle_texture.setter
	def idle_texture(self, texture: Texture | None):
		self._idle_texture = texture

	@property
	def disable_texture(self) -> Texture | None:
		return self._disable_texture

	@disable_texture.setter
	def disable_texture(self, texture: Texture | None):
		self._disable_texture = texture

	@property
	def hover_texture(self) -> Texture | None:
		return self._hover_texture

	@hover_texture.setter
	def hover_texture(self, texture: Texture | None):
		self._hover_texture = texture

	@property
	def click_texture(self) -> Texture | None:
		return self._click_texture

	@click_texture.setter
	def click_texture(self, texture: Texture | None):
		self._click_texture = texture

	def get_texture(self) -> Texture | None:
		if self.disabled:
			return self.disable_texture or self.idle_texture
		if self.clicking:
			return self.click_texture or self.idle_texture
		if self.hovering:
			return self.hover_texture or self.idle_texture
		return self.idle_texture

	@on('mouseenter')
	def __on_mouse_enter(self, event: MouseOverEvent) -> None:
		self.__hovering = True
		if event.is_button_down(MOUSE_MAIN_BUTTON):
			self.__clicking = True
		self.push_cursor(pygame.SYSTEM_CURSOR_HAND)

	@on('unload')
	@on('mouseleave')
	def __on_mouse_leave(self) -> None:
		self.__hovering = False
		self.__clicking = False
		self.pop_cursor()

	@on('mousedown')
	def __on_mouse_down(self, event: MouseClickEvent) -> None:
		if not self.disabled and event.button == MOUSE_MAIN_BUTTON:
			self.__clicking = True

	@on('mouseup')
	def __on_mouse_up(self, event: MouseClickEvent) -> None:
		if self.__clicking and event.button == MOUSE_MAIN_BUTTON:
			self.__clicking = False
			self.on_click()

	def on_click(self) -> None:
		if self.__callback is not None:
			self.__callback()

	def on_draw(self, surface: Surface):
		texture = self.get_texture()
		if texture is not None:
			texture.draw_at(surface, size=self.size)
