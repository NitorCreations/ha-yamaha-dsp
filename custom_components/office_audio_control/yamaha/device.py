import asyncio
from dataclasses import dataclass

from custom_components.office_audio_control.yamaha.response import parse_response, Response, ErrorResponse, OkResponse, \
    NotifyResponse
from custom_components.office_audio_control.yamaha.telnet import TelnetDevice


@dataclass
class ProductInformation:
    protocol_version: str
    parameter_set_version: str
    firmware_version: str
    product_name: str
    serial_number: str
    device_id: str
    device_name: str


class ResponseError(Exception):
    pass


class YamahaDspDevice(TelnetDevice):
    def __init__(self, host: str, port: int, timeout: int = 5):
        super().__init__(host, port)
        self._timeout = timeout
        self._response_listener_task: asyncio.Task | None = None
        self._last_command_response = None
        self._command_response_received = asyncio.Event()

    async def after_connect(self):
        # Start the response listener
        self._response_listener_task = asyncio.create_task(self._response_listener())

        # A handshake must be performed before the device will accept commands
        await self._perform_handshake()

    async def before_disconnect(self):
        # Cancel the response listener task
        self._response_listener_task.cancel()
        await self._response_listener_task

    async def _response_listener(self):
        while True:
            raw_resp = await self._read_until("\n")

            # Exit the loop if we read nothing, the other layers will
            # handle the underlying error
            if raw_resp is None:
                return

            resp = parse_response(raw_resp)

            if isinstance(resp, NotifyResponse):
                await self._handle_notify_response(resp)
            else:
                self._last_command_response = resp
                self._command_response_received.set()

    @staticmethod
    async def _handle_notify_response(response: NotifyResponse):
        print(f"Got NOTIFY response: ", response.__dict__)

    async def _send_command(self, command):
        self._writer.write(f"{command}\n".encode())
        await self._writer.drain()

    async def _wait_for_response(self):
        await self._command_response_received.wait()

    async def _run_command(self, command: str) -> OkResponse | None:
        try:
            # Send the command
            await asyncio.wait_for(self._send_command(command), self._timeout)

            # Wait for the response
            await asyncio.wait_for(self._wait_for_response(), self._timeout)
            resp = self._last_command_response
            self._command_response_received.clear()

            if isinstance(resp, OkResponse):
                return resp
            else:
                raise ResponseError(resp)
        except TimeoutError:
            raise RuntimeError("Command timed out")
        except (ConnectionResetError, BrokenPipeError):
            await self.disconnect()
            raise RuntimeError("Connection was reset")
        finally:
            if not self._connected:
                print("Connection seems to be broken, will attempt to reconnect")
                await self.reconnect()

    async def _perform_handshake(self):
        await self._run_command("devstatus runmode")

    async def query_product_information(self) -> ProductInformation:
        protocol_ver_resp = await self._run_command("devinfo protocolver")
        parameter_set_resp = await self._run_command("devinfo paramsetver")
        firmware_version_resp = await self._run_command("devinfo version")
        product_name_resp = await self._run_command("devinfo productname")
        serial_number_query = await self._run_command("devinfo serialno")
        device_id_query = await self._run_command("devinfo deviceid")
        device_name_query = await self._run_command("devinfo devicename")

        return ProductInformation(
            protocol_ver_resp.value,
            parameter_set_resp.value,
            firmware_version_resp.value,
            product_name_resp.value,
            serial_number_query.value,
            device_id_query.value,
            device_name_query.value
        )
