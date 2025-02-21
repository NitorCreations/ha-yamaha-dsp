import asyncio

from custom_components.office_audio_control.yamaha.device import YamahaDspDevice


async def main():
    device = YamahaDspDevice("10.110.3.75", 49280)

    print("Connecting")
    await device.connect()

    while True:
        try:
            product_information = await device.query_product_information()
            print(product_information)
        except Exception as e:
            print("Got exception", e)

        await asyncio.sleep(3)


if __name__ == '__main__':
    asyncio.run(main())
