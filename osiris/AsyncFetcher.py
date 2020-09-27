from aiohttp import ClientSession, TCPConnector
import pypeln as pl


def async_fetcher(urls, headers, conn=None):
    async def fetch(url, session):
        async with session.get(url) as response:
            return await response.json()
    #print(f'started fetcher with {len(urls)} urls')
    results = list(pl.task.map(
        fetch,
        urls,
        workers=1000,
        on_start=lambda: dict(session=ClientSession(connector=TCPConnector(limit=None),
                                                    headers=headers)),
        on_done=lambda session: session.close(),
        # run=True,
    ))
    #print('done fetching')

    if conn is not None:
        conn.send(results)
        conn.close()
    else:
        return results
