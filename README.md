# MultiRequest

MultiRequest is the library for sending asynchronous requests simultaneously, taking into account the rate limit.

## Functionality

- __Support for multiple services__ (send requests for several services)
- __Proxy__ (use proxy for acceleration of data collect)

## quickstart

### create service

``` python
from MultiRequest.types import service

service = Service(name='jsonplaceholder', rate_limit=10)
```

### create proxy

using proxy is not mandatory, if you dont set proxy the library will send requests from localhost

``` python
from MultiRequest.types import Proxy

proxy = Proxy(protocol='HTTPS', ip='0.0.0.0', port=80, user='user', password='password')
```

### create request

``` python
from MultiRequest.types import Request

request=Request(url=f'https://jsonplaceholder.typicode.com/todos/1', service=service)
```

### create task

task is an abstract object that receiving a list of requests

``` python
from MultiRequest.types import Task

tasks = Task(requests=[request])
```

### run sender

``` python
import asyncio

from MultiRequest import Sender


async def run():
        async for request in sender.run():
        print(request.data)  # -> b'{\n  "userId": 1,\n  "id": 1,\n  "title": "delectus aut autem",\n  "completed": false\n}'


if __name__ == '__main__':
    sender = Sender(tasks=[task], services=[service])
    asyncio.run(run())
```

### run multi task sender

``` python
import asyncio

from MultiRequest import Sender


async def run():
        async for task in sender.multi_task_run():
        print(type(task))  # -> <class 'MultiRequest.types.task.Task'>


if __name__ == '__main__':
    sender = Sender(tasks=[task] * 10, services=[service])
    asyncio.run(run())
```

### How it works

for example, we want to collect data from service [JSONPlaceHolder] allows to send 10 requests in second, we want to
collect 200 pages.

``` python
import asyncio
import time

from MultiRequest import Sender
from MultiRequest.types import Task, Service, Request


async def run():
    async for request in sender.run():
        print(request.data)


if __name__ == '__main__':
    service = Service(name='jsonplaceholder', rate_limit=10)
    task = Task(requests=[Request(url=f'https://jsonplaceholder.typicode.com/todos/{i}', service=service) for i in range(1, 201)])
    sender = Sender(tasks=[task], services=[service])
    time_start = time.time()
    asyncio.run(run())
    print(time.time() - time_start)

```

this code sent 200 request (10 seconds per second) in 20 seconds and printed data as soon received the answer.
library sent request while rate limit > 0, if rate limit = 0 library reached the limit there is a wait until the rate
limit is updated (every second).

[JSONPlaceHolder]: <https://jsonplaceholder.typicode.com/todos>