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
            proxy = service['proxies'][service['target']]
            if proxy[1] > 0:
                proxy[1] -= 1
                service['target'] = 0 if service['target'] == len(service['proxies']) - 1 else service['target'] + 1
                data, response_object = await self.send_request(request, proxy[0])
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
                    raise f'Request error: {ex}\n{request} | {proxy}'
