# ha-yamaha-dsp

[![Linting](https://github.com/NitorCreations/ha-yamaha-dsp/actions/workflows/ruff.yaml/badge.svg)](https://github.com/NitorCreations/ha-yamaha-dsp/actions/workflows/ruff.yaml)
[![Tests](https://github.com/NitorCreations/ha-yamaha-dsp/actions/workflows/unittest.yaml/badge.svg)](https://github.com/NitorCreations/ha-yamaha-dsp/actions/workflows/unittest.yaml)

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
* toggles (on/off switches)
* routers (select, one source selection per sink)

Entities are configured using JSON, like this:

A speaker:
```json
{
  "name": "Kitchen",
  "index_source": 33,
  "index_volume": 47,
  "index_mute": 48
}
```

A source:
```json
{
  "name": "Lounge DJ mixer",
  "index_volume": 11,
  "index_mute": 12
}
```

A toggle:
```json
{
  "name": "Wireless mics to classroom",
  "index_toggle": 2
}
```

A router sink:
```json
{
  "name": "Classroom sink",
  "index_source": 20019,
  "sources": [
    { "label": "NONE", "value": 0 },
    { "label": "Mic bus", "value": 3 },
    { "label": "YDIF IN 1", "value": 17 }
  ]
}
```

Router entities behave like a matrix selector per sink: each sink exposes the allowed source options that
you configure, and exactly one source can be selected at a time for each sink.

## Development

Development is done the same way as any custom Home Assistant integration. For a more detailed description, see 
e.g. https://github.com/NitorCreations/ha-extron?tab=readme-ov-file#development.

The [examples](./examples) directory contains a small sample program that illustrates how the library for 
communicating with the Yamaha DSP works.

## License

GNU GENERAL PUBLIC LICENSE version 3
