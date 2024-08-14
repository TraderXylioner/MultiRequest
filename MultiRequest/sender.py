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
                 ):
        self.tasks = tasks or []
        self.services = services or []
        self.proxies = proxies or []
        if use_localhost_ip:
            self.proxies.append('localhost')
        self.rate_limit_manager = RateLimitManager(self.services, self.proxies)
        self.requester = Requester

    def _check_params(self):
        if not self.tasks:
            raise Exception('tasks not set')
        elif not self.services:
            raise Exception('services not set')
        elif not self.proxies:
            raise Exception('proxies not set')

    async def multi_task_run(self) -> Task:
        self._check_params()
        rate_limit_manager_task = asyncio.create_task(self.rate_limit_manager.start())

        try:
            tasks = [self._process_task(task, yield_request=False) for task in self.tasks]
            worker_tasks = {asyncio.create_task(task.__anext__()): task for task in tasks}
            for worker_task in worker_tasks:
                done, _ = await asyncio.wait([worker_task])
                _, task = next(iter(done)).result()
                yield task
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
        _requests = [
            asyncio.create_task(self.requester.processing_request(_request, self.rate_limit_manager.rate_limits)) for
            _request in task.requests]
        for _request in _requests:
            await _request
            if yield_request:
                yield _request.result(), task
        if not yield_request:
            yield None, task
