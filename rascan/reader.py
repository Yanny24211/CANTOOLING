import cantools
from rascan.bus import open_bus

class CANReader:
    def __init__(self, dbc_paths, channel=None):
        self.db = cantools.database.Database()

        if isinstance(dbc_paths, str):
            dbc_paths = [dbc_paths]
        
        for path in dbc_paths:
            print(f"Loading DBC: {path}")
            self.db.add_dbc_file(path)

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
        except cantools.database.errors.DecodeError as e:
            # Print the exact error so we can fix the DBC file
            print(f"Dropped ID {msg.arbitration_id} ({hex(msg.arbitration_id)}): {e}")
            return None
