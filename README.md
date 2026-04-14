# asha-windows

> **The first open-source attempt at implementing ASHA (Audio Streaming for Hearing Aids) on Windows using Python.**

[![Language](https://img.shields.io/badge/language-Python-blue)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)](https://www.microsoft.com/windows)
[![Protocol](https://img.shields.io/badge/protocol-BLE%20%2F%20ASHA-green)](https://source.android.com/docs/core/connect/bluetooth/asha)
[![Status](https://img.shields.io/badge/status-Partial%20Implementation-orange)]()

---

## What is ASHA?

**ASHA (Audio Streaming for Hearing Aids)** is a Bluetooth Low Energy (BLE) protocol developed by Google that allows hearing aids to receive audio directly from a device. It is natively supported on Android and Linux, but **not on Windows**.

ASHA works over a BLE channel called **L2CAP CoC (Connection-Oriented Channel)** — a low-latency, reliable transport specifically designed for streaming audio to hearing aids.

---

## The Problem: Windows and ASHA

Windows does not expose the **L2CAP CoC API** in its public Bluetooth stack (WinRT/Windows.Devices.Bluetooth). This is the fundamental blocker for ASHA on Windows:

| Layer | Status |
|---|---|
| BLE device scanning | ✅ Supported by Windows |
| BLE pairing & connection | ✅ Supported by Windows |
| GATT (reading device info) | ✅ Supported by Windows |
| L2CAP CoC (audio streaming) | ❌ **Not exposed by Windows** |

Without L2CAP CoC, it is impossible to open the audio streaming channel that ASHA requires — no matter what software approach is taken. This is not a fixable bug; it is a missing feature in the Windows Bluetooth stack.

Microsoft has not publicly committed to adding L2CAP CoC support. There are open requests on the Windows Feedback Hub, but no roadmap exists as of 2025.

### Why can't we work around it?

The only true workaround would be writing a **custom kernel-mode driver** (KMDF/WDM) that interfaces directly with the Bluetooth hardware below the Windows API level. This is an extremely complex undertaking requiring:

- Deep knowledge of Windows kernel internals
- Bluetooth HCI/L2CAP protocol implementation from scratch
- Microsoft driver signing certification
- Months to years of development time

For most users and developers, this is not a realistic path.

---

## What This Project Does

Despite the L2CAP CoC limitation, this project implements everything that *is* possible on Windows today:

### ✅ Working

- **BLE Scanning** — discovers ASHA-compatible hearing aids in range
- **BLE Connection & Pairing** — connects to hearing aids via Bluetooth LE
- **GATT Service Discovery** — reads the ASHA service and characteristics
- **Device Capability Reading** — retrieves codec type, PSM value, device side (left/right)
- **ASHA Control Commands** — sends START and STOP audio stream commands
- **System Audio Capture** — captures desktop audio via Windows Stereo Mix

### ❌ Not Working (and why)

- **L2CAP CoC Audio Channel** — Windows does not expose this API. The `bridge.py` script reaches the point of attempting to open this channel and fails. This is where the audio stream would flow to the hearing aid.
- **Actual audio delivery to the hearing aid** — depends entirely on the above

---

## File Structure

```
asha-windows/
├── scan.py       # BLE scanner — finds ASHA hearing aids and reads their capabilities
├── bridge.py     # Connection bridge — pairs, sends control commands, attempts audio channel
└── README.md
```

### scan.py

Scans for nearby BLE devices and filters for those advertising the ASHA service UUID. Prints device name, address, side (left/right), codec, and PSM value.

### bridge.py

Connects to a discovered hearing aid, reads GATT characteristics, sends an ASHA START command, captures system audio via Stereo Mix, and attempts to open an L2CAP CoC channel for streaming. This is where execution halts due to Windows API limitations.

---

## Requirements

- Windows 10 / Windows 11
- Bluetooth 5.0 adapter
- Python 3.9+
- A hearing aid supporting the ASHA protocol (tested with Oticon Zircon 1 miniRITE)
- Stereo Mix enabled in Windows sound settings (for audio capture)

### Install dependencies

```bash
pip install bleak sounddevice numpy
```

---

## Usage

### 1. Scan for hearing aids

```bash
python scan.py
```

This will list nearby ASHA-compatible devices with their capabilities.

### 2. Attempt connection and bridging

```bash
python bridge.py
```

This connects to the first discovered hearing aid, reads its profile, sends control commands, and attempts to open the audio channel (which will fail at the L2CAP CoC step on Windows).

---

## Tested With

| Hardware | Result |
|---|---|
| Oticon Zircon 1 miniRITE | Scan ✅ / Connect ✅ / Stream ❌ |
| Dell Inspiron 15 (Windows 11, BT 5.0) | Host platform |

---

## Solutions That Actually Work Today

If you need hearing aid audio streaming working *right now*, here are two proven alternatives:

### 🔌 Pico-ASHA (Recommended for Windows users)

[Pico-ASHA](https://github.com/shermp/Pico-ASHA) uses a **Raspberry Pi Pico W (~$6)** as a USB audio bridge. It appears as a standard sound card in Windows and handles ASHA streaming in hardware — no driver or API hacking required. This is the most practical solution for Windows users today.

### 🐧 Linux — asha_pipewire_sink

If you can run Linux, [asha_pipewire_sink](https://github.com/thewierdnut/asha_pipewire_sink) is a mature, working solution built on BlueZ and PipeWire. Linux's BlueZ Bluetooth stack fully exposes L2CAP CoC, making real ASHA audio streaming possible.

---

## Roadmap / Next Steps

- [ ] Test on Ubuntu via WSL2 + Bluetooth passthrough (experimental)
- [ ] Investigate undocumented WinRT APIs for L2CAP CoC access
- [ ] Ubuntu dual boot with BlueZ + asha_pipewire_sink as reference implementation
- [ ] Document exact Windows API error responses when L2CAP CoC is attempted (for future researchers)

---

## For Developers / Researchers

If you are looking into this problem, here are the key reference points:

- [Google ASHA Specification](https://source.android.com/docs/core/connect/bluetooth/asha) — official protocol spec
- [asha_pipewire_sink](https://github.com/thewierdnut/asha_pipewire_sink) — working Linux implementation to reference
- [Asymptotic BlueZ ASHA writeup](https://asymptotic.io/blog/a-brimful-of-asha/) — good technical deep-dive
- [Pico-ASHA](https://github.com/shermp/Pico-ASHA) — hardware workaround
- Windows Feedback Hub — search "L2CAP CoC" to upvote existing requests to Microsoft

The most valuable contribution to this project right now would be someone with **Windows kernel driver experience** exploring whether a KMDF driver could implement L2CAP CoC support below the WinRT API layer.

---

## Contributing

Contributions are welcome, especially:

- Testing with other hearing aid brands (Phonak, Starkey, Widex, etc.)
- Investigating undocumented Windows Bluetooth APIs
- Kernel driver expertise
- Documentation improvements

Please open an issue before starting significant work so efforts aren't duplicated.

---

## Acknowledgements

Built with assistance from [Claude](https://claude.ai) (Anthropic).

---

## License

MIT
