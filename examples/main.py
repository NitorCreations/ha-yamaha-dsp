import asyncio

from custom_components.yamaha_dsp.yamaha.device import YamahaDspDevice


async def main():
    device = YamahaDspDevice("10.110.3.75", 49280)

    # Connect to the device. The handshake is done automatically, so once connect() returns
    # we're ready to send commands
    print("Connecting")
    await device.connect()

    while True:
        try:
            # Query examples
            product_information = await device.query_product_information()
            cafe_speakers_vol = (await device.query_parameter_normalized("MTX:Index_47")).get_int_value()
            cafe_speakers_muted = (await device.query_parameter_raw("MTX:Index_48")).get_bool_value()
            cafe_speakers_source = (await device.query_parameter_raw("MTX:Index_33")).get_int_value()
            print(product_information)
            print(cafe_speakers_vol)
            print(cafe_speakers_muted)
            print(cafe_speakers_source)

            # Set parameter examples
            await device.set_parameter_normalized("MTX:Index_47", "0", "0", "900")
            await device.set_parameter_raw("MTX:Index_48", "0", "0", "0")
        except Exception as e:
            print("Got exception", e)

        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
