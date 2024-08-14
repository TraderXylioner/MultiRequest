import asyncio
import time


class RateLimitManager:
    def __init__(self, services, proxies):
        self.services = services
        self.proxies = proxies
        self.rate_limits = {}
        self.time_update = time.time()

    def create_manager(self):
        for _service in self.services:
            self.rate_limits.setdefault(_service.name, {}).update({proxy: _service.rate_limit for proxy in self.proxies})
        self.time_update = time.time()

    async def start(self):
        self.create_manager()
        while True:
            if time.time() >= self.time_update + 1:
                self.create_manager()
            await asyncio.sleep(0)
