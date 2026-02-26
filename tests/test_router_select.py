import unittest

from types import SimpleNamespace
from unittest.mock import AsyncMock

from custom_components.yamaha_dsp import RouterConfiguration, RouterSourceConfiguration
from custom_components.yamaha_dsp.select import RouterSelectEntity


class RouterSelectEntityTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.config = RouterConfiguration(
            name="Classroom sink",
            index_source=20019,
            sources=[
                RouterSourceConfiguration(label="NONE", value=0),
                RouterSourceConfiguration(label="Mic bus", value=3),
                RouterSourceConfiguration(label="YDIF IN 1", value=17),
            ],
        )
        self.device = AsyncMock()
        self.entity = RouterSelectEntity(self.config, self.device, SimpleNamespace())

    async def test_async_update_reads_selected_option(self):
        self.device.query_parameter_raw.return_value = SimpleNamespace(get_int_value=lambda: 17)

        await self.entity.async_update()

        self.device.query_parameter_raw.assert_awaited_once_with("MTX:Index_20019")
        self.assertEqual("YDIF IN 1", self.entity.current_option)

    async def test_async_select_option_sets_parameter(self):
        await self.entity.async_select_option("Mic bus")

        self.device.set_parameter_raw.assert_awaited_once_with("MTX:Index_20019", "0", "0", "3")

    async def test_async_select_option_rejects_invalid_value(self):
        with self.assertRaises(ValueError):
            await self.entity.async_select_option("Invalid option")


if __name__ == "__main__":
    unittest.main()
