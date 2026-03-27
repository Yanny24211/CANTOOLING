from datetime import datetime
from rascan.reader import CANReader

dbc_paths = ["dbc/nissan_versa_2014.dbc"]

def main():  
    reader = CANReader(dbc_paths)
    
    # Generate Log File
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = f"can_log_{timestamp_str}.txt"

    try:
        print(f"Starting live monitor...")
        print(f"Logging all decoded data to: {log_filename}")
        print("Press Ctrl+C to exit.\n")
        
        # Open the file in append mode ("a")
        with open(log_filename, "a") as log_file:
            while True:
                frame = reader.read()
                if frame:
                    # Create a readable timestamp for the specific CAN frame
                    current_time = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                    
                    # Format the output string
                    log_entry = f"[{current_time}] ID: {frame['id']} | Signals: {frame['signals']}"
                    
                    # Print it to your terminal so you can still watch it live
                    print(log_entry)
                    
                    # Write it to the text file and force the Pi to save it immediately
                    log_file.write(log_entry + "\n")
                    log_file.flush() 

    except KeyboardInterrupt:
        print(f"\nMonitor stopped. Your data is safely saved in {log_filename}")

if __name__ == "__main__":
    main()