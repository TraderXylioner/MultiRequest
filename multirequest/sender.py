import asyncio

from ._requester import Requester
from .types import Task, Request, Proxy, Service
from ._rate_limit_manager import RateLimitManager


class Sender:
    def __init__(self,
                 tasks: list[Task] = None,
                 services: list[Service] = None,
                 proxies: list[Proxy] = None,
                 use_localhost_ip: bool = True,
                 is_raise_error: bool = True,
                 attempts: int = 10,
                 timeout: int | None = None,
                 ):
        self.tasks = tasks or []
        self.services = services or []
        self.proxies = proxies or []
        if use_localhost_ip:
            self.proxies.append('localhost')  # localhost proxy
        self.rate_limit_manager = RateLimitManager(self.services, self.proxies)
        self.is_raise_error = is_raise_error
        self.attempts = attempts
        self.timeout = timeout

    def _check_params(self):
        if not self.tasks:
            raise Exception('tasks not set')
        elif not self.services:
            raise Exception('services not set')
        elif not self.proxies:
            raise Exception('proxies not set')

    async def multi_task_run(self, workers: int = 0) -> Task:
        self._check_params()
        rate_limit_manager_task = asyncio.create_task(self.rate_limit_manager.start())

        try:
            tasks = [self._process_task(task, yield_request=False) for task in self.tasks]
            tasks_chunks = [tasks[i:i + workers] for i in range(0, len(tasks), workers)] if workers != 0 else [tasks]

            for tasks_chunk in tasks_chunks:
                worker_tasks = [(asyncio.create_task(task.__anext__()), task) for task in tasks_chunk]
                for worker_task in worker_tasks:
                    try:
                        done, _ = await asyncio.wait([worker_task[0]])
                        _, task = next(iter(done)).result()
                        yield task
                    except Exception as ex:
                        if self.is_raise_error:
                            raise RuntimeError(f'Worker task error: {ex}\n{worker_task}')

        finally:
            rate_limit_manager_task.cancel()

    async def run(self) -> Request:
        self._check_params()
        rate_limit_manager_task = asyncio.create_task(self.rate_limit_manager.start())

        try:
            for _task in self.tasks:
                async for _request, _ in self._process_task(_task):
                    yield _request
        finally:
            rate_limit_manager_task.cancel()

    async def _process_task(self, task: Task, yield_request=True) -> (Request | None, Task):
        try:
            _requests = [
                asyncio.create_task(Requester(self.is_raise_error, self.attempts, self.timeout).processing_request(_request, self.rate_limit_manager.rate_limits)) for
                _request in task.requests]
            for _request in _requests:
                await _request
                if yield_request:
                    yield _request.result(), task
            if not yield_request:
                yield None, task
        except Exception as ex:
            if self.is_raise_error:
                raise RuntimeError(f'Task error: {ex}\n{task}')
