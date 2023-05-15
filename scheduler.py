# Copyright (C) 2023 zyxkad@gmail.com

import time
from threading import RLock, Thread
from typing import TypeVar
from .utils import *

__all__ = [
	'StopSchedule',
	'Task', 'IntervalTask',
	'Scheduler'
]

class StopSchedule(BaseException):
	pass

SchedulerSelf = TypeVar('SchedulerSelf', bound='Scheduler')

class Task:
	def __init__(self, when: float, cb):
		assert isinstance(when, (int, float))
		assert callable(cb)
		assert when >= 0
		self._when = when
		self._cb = cb

	@property
	def when(self) -> float:
		return self._when

	@property
	def callback(self) -> float:
		return self._cb

	def _call(self, scheduler: SchedulerSelf):
		self._cb()

	def __eq__(self, other):
		return self.when == other.when

	def __lt__(self, other):
		return self.when < other.when

	def __gt__(self, other):
		return self.when > other.when

class IntervalTask(Task):
	def __init__(self, start: float, interval: float, cb):
		super().__init__(start, cb)
		assert isinstance(interval, (int, float))
		assert interval >= 0
		self._last = -1
		self._interval = interval

	@property
	def last(self) -> float:
		return self._last

	@property
	def interval(self) -> float:
		return self._interval

	def _call(self, scheduler: SchedulerSelf):
		now = scheduler.time
		dt = now - self._last if self._last >= 0 else 0
		self._last = now
		try:
			self._cb(dt)
		except StopSchedule:
			pass
		else:
			self._when = now + self.interval
			scheduler.put_task(self)

_sleep_offset = 0.0
def _test_sleep_offset():
	global _sleep_offset
	x = 0
	n = 0
	s = 1
	while True:
		if n < 10:
			s = 0.1
		else:
			s = 1
		a = time.time()
		time.sleep(s)
		b = time.time() - a
		if n > 1000000:
			x = b
			n = s
		else:
			x += b
			n += s
			_sleep_offset = 0.1 - x / n
Thread(target=_test_sleep_offset, daemon=True, name='test_sleep_offset').start()

class Scheduler:
	def __init__(self):
		self._time = 0
		self._lock = RLock()
		self._jobs = []
		self._paused = False
		self._timescale = 1

		self._looping = False

	@property
	def time(self) -> float:
		return self._time

	@property
	def paused(self) -> bool:
		return self._paused

	@property
	def timescale(self) -> float:
		return self._timescale

	@timescale.setter
	def timescale(self, timescale: float):
		self._timescale = timescale

	def put_task(self, task: Task):
		assert isinstance(task, Task)
		with self._lock:
			i = binSearch(self._jobs, lambda t: compare(t.when, task.when))
			self._jobs.insert(i, task)
		return task

	def add_interval(self, cb, interval: float):
		assert callable(cb)
		assert isinstance(interval, (int, float))
		task = IntervalTask(self._time + interval, interval, cb)
		return self.put_task(task)

	def add_timeout(self, cb, timeout: float):
		assert callable(cb)
		assert isinstance(timeout, (int, float))
		task = Task(self._time + timeout, cb)
		return self.put_task(task)

	def unschedule(self, task: Task):
		assert isinstance(task, Task)
		with self._lock:
			self._jobs.remove(task)

	def clear(self):
		with self._lock:
			self._jobs.clear()

	def update(self, dt: float, *, check_looping: bool = False):
		if self._paused:
			return

		self._time += dt * self.timescale
		with self._lock:
			for t in self._jobs.copy():
				if check_looping and not self._looping:
					return
				if t.when > self._time:
					break
				self._jobs.pop(0)
				t._call(self)

	def run(self):
		self._paused = False

	def pause(self):
		self._paused = True

	@property
	def looping(self) -> bool:
		return self._looping

	def stop(self):
		self._looping = False

	def loopUntilEmpty(self):
		self._looping = True
		last = time.time()
		while self._looping and len(self._jobs) > 0:
			t = self._jobs[0]
			st = (t.when - self._time) / self.timescale + last - time.time() + _sleep_offset
			if st > 0:
				time.sleep(st)
			now = time.time()
			self.update(now - last, check_looping=True)
			last = now

