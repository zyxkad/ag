# Copyright (C) 2023 zyxkad@gmail.com

from .resources import *
from .camera import *
from .nodes import *
from .event import *
from .scheduler import *

import sys
import pygame

__all__ = [
	'Director'
]

class _FPSTask: pass

class Director:
	INSTANCE = None

	def __new__(cls, *args, **kwargs):
		if cls.INSTANCE is None:
			cls.INSTANCE = super().__new__(cls)
			cls.__init(cls.INSTANCE, *args, **kwargs)
		return cls.INSTANCE

	@classmethod
	def __init(cls, self, exit_when_quit: bool = True, destroy_when_quit: bool = True):
		self._inited = False
		self._scheduler = Scheduler()
		self._fps = 30.0
		self.__frames_sec = 0
		self.__counted_f = 0
		self.__real_fps = 0.0
		self._scenes = []
		self._clear_color = Colors.white
		self._camera = Camera(0, 0)
		self._keymap = {}
		if exit_when_quit:
			Events.QUIT.register(self.__exit, priority=LOWEST_PRIORITY)
		elif destroy_when_quit:
			Events.QUIT.register(self.destroy, priority=LOWEST_PRIORITY)

	def __exit(self):
		self.destroy()
		sys.exit(0)

	@property
	def inited(self) -> bool:
		return self._inited

	@property
	def scheduler(self):
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

	def init_with_window(self, size: Vec2, title: str = None):
		self.init()
		self.winsize = size
		if title is not None:
			self.title = title

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
	def winsize(self, size: Vec2 | tuple[float, float]):
		pygame.display.set_mode(tuple(size))

	@property
	def title(self) -> str:
		captions = pygame.display.get_caption()
		if len(captions) == 0:
			return None
		return captions[0]

	@title.setter
	def title(self, title: str) -> str:
		pygame.display.set_caption(title)

	@property
	def clear_color(self) -> Color:
		return self._clear_color

	@clear_color.setter
	def clear_color(self, color: Color | tuple):
		if not isinstance(color, Color):
			color = Color(color)
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

	def update(self, dt: float):
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				Events.QUIT.emit()
			elif event.type == pygame.KEYUP:
				self._keymap[event.dict['key']] = False
				Events.KEYUP.emit(event.dict)
			elif event.type == pygame.KEYDOWN:
				self._keymap[event.dict['key']] = True
				Events.KEYDOWN.emit(event.dict)
			elif event.type == pygame.MOUSEMOTION:
				Events.MOUSEMOVE.emit(event.dict)
			elif event.type == pygame.MOUSEBUTTONUP:
				Events.MOUSEUP.emit(event.dict)
			elif event.type == pygame.MOUSEBUTTONDOWN:
				Events.MOUSEDOWN.emit(event.dict)
			else:
				Events.EVENT.emit(event)

	def draw_scene(self, dt: float):
		self.__frames_sec += dt
		self.__counted_f += 1
		if self.__counted_f >= self.fps:
			self.__real_fps = self.__counted_f / self.__frames_sec
			self.__frames_sec = 0
			self.__counted_f = 0

		osurface = pygame.display.get_surface()
		surface = CameraSurface(self._camera, osurface)
		surface.fill(self.clear_color)

		uis = []
		lys = []
		for c in self.current_scene.children:
			if isinstance(c, UILayer):
				uis.append(c)
			else:
				lys.append(c)
		que = list(sorted(uis, key=lambda n: n.z_index, reverse=True))
		que.extend(sorted(lys, key=lambda n: n.z_index, reverse=True))
		que.append(self.current_scene)
		while len(que) > 0:
			n = que.pop(-1)
			que.extend(sorted(n.children, key=lambda n: n.z_index, reverse=True))
			if isinstance(n, (Scene, UILayer)):
				n.on_draw(surface.get_origin())
			else:
				if n.width == 0 and n.height == 0:
					n.on_draw(surface)
				else:
					s = Surface((n.width, n.height))
					n.on_draw(s)
					surface.blit(s, Vec2(n.x, n.y))
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
		foreach_call(scene, lambda n: n.on_enter())
		scene.scheduler = self.scheduler
		self._scenes.append(scene)
		foreach_call(scene, lambda n: n.on_entered())
		self._loop()

	def push_scene(self, scene: Scene):
		assert len(self._scenes) > 0, 'Cannot use `push_scene` to start main loop'
		foreach_call(scene, lambda n: n.on_enter())
		scene.scheduler = self.scheduler
		self._scenes.append(scene)
		foreach_call(scene, lambda n: n.on_entered())

	def pop_scene(self):
		assert len(self._scenes) > 0, 'Main loop not running'
		s = self._scenes[-1]
		foreach_call(s, lambda n: n.on_exit())
		self._scenes.pop(-1)
		foreach_call(s, lambda n: n.on_exited())
		if len(self._scenes) == 0:
			self._end()

	def pop_scene_to(self, level: int = 1):
		assert len(self._scenes) > 0, 'Main loop not running'
		assert level >= 0
		while len(self._scenes) > level:
			s = self._scenes[-1]
			foreach_call(s, lambda n: n.on_exit())
			self._scenes = self._scenes[:-1]
			foreach_call(s, lambda n: n.on_exited())
		if len(self._scenes) == 0:
			self._end()

	def replace_scene(self, scene: Scene):
		assert len(self._scenes) > 0, 'Main loop not running'
		s = self._scenes[-1]
		foreach_call(s, lambda n: n.on_exit())
		self._scenes.pop(-1)
		foreach_call(s, lambda n: n.on_exited())
		foreach_call(scene, lambda n: n.on_enter())
		scene.scheduler = self.scheduler
		self._scenes[-1] = scene
		foreach_call(scene, lambda n: n.on_entered())

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
