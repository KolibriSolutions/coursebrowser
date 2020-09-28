from aiohttp import ClientSession, TCPConnector
import asyncio


def async_fetcher(urls, headers):
    async def fetch(url, session):
        async with session.get(url) as response:
            return await response.json()

    # async def bound_fetch(sem, url, session):
    #     # Getter function with semaphore.
    #     async with sem:
    #         await fetch(url, session)

    async def run(urls, headers):
        # create instance of Semaphore
        # sem = asyncio.Semaphore(1000)
        tasks = []
        # Create client session that will ensure we dont open new connection
        # per each request.
        async with ClientSession(headers=headers) as session:
            for url in urls:
                # pass Semaphore and session to every GET request
                task = asyncio.ensure_future(fetch(url, session))
                tasks.append(task)

            responses = await asyncio.gather(*tasks)
            await session.close()
            return responses

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    future = asyncio.ensure_future(run(urls, headers))
    results = loop.run_until_complete(future)
    loop.close()

    return results