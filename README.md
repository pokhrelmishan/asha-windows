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

## References
- [Google ASHA spec](https://source.android.com/docs/core/connect/bluetooth/asha)
- [asha_pipewire_sink](https://github.com/thewierdnut/asha_pipewire_sink)
- [Asymptotic BlueZ ASHA](https://asymptotic.io/blog/a-brimful-of-asha/)
