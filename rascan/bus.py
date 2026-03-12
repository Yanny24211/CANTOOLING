import can

def open_bus(channel=None, bitrate=500000):
    """
    Opens a CAN bus connection using the CSS Electronics serial interface.
    If no channel is provided, it attempts to auto-detect the CL2000.
    """
    if channel is None:
        configs = can.detect_available_configs("csscan_serial")
        if not configs:
            raise RuntimeError("No CL2000 device detected. Check your USB connection.")
        channel = configs[0]["channel"]
        print(f"Auto-detected CL2000 on {channel}")

    return can.interface.Bus(
        interface="csscan_serial",
        channel=channel,
        bitrate=bitrate
    )