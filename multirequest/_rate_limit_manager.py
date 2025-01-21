import asyncio
import time


class RateLimitManager:
    def __init__(self, services, proxies):
        self.services = services
        self.proxies = proxies
        self.rate_limits = {}

    def create_manager(self):
        for _service in self.services:
            self.rate_limits.setdefault(_service.name, {})['proxies'] = {proxy: _service.rate_limit for proxy in self.proxies}
            self.rate_limits[_service.name]['time_update'] = time.time()
            self.rate_limits[_service.name]['time'] = _service.time_to_update
            self.rate_limits[_service.name]['service_obj'] = _service

    def update_manager(self, service):
        self.rate_limits[service.name]['proxies'] = {proxy: service.rate_limit for proxy in self.proxies}
        self.rate_limits[service.name]['time_update'] = time.time()

    async def start(self):
        self.create_manager()
        while True:
            for i in self.rate_limits:
                if time.time() >= self.rate_limits[i]['time_update'] + self.rate_limits[i]['time']:
                    self.update_manager(self.rate_limits[i]['service_obj'])
            await asyncio.sleep(0)
