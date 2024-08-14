import asyncio

import aiohttp

from ._utils import _dispatch_request
from .types import Request, Proxy


class Requester:
    @classmethod
    async def processing_request(cls, request: Request, rate_limits: dict) -> Request:
        service = rate_limits[request.service.name]
        while True:
            for proxy in service:
                if service[proxy] > 0:
                    service[proxy] -= 1
                    request.data, request.response_object = await cls.send_request(request, proxy)
                    return request
                await asyncio.sleep(0)

    @classmethod
    async def send_request(cls, request: Request, proxy: Proxy, attempts: int = 10) -> bytes:
        while attempts:
            try:
                attempts -= 1
                _proxy = None if proxy == 'localhost' else proxy.to_string()
                async with aiohttp.ClientSession(trust_env=True, headers=request.headers) as session:
                    async with _dispatch_request(session, request.method.value)(**request.get_request_params(),
                                                                                ssl=True, proxy=_proxy) as response:
                        return await response.content.read(), response
            except Exception as ex:
                raise ex
