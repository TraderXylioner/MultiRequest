import asyncio
import time

import aiohttp

from .types import Task, Request, Proxy, Service


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
        self._worker = {}
        self._worker_time_update = time.time()

    async def multi_task_run(self) -> Task:
        _update_worker_task = asyncio.create_task(self._update_worker())
        for _task in self.tasks:
            async for _request in self._processing_task(_task):
                ...
            yield _task
        _update_worker_task.cancel()

    async def run(self) -> Request:
        _update_worker_task = asyncio.create_task(self._update_worker())
        for _task in self.tasks:
            async for _request in self._processing_task(_task):
                yield _request
        _update_worker_task.cancel()

    async def _processing_task(self, task: Task):
        if not self.proxies:
            raise Exception('proxies not set')  # TODO:
        _requests = [asyncio.create_task(self._processing_request(_request)) for _request in task.requests]
        for _request in _requests:
            await _request
            yield _request.result()

    def _create_worker(self):
        for _service in self.services:
            self._worker.setdefault(_service.name, {}).update({proxy: _service.rate_limit for proxy in self.proxies})
        self._worker_time_update = time.time()

    async def _update_worker(self):
        self._create_worker()
        while True:
            if time.time() >= self._worker_time_update + 1:
                self._create_worker()
            await asyncio.sleep(0)

    async def _processing_request(self, request: Request):
        while True:
            service = self._worker[request.service.name]
            for proxy in service:
                if service[proxy] > 0:
                    service[proxy] -= 1
                    request.data, request.response_object = await self._send_request(request, proxy)
                    return request
                await asyncio.sleep(0)

    @classmethod
    async def _send_request(cls, request: Request, proxy: Proxy, attempts: int = 10):
        while attempts:
            try:
                attempts -= 1
                _proxy = None if proxy == 'localhost' else proxy.to_string()
                async with aiohttp.ClientSession(trust_env=True) as session:
                    async with session.get(url=request.url, proxy=_proxy, ssl=True) as response:
                        return await response.content.read(), response
            except Exception as ex:
                raise ex  # TODO:
