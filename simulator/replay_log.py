import time
import can
import re
from rascan.demo_bus import open_bus

# Path to the uploaded file
TXT_FILE_PATH = "simulator/0000090.TXT"

def parse_timestamp(ts_str):
    """
    Parses the CL2000 timestamp format DDThhmmssms 
    (e.g. 02T003735020) into total relative seconds.
    """
    match = re.match(r"(\d{2})T(\d{2})(\d{2})(\d{2})(\d{3})", ts_str)
    if not match:
        return None
    
    day, hour, minute, second, ms = map(int, match.groups())
    
    # Convert everything to total seconds to easily calculate time differences
    total_seconds = (day * 86400) + (hour * 3600) + (minute * 60) + second + (ms / 1000.0)
    return total_seconds

def main():
    bus = open_bus("vcan0")
    print(f"Starting playback from {TXT_FILE_PATH} on vcan0...")
    
    try:
        with open(TXT_FILE_PATH, 'r') as file:
            last_timestamp = None
            
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                
                # Skip the metadata headers and the column definition row
                if not line or line.startswith('#') or line.startswith('Timestamp'):
                    continue
                
                try:
                    # Split the line by semicolon
                    parts = line.split(';')
                    if len(parts) < 4:
                        continue
                        
                    ts_str = parts[0]
                    # Type '1' usually denotes an extended CAN ID (29-bit) in CL2000 logs
                    is_extended = (parts[1] == '1') 
                    arbitration_id = int(parts[2], 16)
                    
                    # Convert hex data to bytearray. (Pad with 0 if length is odd, to prevent fromhex errors)
                    hex_data = parts[3]
                    if len(hex_data) % 2 != 0:
                        hex_data = '0' + hex_data
                    data_bytes = bytes.fromhex(hex_data)
                    
                    # Compute sleep delay to simulate real-time playback
                    timestamp_sec = parse_timestamp(ts_str)
                    if timestamp_sec is None:
                        continue
                    
                    if last_timestamp is not None:
                        sleep_time = timestamp_sec - last_timestamp
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                            
                    last_timestamp = timestamp_sec
                    
                    # Create and send the raw CAN message
                    msg = can.Message(
                        arbitration_id=arbitration_id,
                        data=data_bytes,
                        is_extended_id=is_extended
                    )
                    
                    bus.send(msg)
                    
                except ValueError as e:
                    print(f"Line {line_num}: Error parsing - {e}")
                    
        print("Playback finished.")

    except FileNotFoundError:
        print(f"Error: Could not find the file {TXT_FILE_PATH}")
    except KeyboardInterrupt:
        print("\nExiting Playback...")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()