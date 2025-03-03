# ha-yamaha-dsp

Home Assistant integration for controlling Yamaha DSP processors such as the MRX7-D.

## Supported devices

* Yamaha MRX7-D

## Requirements

The DSP must have Telnet access enabled

## Features

Since the DSP is a complicated device that allows for very fine-grained customization, the 
integration tries to be fairly generic. This means that out of the box, no entities are created 
when you configure the integration - everything must be configured explicitly.

The following entity types can be configured:

* speakers (media player, with source selection)
* sources (media player)
* routes (on/off switches)

## Development

Development is done the same way as any custom Home Assistant integration. For a more detailed description, see 
e.g. https://github.com/NitorCreations/ha-extron?tab=readme-ov-file#development.

## License

GNU GENERAL PUBLIC LICENSE version 3
