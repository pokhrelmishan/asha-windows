# asha-windows

# asha-windows

First open source attempt at implementing ASHA (Audio Streaming for Hearing Aids) 
on Windows, written in Python.

## What works
- Scanning and finding ASHA hearing aids on Windows
- Connecting and pairing via BLE
- Reading device capabilities (codec, PSM, side)
- Sending ASHA control commands (START/STOP)
- Capturing system audio via Stereo Mix

## What doesn't work yet
- L2CAP CoC audio channel (Windows doesn't expose this API)
- Actual audio streaming to the hearing aid

## Tested with
- Oticon Zircon 1 miniRITE
- Dell Inspiron 15, Windows 11, Bluetooth 5.0

## Next steps
- Ubuntu dual boot with BlueZ + asha_pipewire_sink

## Alternative solutions

### Pico-ASHA (recommended for Windows users right now)
If you just want audio streaming to work on Windows today without waiting for 
a software solution, [Pico-ASHA](https://github.com/shermp/Pico-ASHA) uses a 
$6 Raspberry Pi Pico W as a USB audio bridge. It appears as a normal sound card 
in Windows and streams audio to ASHA hearing aids. No software hacking required.

### Linux (asha_pipewire_sink)
If you run Linux, [asha_pipewire_sink](https://github.com/thewierdnut/asha_pipewire_sink) 
is a mature working solution using BlueZ and PipeWire.

## References
- [Google ASHA spec](https://source.android.com/docs/core/connect/bluetooth/asha)
- [asha_pipewire_sink](https://github.com/thewierdnut/asha_pipewire_sink)
- [Asymptotic BlueZ ASHA](https://asymptotic.io/blog/a-brimful-of-asha/)
- [Pico-ASHA](https://github.com/shermp/Pico-ASHA) - Hardware solution using Raspberry Pi Pico W, works on Windows

  *Built with assistance from Claude (Anthropic) as an AI pair programmer.*
