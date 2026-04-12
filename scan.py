import ctypes
ctypes.windll.ole32.CoInitializeEx(None, 0x2)  # COINIT_APARTMENTTHREADED
import asyncio
try:
    import audioop
except ImportError:
    import audioop_lts as audioop
import struct
import sounddevice as sd
import numpy as np
from bleak import BleakClient, BleakScanner
from bleak.backends.winrt.util import allow_sta
allow_sta._allowed = True

AUDIO_CONTROL = "f0d4de7e-4a88-476c-9d9f-1937b0996cc0"
AUDIO_STATUS  = "38663f1a-e711-4cac-b641-326b56404837"
VOLUME        = "00e4ca9e-ab14-41e4-8823-f9e70c7e91df"
LE_PSM_OUT    = "2d410339-82b6-42aa-b34e-e2e01df8cc1a"

CMD_START = 0x01
CMD_STOP  = 0x02

SAMPLE_RATE   = 16000
FRAME_MS      = 20
FRAME_SAMPLES = int(SAMPLE_RATE * FRAME_MS / 1000)

async def stream_audio():
    # Scan
    print("Scanning for Zircon...")
    address = None
    while address is None:
        devices = await BleakScanner.discover(timeout=5.0, return_adv=True)
        for addr, (device, adv) in devices.items():
            if device.name and "Mishan" in device.name:
                address = addr
                print(f"Found at {addr}")
                break
        if address is None:
            print("Retrying...")

    async with BleakClient(
        address,
        timeout=30.0,
        winrt=dict(use_cached_services=False)
    ) as client:
        print("Connected!")

        # Set volume
        await client.write_gatt_char(VOLUME, bytes([0x00]), response=False)

        # Send START command
        start_cmd = struct.pack('BBBBBB', CMD_START, 0x01, 0x01, 0, 0, 0)
        await client.write_gatt_char(AUDIO_CONTROL, start_cmd, response=False)
        print("Audio started!")
        print("Playing audio from your laptop speakers/system...")
        print("Press Ctrl+C to stop\n")

        await asyncio.sleep(1)

        # Find loopback device (system audio output)
        print("Available audio devices:")
        devices_list = sd.query_devices()
        loopback_device = None
        for i, dev in enumerate(devices_list):
            print(f"  [{i}] {dev['name']} (in:{dev['max_input_channels']} out:{dev['max_output_channels']})")
            if 'loopback' in dev['name'].lower() or 'stereo mix' in dev['name'].lower() or 'what u hear' in dev['name'].lower():
                loopback_device = i
                print(f"      ^ using this for system audio capture")

        if loopback_device is None:
            print("\nNo loopback device found - using default input instead")
            print("To capture system audio, enable 'Stereo Mix' in Windows sound settings")

        seq = 0
        loop = asyncio.get_event_loop()

        def audio_callback(indata, frames, time, status):
            nonlocal seq
            # Convert to mono 16-bit
            mono = indata[:, 0].astype(np.int16).tobytes()
            # Encode to ulaw (approximation of G.722 for now)
            encoded = audioop.lin2ulaw(mono, 2)
            # Build packet with sequence byte
            packet = bytes([seq & 0xFF]) + encoded
            seq += 1
            # Schedule send on event loop
            asyncio.run_coroutine_threadsafe(
                client.write_gatt_char(AUDIO_CONTROL, packet, response=False),
                loop
            )
            if seq % 50 == 0:
                print(f"Streaming... ({seq} packets sent)")

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            blocksize=FRAME_SAMPLES,
            device=loopback_device,
            callback=audio_callback
        ):
            try:
                while True:
                    await asyncio.sleep(0.1)
            except KeyboardInterrupt:
                print("\nStopping...")

        # Send STOP
        stop_cmd = struct.pack('B', CMD_STOP)
        await client.write_gatt_char(AUDIO_CONTROL, stop_cmd, response=False)
        print("Stopped.")

try:
    loop = asyncio.ProactorEventLoop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(stream_audio())
except Exception as e:
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
finally:
    loop.close()