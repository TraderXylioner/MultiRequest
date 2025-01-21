import asyncio

import aiohttp

from ._utils import _dispatch_request
from .types import Request, Proxy
from .types.request import Response


class Requester:
    def __init__(self, is_raise_error: bool):
        self.is_raise_error = is_raise_error

    async def processing_request(self, request: Request, rate_limits: dict) -> Request:
        service = rate_limits[request.service.name]
        while True:
            for proxy in service['proxies']:
                if service['proxies'][proxy] > 0:
                    service['proxies'][proxy] -= 1
                    data, response_object = await self.send_request(request, proxy)
                    request.response = Response(data=data, object=response_object)
                    return request

                await asyncio.sleep(0)

    async def send_request(self, request: Request, proxy: Proxy, attempts: int = 10) -> bytes:
        while attempts:
            try:
                attempts -= 1
                _proxy = None if proxy == 'localhost' else proxy.to_string()
                async with aiohttp.ClientSession(trust_env=True, headers=request.headers) as session:
                    async with _dispatch_request(session, request.method.value)(**request.get_request_params(),
                                                                                ssl=True, proxy=_proxy) as response:
                        return await response.content.read(), response
            except Exception as ex:
                if self.is_raise_error:
                    raise ex