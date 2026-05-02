import unittest

from custom_components.yamaha_dsp import EntityType, create_dsp_configuration, create_unique_id


class UtilsTests(unittest.TestCase):
    def test_create_unique_id(self):
        self.assertEqual("kitchen_speaker", create_unique_id("Kitchen", EntityType.SPEAKER))
        (self.assertEqual("lounge_usb_input_source", create_unique_id("Lounge USB input", EntityType.SOURCE)),)
        self.assertEqual(
            "wireless_mics_to_lovelace_toggle", create_unique_id("Wireless mics to Lovelace", EntityType.TOGGLE)
        )
        self.assertEqual("classroom_sink_router", create_unique_id("Classroom sink", EntityType.ROUTER))

    def test_configuration_parsing(self):
        options = {
            "toggle_configuration": [
                """
                {
                    "name": "Some toggle",
                    "index_toggle": 109
                }
                """
            ],
            "router_configuration": [
                """
                {
                  "name": "Classroom sink",
                  "index_source": 20019,
                  "sources": [
                    { "label": "NONE", "value": 0 },
                    { "label": "Mic bus", "value": 3 }
                  ]
                }
                """
            ]
        }
        config = create_dsp_configuration(options)

        # Check toggles
        self.assertEqual(1, len(config.toggles))
        toggle = config.toggles[0]
        self.assertEqual("Some toggle", toggle.name)
        self.assertEqual(109, toggle.index_toggle)

        # Check routers
        self.assertEqual(1, len(config.routers))
        router = config.routers[0]
        self.assertEqual("Classroom sink", router.name)
        self.assertEqual(20019, router.index_source)
        self.assertEqual(["NONE", "Mic bus"], [source.label for source in router.sources])
        self.assertEqual([0, 3], [source.value for source in router.sources])

    def test_router_configuration_rejects_duplicate_labels(self):
        options = {
            "router_configuration": [
                """
                {
                  "name": "Classroom sink",
                  "index_source": 20019,
                  "sources": [
                    { "label": "Mic bus", "value": 1 },
                    { "label": "Mic bus", "value": 2 }
                  ]
                }
                """
            ]
        }

        with self.assertRaises(ValueError):
            create_dsp_configuration(options)


if __name__ == "__main__":
    unittest.main()
