import unittest

from custom_components.office_audio_control.yamaha.response import ErrorResponse, OkResponse, parse_response


class YamahaResponseTest(unittest.TestCase):
    def test_parse_response(self):
        ok_response = parse_response('OK devstatus runmode "normal"\n')
        self.assertIsInstance(ok_response, OkResponse)
        self.assertEqual(["OK", "devstatus", "runmode", "normal"], ok_response.parsed_response)
        self.assertEqual("normal", ok_response.value)

        complex_ok_response = parse_response('OK ssinfo 0 "" reserve "" ""' + "\n")
        self.assertIsInstance(ok_response, OkResponse)
        self.assertEqual(["OK", "ssinfo", "0", "", "reserve", "", ""], complex_ok_response.parsed_response)

        error_response = parse_response("ERROR event WrongFormat")
        self.assertIsInstance(error_response, ErrorResponse)
        self.assertEqual("event", error_response.command_name)
        self.assertEqual("WrongFormat", error_response.error_code)


if __name__ == "__main__":
    unittest.main()
