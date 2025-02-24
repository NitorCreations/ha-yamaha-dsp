import unittest

from custom_components.yamaha_dsp import EntityType, create_unique_id


class UtilsTests(unittest.TestCase):
    def test_create_unique_id(self):
        self.assertEqual("kitchen_speaker", create_unique_id("Kitchen", EntityType.SPEAKER))
        (self.assertEqual("lounge_usb_input_source", create_unique_id("Lounge USB input", EntityType.SOURCE)),)
        self.assertEqual(
            "wireless_mics_to_lovelace_route", create_unique_id("Wireless mics to Lovelace", EntityType.ROUTE)
        )


if __name__ == "__main__":
    unittest.main()
