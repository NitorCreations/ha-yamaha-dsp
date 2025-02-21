import asyncio


class TelnetDevice:
    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._semaphore = asyncio.Semaphore()
        self._connected = False

    async def _read_until(self, phrase: str) -> str | None:
        b = bytearray()

        while not self._reader.at_eof():
            byte = await self._reader.read(1)
            b += byte

            if b.endswith(phrase.encode()):
                return b.decode()

        return None

    async def connect(self):
        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        self._connected = True

        await self.after_connect()

    async def after_connect(self):
        pass

    async def before_disconnect(self):
        pass

    async def disconnect(self):
        await self.before_disconnect()

        self._connected = False

        # Ignore potential connection errors here, we're about to disconnect after all
        try:
            self._writer.close()
            await self._writer.wait_closed()
        except ConnectionError:
            pass

    async def reconnect(self):
        await self.disconnect()
        await self.connect()

    def is_connected(self) -> bool:
        return self._connected
