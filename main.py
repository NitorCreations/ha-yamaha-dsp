import asyncio

from custom_components.office_audio_control.yamaha.device import YamahaDspDevice


async def main():
    device = YamahaDspDevice("10.110.3.75", 49280)

    print("Connecting")
    await device.connect()

    while True:
        try:
            product_information = await device.query_product_information()
            cafe_speakers_vol = (await device.query_parameter_normalized("MTX:Index_47")).get_int_value()
            cafe_speakers_muted = (await device.query_parameter_raw("MTX:Index_48")).get_bool_value()
            cafe_speakers_source = (await device.query_parameter_raw("MTX:Index_33")).get_int_value()
            classroom_speakers_vol = (await device.query_parameter_normalized("MTX:Index_51")).get_int_value()
            classroom_speakers_muted = (await device.query_parameter_raw("MTX:Index_52")).get_bool_value()
            print(product_information)
            print(cafe_speakers_vol)
            print(cafe_speakers_muted)
            print(cafe_speakers_source)
            # print(classroom_speakers_vol)
            # print(classroom_speakers_muted)

            await device.set_parameter_normalized("MTX:Index_47", "0", "0", "900")
            await device.set_parameter_raw("MTX:Index_48", "0", "0", "0")
        except Exception as e:
            print("Got exception", e)

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
