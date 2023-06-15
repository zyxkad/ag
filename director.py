# Copyright (C) 2023 zyxkad@gmail.com

import enum
import sys
import time

from .resources import Color, Colors, Vec2, Surface, Anchor
from .camera import Camera, CameraSurface
from .nodes import Node, Scene, UILayer
from .event import (Event, EventTarget, LOWEST_PRIORITY,
	QuitEvent, UIEvent, LoadEvent,
	KeyboardEvent, MouseMoveEvent, MouseClickEvent, MouseOverEvent,
	MOUSE_MAIN_BUTTON)
from .scheduler import Scheduler, IntervalTask

import pygame

__all__ = [
	'QuitBehavior',
	'Director'
]


class QuitBehavior(enum.Enum):
	EXIT_WHEN_QUIT = enum.auto()
	DESTROY_WHEN_QUIT = enum.auto()
	CUSTOM_WHEN_QUIT = enum.auto()

class Director(EventTarget):
	INSTANCE = None
	_double_click_interval = 0.4

	def __new__(cls, *args, **kwargs):
		if cls.INSTANCE is None:
			cls.INSTANCE = super().__new__(cls)
			cls.__init(cls.INSTANCE, *args, **kwargs)
		return cls.INSTANCE

	def __init__(self, *args, **kwargs):
		pass

	_inited: bool
	_scheduler: Scheduler | None
	_fps: float
	__frames_sec: float
	__counted_f: int
	__real_fps: float
	_scenes: list[Scene]
	_clear_color: Color
	_camera: Camera
	_keymap: dict[int, bool]
	_mouseflags: int
	__last_click: float | None
	__dbclick: bool
	_mousemoving: Node | None
	_focused: Node | None

	@classmethod
	def __init(cls, self, quit_behavior: QuitBehavior = QuitBehavior.EXIT_WHEN_QUIT):
		super().__init__(self)
		self._inited = False
		self._scheduler = None
		self._fps = 30.0
		self.__frames_sec = 0
		self.__counted_f = 0
		self.__real_fps = 0.0
		self._scenes = []
		self._clear_color = Colors.white
		self._camera = Camera(0, 0)
		self._keymap = {}
		self._mouseflags = 0
		self.__last_click = None
		self.__dbclick = False
		self._mousemoving = None
		self._focused = None

		if quit_behavior is QuitBehavior.EXIT_WHEN_QUIT:
			self.register('quit', lambda e: self.__exit(), priority=LOWEST_PRIORITY)
		elif quit_behavior is QuitBehavior.DESTROY_WHEN_QUIT:
			self.register('quit', lambda e: self.destroy(), priority=LOWEST_PRIORITY)

	def __exit(self):
		self.destroy()
		sys.exit(0)

	@property
	def inited(self) -> bool:
		return self._inited

	@property
	def scheduler(self) -> Scheduler:
		assert self._scheduler is not None
		return self._scheduler

	def _end(self):
		self.scheduler.stop()

	def _loop(self):
		self.scheduler.loopUntilEmpty()

	def init(self):
		assert not self._inited
		self._inited = True
		self._scheduler = Scheduler()
		self.__frames_sec = 0
		self.__counted_f = 0
		self.__real_fps = 0.0
		pygame.init()

	def init_with_window(self, size: Vec2 | tuple[float, float], title: str | None = None, *,
		fps: float = 30.0):
		self.init()
		if not isinstance(size, Vec2):
			size = Vec2(size)
		self.winsize = size
		if title is not None:
			self.title = title
		self.fps = fps

	def destroy(self):
		if self._inited:
			self._end()
			self._inited = False
			self.pop_scene_to(0)
			pygame.quit()
			self._scheduler = None

	@property
	def fps(self) -> float:
		return self._fps

	@fps.setter
	def fps(self, fps: float):
		if fps == self._fps:
			return
		self._fps = fps
		if self.__frames_sec > 0:
			self.__real_fps = self.__counted_f / self.__frames_sec
			self.__frames_sec = 0
			self.__counted_f = 0

	@property
	def spf(self) -> float:
		return 1 / self.fps

	@spf.setter
	def spf(self, spf: float):
		self.fps = 1 / spf

	@property
	def real_fps(self) -> float:
		return self.__real_fps

	@property
	def winsize(self) -> Vec2:
		return Vec2(pygame.display.get_window_size())

	@winsize.setter
	def winsize(self, size: Vec2):
		pygame.display.set_mode(size.xy)

	@property
	def title(self) -> str:
		captions = pygame.display.get_caption()
		if len(captions) == 0:
			return ''
		return captions[0]

	@title.setter
	def title(self, title: str):
		pygame.display.set_caption(title)

	@property
	def clear_color(self) -> Color:
		return self._clear_color

	@clear_color.setter
	def clear_color(self, color: Color | tuple[int, int, int]):
		if not isinstance(color, Color):
			color = Color(*color)
		self._clear_color = color

	@property
	def camera(self) -> Camera:
		return self._camera

	@camera.setter
	def camera(self, camera: Camera):
		self._camera = camera

	@property
	def keymap(self) -> dict[int, bool]:
		return self._keymap

	def is_keydown(self, key: int) -> bool:
		return self._keymap.get(key, False)

	def __get_ctrl_keys(self) -> dict:
		return {
			'alt': self.is_keydown(pygame.K_LALT) or self.is_keydown(pygame.K_RALT),
			'ctrl': self.is_keydown(pygame.K_LCTRL) or self.is_keydown(pygame.K_RCTRL),
			'meta': self.is_keydown(pygame.K_LMETA) or self.is_keydown(pygame.K_RMETA),
			'shift': self.is_keydown(pygame.K_LSHIFT) or self.is_keydown(pygame.K_RSHIFT),
			'buttons': self.mouseflags,
		}

	@property
	def mouseflags(self) -> int:
		return self._mouseflags

	def is_mousedown(self, btn: int) -> bool:
		return bool(self.mouseflags & (1 << btn))

	def _get_reachable_node_at(self, x: int, y: int) -> list[tuple[Node, Vec2]]:
		assert self.current_scene is not None, 'Main loop is not running'
		pos = Vec2(x, y)
		cpos = Vec2(self.camera.x - self.winsize.x // 2, self.camera.y - self.winsize.y // 2)
		nodes = self.current_scene._get_reachable_ui_by_pos(pos) or \
			self.current_scene._get_reachable_nodes_by_pos(cpos)
		return [(self.current_scene, pos)] if nodes is None else nodes

	def __on_mouse_move(self, dx: int, dy: int, x: int, y: int) -> bool:
		targets = self._get_reachable_node_at(x, y)
		target = targets[0][0]
		kwargs = self.__get_ctrl_keys()
		e = MouseMoveEvent(target, dx=dx, dy=dy,
			x=x, y=y, viewX=x - self.camera.x, viewY=y - self.camera.y,
			screenX=x, screenY=y,
			**kwargs)
		if not self.dispatch(e, capture=True):
			return False
		for n, pos in reversed(targets):
			e._x, e._y = pos.xy
			if not EventTarget.dispatch(n, e, capture=True):
				return False
		for n, pos in targets:
			e._x, e._y = pos.xy
			if not EventTarget.dispatch(n, e, capture=False):
				return False
		if not self.dispatch(e, capture=False):
			return False
		old = self._mousemoving
		if old is not target:
			if old is not None:
				print('moveout:', old)
				old.dispatch(MouseOverEvent('mouseleave', old, target,
					**kwargs))
				old.dispatch(MouseOverEvent('mouseout', old, target, bubbles=True,
					**kwargs))
			self._mousemoving = target
			target.dispatch(MouseOverEvent('mouseenter', target, old,
				**kwargs))
			target.dispatch(MouseOverEvent('mouseover', target, old, bubbles=True,
				**kwargs))
		return True

	def __dispatch_click_event(self, etype: str, btn: int, x: int, y: int, targets: list[tuple[Node, Vec2]]) -> bool:
		target = targets[0][0]
		e = MouseClickEvent(etype, target, btn,
			x=x, y=y, viewX=x - self.camera.x, viewY=y - self.camera.y,
			screenX=x, screenY=y,
			**self.__get_ctrl_keys())
		if not self.dispatch(e, capture=True):
			return False
		for n, pos in reversed(targets):
			e._x, e._y = pos.xy
			if not EventTarget.dispatch(n, e, capture=True):
				return False
		for n, pos in targets:
			e._x, e._y = pos.xy
			if not EventTarget.dispatch(n, e, capture=False):
				return False
		return self.dispatch(e, capture=False)

	def __on_mouse_down(self, btn: int, x: int, y: int) -> None:
		self._mouseflags |= 1 << btn
		targets = self._get_reachable_node_at(x, y)
		target = targets[0][0]
		self.__dispatch_click_event('mousedown', btn, x, y, targets)
		if btn == MOUSE_MAIN_BUTTON:
			if self.__last_click is None:
				self.__last_click = time.time()
			else:
				if time.time() - self.__last_click <= self._double_click_interval:
					self.__dbclick = True
				self.__last_click = None
		old = self._focused
		if old is not target:
			if old is not None:
				old.dispatch(UIEvent('focusout', old))
				old._focusing = False
				self._focused = None
				old.dispatch(UIEvent('blur', old, bubbles=False))
			if target.selectable:
				target.dispatch(UIEvent('focusin', target))
				self._focused = target
				target._focusing = True
				target.dispatch(UIEvent('focus', target, bubbles=False))

	def __on_mouse_up(self, btn: int, x: int, y: int) -> None:
		self._mouseflags &= ~(1 << btn)
		targets = self._get_reachable_node_at(x, y)
		self.__dispatch_click_event('mouseup', btn, x, y, targets)
		self.__dispatch_click_event('click', btn, x, y, targets)
		if btn == MOUSE_MAIN_BUTTON and self.__dbclick:
			self.__dbclick = False
			self.__dispatch_click_event('dbclick', btn, x, y, targets)

	def __on_text_editing(self, text: str, start: int, length: int) -> None:
		return

	def __on_text_input(self, text: str) -> None:
		return

	def update(self, dt: float) -> None:
		e: Event
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				self.dispatch(QuitEvent())
			elif event.type == pygame.KEYDOWN:
				self._keymap[event.dict['key']] = True
				e = KeyboardEvent('keydown', self, event.dict['key'], **self.__get_ctrl_keys())
				self.dispatch(e)
			elif event.type == pygame.KEYUP:
				self._keymap[event.dict['key']] = False
				e = KeyboardEvent('keyup', self, event.dict['key'], **self.__get_ctrl_keys())
				self.dispatch(e)
			elif event.type == pygame.MOUSEMOTION:
				dx, dy = event.dict['rel']
				x, y = event.dict['pos']
				self.__on_mouse_move(dx, dy, x, y)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				x, y = event.dict['pos']
				btn = event.dict['button'] - 1
				assert btn >= 0
				self.__on_mouse_down(btn, x, y)
			elif event.type == pygame.MOUSEBUTTONUP:
				x, y = event.dict['pos']
				btn = event.dict['button'] - 1
				assert btn >= 0
				self.__on_mouse_up(btn, x, y)
			elif event.type == pygame.TEXTEDITING:
				self.__on_text_editing(event.dict['text'], event.dict['start'], event.dict['length'])
			elif event.type == pygame.TEXTINPUT:
				self.__on_text_input(event.dict['text'])
			elif event.type == pygame.ACTIVEEVENT:
				pass # { gain: int-bool, state: 1 for pointer; 2 for focus }
			elif event.type == pygame.WINDOWENTER:
				self.dispatch(MouseOverEvent('mouseenter', self, None, **self.__get_ctrl_keys()))
			elif event.type == pygame.WINDOWLEAVE:
				kwargs = self.__get_ctrl_keys()
				self.dispatch(MouseOverEvent('mouseleave', self, None, **kwargs))
				old_moving = self._mousemoving
				if old_moving is not None:
					old_moving.dispatch(MouseOverEvent('mouseleave', old_moving, None,
						**kwargs))
					old_moving.dispatch(MouseOverEvent('mouseout', old_moving, None, bubbles=True,
						**kwargs))
					self._mousemoving = None
			elif event.type == pygame.WINDOWFOCUSGAINED:
				self.dispatch(UIEvent('winfocusin', self))
			elif event.type == pygame.WINDOWFOCUSLOST:
				self.dispatch(UIEvent('winfocusout', self))
			else:
				print('[DBUG] unknown event:', event.type, event)

	def draw_scene(self, dt: float):
		assert self.current_scene is not None

		self.__frames_sec += dt
		self.__counted_f += 1
		if self.__counted_f >= self.fps:
			self.__real_fps = self.__counted_f / self.__frames_sec
			self.__frames_sec = 0
			self.__counted_f = 0

		osurface = pygame.display.get_surface()
		surface = CameraSurface(self.camera, osurface)
		surface.fill(self.clear_color)
		sorigin = Surface(osurface)

		if self.current_scene.visible:
			s = Surface(sorigin.size)
			self.current_scene.on_draw(s)
			sorigin.blit(s, (0, 0), anchor=Anchor.TOP_LEFT)
			uis: list[Node] = []
			lys: list[Node] = []
			for c in self.current_scene.children:
				if isinstance(c, UILayer):
					uis.append(c)
				else:
					lys.append(c)
			while len(lys) > 0:
				n = lys.pop(-1)
				if not n.visible:
					continue
				lys.extend(n.children)
				if n.width >= 0 and n.height >= 0:
					s = Surface((n.width, n.height))
					n.on_draw(s)
					surface.blit(s, n.pos, anchor=n.anchor)
			while len(uis) > 0:
				n = uis.pop(-1)
				if not n.visible:
					continue
				uis.extend(n.children)
				if isinstance(n, UILayer):
					s = Surface(sorigin.size)
					n.on_draw(s)
					sorigin.blit(s, (0, 0), anchor=Anchor.TOP_LEFT)
				elif n.width >= 0 and n.height >= 0:
					s = Surface((n.width, n.height))
					n.on_draw(s)
					sorigin.blit(s, n.pos, anchor=n.anchor)
		pygame.display.update()

	@property
	def scenes(self) -> list[Scene]:
		return self._scenes.copy()

	@property
	def current_scene(self) -> Scene | None:
		return None if len(self._scenes) == 0 else self._scenes[-1]

	def run_with_scene(self, scene: Scene):
		assert self._inited, 'Need to be inited'
		assert len(self._scenes) == 0, 'Main loop is started'
		self.scheduler.add_interval(self.update, 0.05)
		self.scheduler.put_task(_FPSTask(self.scheduler.time + self.spf, self.draw_scene, self))
		scene.scheduler = self.scheduler
		self._scenes.append(scene)
		scene.foreach_child(lambda n: n.dispatch(LoadEvent('load', n)))
		self._loop()

	def push_scene(self, scene: Scene):
		old = self.current_scene
		assert old is not None, 'Cannot use `push_scene` to start main loop'
		old.foreach_child(lambda n: n.dispatch(LoadEvent('unload', n)))
		scene.scheduler = self.scheduler
		self._scenes.append(scene)
		scene.foreach_child(lambda n: n.dispatch(LoadEvent('load', n)))

	def pop_scene(self):
		old = self.current_scene
		assert old is not None, 'Main loop is not running'
		old.foreach_child(lambda n: n.dispatch(LoadEvent('unload', n)))
		self._scenes.pop(-1)
		if len(self._scenes) == 0:
			self._end()

	def pop_scene_to(self, level: int = 1):
		assert self.current_scene is not None, 'Main loop is not running'
		assert level >= 0
		if len(self._scenes) > level:
			old = self._scenes[-1]
			old.foreach_child(lambda n: n.dispatch(LoadEvent('unload', n)))
			while len(self._scenes) > level:
				self._scenes = self._scenes[:-1]
		if len(self._scenes) == 0:
			self._end()

	def replace_scene(self, scene: Scene):
		assert self.current_scene is not None, 'Main loop is not running'
		old = self._scenes[-1]
		old.foreach_child(lambda n: n.dispatch(LoadEvent('unload', n)))
		self._scenes.pop(-1)
		scene.foreach_child(lambda n: n.dispatch(LoadEvent('load', n)))
		scene.scheduler = self.scheduler
		self._scenes[-1] = scene

class _FPSTask(IntervalTask):
	def __init__(self, start: float, cb, director: Director):
		super().__init__(start, director.spf, cb)
		self._director = director

	@property
	def director(self) -> Director:
		return self._director

	@property
	def interval(self) -> float:
		return self.director.spf
