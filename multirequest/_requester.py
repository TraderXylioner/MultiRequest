import asyncio

import aiohttp
from aiohttp import ClientResponse

from ._utils import _dispatch_request
from .types import Request, Proxy, Service
from .types.request import Response


class Requester:
    def __init__(self, is_raise_error: bool, attempts: int, timeout: int | None):
        self.is_raise_error = is_raise_error
        self.attempts = attempts
        self.timeout = timeout

    async def processing_request(self, request: Request, rate_limits: dict) -> Request:
        try:
            service = rate_limits[request.service.name]
            data, response_object = await self.send_request(request, service)
            request.response = Response(data=data, object=response_object)
            return request
        except Exception as ex:
            if self.is_raise_error:
                raise RuntimeError(f'Request error: {ex}\n{request}')

    async def get_proxy(self, service: Service) -> Proxy:
        while True:
            proxy = service['proxies'][service['target']]
            if proxy[1] > 0:
                proxy[1] -= 1
                service['target'] = 0 if service['target'] == len(service['proxies']) - 1 else service['target'] + 1
                return proxy
            await asyncio.sleep(0)

    async def send_request(self, request: Request, service: Service) -> tuple[bytes, ClientResponse]:
        _local_attempts = self.attempts
        while _local_attempts:
            _local_attempts -= 1
            proxy = await self.get_proxy(service)
            _proxy = None if proxy == 'localhost' else proxy.to_string()
            async with aiohttp.ClientSession(trust_env=True, headers=request.headers) as session:
                async with _dispatch_request(session, request.method.value)(**request.get_request_params(),
                                                                            ssl=True, proxy=_proxy,
                                                                            timeout=self.timeout) as response:
                    return await response.content.read(), response
