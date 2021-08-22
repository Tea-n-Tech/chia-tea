import asyncio

import aiohttp

API_EXCEPTIONS = (
    # No config or error response
    ValueError,
    # No chia on machine
    RuntimeError,
    # Not running
    aiohttp.ClientConnectorError,
    asyncio.TimeoutError,
)
