import asyncio
import audioop
import struct
from bleak import BleakClient, BleakScanner
from bleak.backends.winrt.util import allow_sta

allow_sta._allowed = True

ASHA_SERVICE    = "0000fdf0-0000-1000-8000-00805f9b34fb"
READ_ONLY_PROPS = "6333651e-c481-4a3e-9169-7c902aad37bb"
AUDIO_CONTROL   = "f0d4de7e-4a88-476c-9d9f-1937b0996cc0"
VOLUME          = "00e4ca9e-ab14-41e4-8823-f9e70c7e91df"
LE_PSM_OUT      = "2d410339-82b6-42aa-b34e-e2e01df8cc1a"

CMD_START = 0x01
CMD_STOP  = 0x02

SAMPLE_RATE   = 16000
FRAME_SAMPLES = 320

async def find_zircon():
    print("Scanning for Mishan Hearing aids...")
    while True:
        devices = await BleakScanner.discover(
            timeout=5.0,
            return_adv=True,
            cb=dict(use_bdaddr=True)
        )
        for addr, (device, adv) in devices.items():
            if device.name and "Mishan" in device.name:
                print(f"Found: {device.name} at {addr} (signal: {adv.rssi} dBm)")
                return addr
        print("Not found, retrying... (restart Zircon if stuck)")

async def main():
    address = await find_zircon()

    print("Connecting...")
    async with BleakClient(
        address,
        timeout=30.0,
        winrt=dict(use_cached_services=False)
    ) as client:
        print("Connected!")

        print("Pairing...")
        await client.pair()
        print("Paired! Waiting for authentication...")
        await asyncio.sleep(3)

        print("Reading device info...")
        data = await client.read_gatt_char(READ_ONLY_PROPS)
        side = "Right" if data[1] & 0x01 else "Left"
        print(f"Device    : {side} ear")

        psm_data = await client.read_gatt_char(LE_PSM_OUT)
        psm = int.from_bytes(psm_data, byteorder='little')
        print(f"Audio PSM : {psm}")

        await client.write_gatt_char(VOLUME, bytes([0x00]), response=False)

        start_cmd = struct.pack('BBBBBB', CMD_START, 0x01, 0x01, 0, 0, 0)
        await client.write_gatt_char(AUDIO_CONTROL, start_cmd, response=False)
        print("\nAudio channel opened!")
        print("Streaming audio to your Zircon...")
        print("Press Ctrl+C to stop\n")

        await asyncio.sleep(1)

        import sounddevice as sd
        import numpy as np

        print("Audio devices:")
        devices_list = sd.query_devices()
        loopback = None
        for i, dev in enumerate(devices_list):
            print(f"  [{i}] {dev['name']}")
            name = dev['name'].lower()
            if any(x in name for x in ['stereo mix', 'loopback', 'what u hear']):
                loopback = i
                print(f"       ^ will use this")

        if loopback is None:
            print("\nNo loopback device found, using default input.")

        seq = 0
        loop = asyncio.get_event_loop()
        errors = []

        def audio_callback(indata, frames, time, status):
            nonlocal seq
            try:
                mono = indata[:, 0].astype(np.int16).tobytes()
                encoded = audioop.lin2ulaw(mono, 2)
                packet = bytes([seq & 0xFF]) + encoded
                seq += 1
                asyncio.run_coroutine_threadsafe(
                    client.write_gatt_char(
                        AUDIO_CONTROL, packet, response=False
                    ),
                    loop
                )
                if seq % 100 == 0:
                    print(f"Streaming... {seq} packets sent")
            except Exception as e:
                errors.append(e)

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            blocksize=FRAME_SAMPLES,
            device=loopback,
            callback=audio_callback
        ):
            try:
                while True:
                    await asyncio.sleep(0.1)
                    if errors:
                        print(f"Audio error: {errors[-1]}")
                        errors.clear()
            except KeyboardInterrupt:
                print("\nStopping...")

        stop_cmd = struct.pack('B', CMD_STOP)
        await client.write_gatt_char(AUDIO_CONTROL, stop_cmd, response=False)
        print("Done!")

loop = asyncio.ProactorEventLoop()
asyncio.set_event_loop(loop)
try:
    loop.run_until_complete(main())
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
finally:
    loop.close()