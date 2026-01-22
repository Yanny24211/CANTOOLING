import cantools
from rascan.bus import open_bus

class CANReader:
    def __init__(self, dbc_path, channel="vcan0"):
        self.db = cantools.database.load_file(dbc_path)
        self.bus = open_bus(channel)

    def read(self, timeout=1.0):
        msg = self.bus.recv(timeout)
        if not msg:
            return None

        try:
            decoded = self.db.decode_message(msg.arbitration_id, msg.data)
            return {
                "id": msg.arbitration_id,
                "signals": decoded
            }
        except KeyError:
            return None
