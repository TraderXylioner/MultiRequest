# MultiRequest

MultiRequest is a library designed for sending asynchronous requests concurrently, while respecting rate limits.

## Functionality

- __Support for Multiple Services:__ Allows sending requests to multiple services.
- __Proxy:__ Optional use of a proxy to accelerate data collection.

## Quickstart

### Create a Service

Define a service with a rate limit.

``` python
from MultiRequest.types import Service

service = Service(name='jsonplaceholder', rate_limit=10)
```

### Create proxy

Using a proxy is optional. If not set, requests will be sent from localhost.

``` python
from MultiRequest.types import Proxy

proxy = Proxy(protocol='HTTPS', ip='0.0.0.0', port=80, user='user', password='password')
```

### Create a Request

Define a request for a specific URL and service.

``` python
from MultiRequest.types import Request

request=Request(url=f'https://jsonplaceholder.typicode.com/todos/1', method='GET', service=service)
```

### Create task

A task consists of a list of requests.

``` python
from MultiRequest.types import Task

tasks = Task(requests=[request])
```

### Run sender

Send requests and handle responses.

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

### Run Multi-Task Sender

Send multiple tasks concurrently.

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

## How it works

### Base Sender

For example, we want to collect data from the JSONPlaceHolder service, which allows us to send up to 10 requests per
second. We aim to collect data from 200 pages.

Here's how you might achieve that:

Define the Rate Limit and Number of Requests:

- The JSONPlaceHolder service allows up to 10 requests per second.
- We need to send requests to retrieve data from 200 pages.

Setup the Task:

- Create a task to send 200 requests, one for each page.

Handle Rate Limiting:

- The library will manage the rate limiting by ensuring that no more than 10 requests are sent per second.
- If the rate limit is reached, the library will wait until it can send additional requests.

Print the Data:

- As soon as data is received, it will be printed.

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
    task = Task(requests=[Request(url=f'https://jsonplaceholder.typicode.com/todos/{i}', method='GET', service=service) for i in range(1, 201)])
    sender = Sender(tasks=[task], services=[service])
    time_start = time.time()
    asyncio.run(run())
    print(time.time() - time_start)

```

This code sends 200 requests (10 requests per second) in 20 seconds and prints the data as soon as it is received. The
library sends requests while the rate limit for the service is greater than 0. If the rate limit is reached (rate
limit = 0), the library waits until the rate limit is reset (every second) and then continues sending requests.

Here's a more detailed explanation:

- The code sends 200 requests at a rate of 10 requests per second.
- The requests are sent until the rate limit of 10 requests per second is reached.
- If the rate limit is reached, the library pauses and waits for the rate limit to reset.
- Once the rate limit is reset (every second), the library continues sending the remaining requests.
- The data from each request is return as soon as it is received.
- This ensures that the requests are sent efficiently while respecting the rate limits of the service.

### Multi task Sender

For example, we want to collect data from the [Binance] and [Mexc] services for several trading pairs. We set a rate
limit of 2 requests per second for Binance and 1 request per second for MEXC. In total, we will collect data for 10
different currency pairs.

``` python
import asyncio
import time

from MultiRequest import Sender
from MultiRequest.types import Task, Service, Request


async def run():
    async for task in sender.multi_task_run():
        print(task)


if __name__ == '__main__':
    symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'SOLUSDT', 'XRPUSDT', 'DOGEUSDT', 'TONUSDT', 'ADAUSDT', 'TRONUSDT',
               'AVAXUSDT']
    services = [Service(name='binance', rate_limit=2), Service(name='mexc', rate_limit=1)]

    tasks = [Task(requests=[Request(
        url=f'https://api.{service.name}.com/api/v3/ticker/24hr',
        method='GET',
        params={'symbol': symbol},
        service=service, name=service.name) for service in services]) for symbol in symbols]

    sender = Sender(tasks=tasks, services=services)

    time_start = time.time()
    asyncio.run(run())
    print(time.time() - time_start)
```

This code sends 20 requests (10 to each service), but at different speeds: 2 requests per second for Binance and
1 request per second for MEXC. Thus, every 10 seconds, 20 requests will be processed (10 from Binance and 10 from MEXC).
The data retrieval speed depends on the minimal rate limit.

The MultiRequest library sends requests while the rate limit > 0 for the service. If the rate limit = 0, the library
waits until the limit is updated (every second) and executes another task where the rate limit > 0.

This example demonstrates how to use MultiRequest to collect data from multiple services with different rate limits.

[JSONPlaceHolder]: <https://jsonplaceholder.typicode.com/todos>

[Binance]: <https://developers.binance.com/docs/binance-spot-api-docs/rest-api#24hr-ticker-price-change-statistics>

[Mexc]: <https://mexcdevelop.github.io/apidocs/spot_v3_en/#24hr-ticker-price-change-statistics>
