# MultiRequest

MultiRequest is the library for sending asynchronous requests simultaneously, taking into account the rate limit.

## functionality

- __Support for multiple services__ (send requests for several services)
- __Proxy__ (use proxy for acceleration of data collect)

## quickstart

### create service

``` python
from MultiRequest.types import service

service = Service(name='jsonplaceholder', rate_limit=100)
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
from MultiRequest import Sender


async def run():
        async for task in sender.multi_task_run():
        print(type(task))  # -> <class 'MultiRequest.types.task.Task'>


if __name__ == '__main__':
    sender = Sender(tasks=[task] * 10, services=[service])
    asyncio.run(run())
```