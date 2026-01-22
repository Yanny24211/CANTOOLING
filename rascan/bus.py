import can

def open_bus(channel="vcan0", bitrate=500000):
    return can.interface.Bus(
        channel=channel,
        bustype="socketcan"
    )
