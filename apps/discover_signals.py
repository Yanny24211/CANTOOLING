#!/usr/bin/env python3
"""
Interactive DBC Builder for Nissan Versa
Discovers correct bit positions from live CAN data
"""
import time
from collections import defaultdict
from rascan.reader import CANReader

class DBCBuilder:
    def __init__(self, channel=None):
        # Initialize CANReader with no DBC files to establish the bus connection
        self.reader = CANReader(dbc_paths=[], channel=channel)
        self.signals = []
        
    def capture_baseline(self, can_id, duration=5):
        """Capture baseline data for a CAN ID"""
        print(f"\nCapturing baseline for ID 0x{can_id:03X}...")
        print(f"Don't touch anything for {duration} seconds!")
        
        samples = []
        start = time.time()
        
        while time.time() - start < duration:
            # Access the underlying bus from CANReader for raw bytes
            msg = self.reader.bus.recv(timeout=0.1)
            if msg and msg.arbitration_id == can_id:
                samples.append(bytes(msg.data))
        
        if not samples:
            print(f"  ✗ No messages received for ID 0x{can_id:03X}")
            return None
        
        # Use most common value as baseline
        baseline = max(set(samples), key=samples.count)
        print(f"  ✓ Baseline captured ({len(samples)} samples)")
        return baseline
    
    def capture_active(self, can_id, action, duration=5):
        """Capture data while performing an action"""
        print(f"\n{action} NOW! ({duration} seconds)")
        
        samples = []
        start = time.time()
        
        while time.time() - start < duration:
            # Access the underlying bus from CANReader for raw bytes
            msg = self.reader.bus.recv(timeout=0.1)
            if msg and msg.arbitration_id == can_id:
                samples.append(bytes(msg.data))
        
        if not samples:
            print(f"  ✗ No messages received")
            return None
        
        # Use most common value
        active = max(set(samples), key=samples.count)
        print(f"  ✓ Active data captured ({len(samples)} samples)")
        return active
    
    def find_changing_bytes(self, baseline, active):
        """Find which bytes changed"""
        changes = []
        
        for i in range(min(len(baseline), len(active))):
            if baseline[i] != active[i]:
                changes.append({
                    'byte': i,
                    'off': baseline[i],
                    'on': active[i],
                    'diff': abs(int(active[i]) - int(baseline[i]))
                })
        
        return changes
    
    def discover_signal(self, name, can_id, action):
        """Discover a signal interactively"""
        print("\n" + "="*70)
        print(f"Discovering: {name} (ID: 0x{can_id:03X})")
        print("="*70)
        
        baseline = self.capture_baseline(can_id)
        if baseline is None:
            return False
        
        active = self.capture_active(can_id, action)
        if active is None:
            return False
        
        changes = self.find_changing_bytes(baseline, active)
        
        if not changes:
            print("  ✗ No bytes changed!")
            return False
        
        print(f"\n  Bytes that changed:")
        for ch in changes:
            print(f"    Byte {ch['byte']}: 0x{ch['off']:02X} → 0x{ch['on']:02X}  (diff: {ch['diff']})")
        
        # Take the byte with biggest change
        main_change = max(changes, key=lambda x: x['diff'])
        byte_pos = main_change['byte']
        
        # Estimate bit position and length
        start_bit = byte_pos * 8
        
        # Determine signal length based on value range
        max_val = max(main_change['off'], main_change['on'])
        if max_val < 2:
            length = 1  # Binary
        elif max_val < 16:
            length = 4  # 4 bits
        elif max_val < 256:
            length = 8  # 1 byte
        else:
            length = 16  # 2 bytes
        
        signal = {
            'name': name,
            'can_id': can_id,
            'start_bit': start_bit,
            'length': length,
            'byte_order': '1',  # Intel (little endian)
            'value_type': '+',   # Unsigned
            'scale': 1.0,
            'offset': 0.0,
            'min': 0,
            'max': (2 ** length) - 1,
            'unit': ''
        }
        
        self.signals.append(signal)
        print(f"\n  ✓ Signal added:")
        print(f"    Bit: {start_bit}, Length: {length}, Byte order: Intel")
        
        return True
    
    def generate_dbc(self, output_file):
        """Generate DBC file from discovered signals"""
        
        # Group by CAN ID
        messages = defaultdict(list)
        for sig in self.signals:
            messages[sig['can_id']].append(sig)
        
        dbc = 'VERSION ""\n\nNS_ :\n\nBS_:\n\nBU_: ECU\n\n'
        
        for can_id in sorted(messages.keys()):
            sigs = messages[can_id]
            msg_name = sigs[0]['name'].replace('_', '') if sigs else f"MSG_{can_id:03X}"
            
            dbc += f"BO_ {can_id} {msg_name}: 8 ECU\n"
            
            for sig in sigs:
                dbc += f" SG_ {sig['name']} : {sig['start_bit']}|{sig['length']}@{sig['byte_order']}{sig['value_type']}"
                dbc += f" ({sig['scale']},{sig['offset']}) [{sig['min']}|{sig['max']}] \"{sig['unit']}\" ECU\n"
            
            dbc += "\n"
        
        with open(output_file, 'w') as f:
            f.write(dbc)
        
        print(f"\n✓ DBC file created: {output_file}")
        print(f"  Messages: {len(messages)}")
        print(f"  Signals: {len(self.signals)}")

def main():
    print("="*70)
    print("  Nissan Versa Interactive DBC Builder")
    print("="*70)
    print("\nThis will help you discover the correct bit positions for your car.")
    print("Make sure your car engine is RUNNING and CL2000 is streaming!\n")
    
    input("Press Enter when ready...")
    
    builder = DBCBuilder()
    
    # Expanded key signals list
    # Note: The CAN IDs here are common standard ones, but may require adjustment 
    # if Nissan mapped them to different arbitration IDs for your specific model year.
    signals_to_discover = [
        ("Throttle_Percentage", 0x180, "Press accelerator pedal to 50%"),
        ("Brake_Percentage", 0x292, "Press brake pedal to 50%"),
        ("Turn_Signal_Left", 0x60D, "Turn ON the LEFT turn signal"),
        ("Turn_Signal_Right", 0x60D, "Turn ON the RIGHT turn signal"),
        ("Hazard_Lights", 0x60D, "Turn ON the Hazard Lights"),
        ("Headlights", 0x60D, "Turn ON the Headlights"),
        ("Vehicle_Speed", 0x284, "Drive vehicle steadily at ~10 mph (Requires safe open area)"),
        ("Steering_Angle", 0x002, "Turn the steering wheel 90 degrees to the left"),
        ("Door_Driver", 0x358, "Open the driver's side door"),
        ("Seatbelt_Driver", 0x358, "Buckle the driver's seatbelt"),
    ]
    
    for name, can_id, action in signals_to_discover:
        success = builder.discover_signal(name, can_id, action)
        if not success:
            print(f"\n⚠️  Skipping {name}")
        
        time.sleep(2)
    
    # Generate DBC
    output = "nissan_versa_discovered.dbc"
    builder.generate_dbc(output)
    
    print("\n" + "="*70)
    print("  Discovery Complete!")
    print("="*70)
    print(f"\nTest your new DBC file:")
    print(f"  python test_dbc.py {output}")
    print("\nIf signals don't decode correctly, you can manually adjust")
    print("the bit positions in the DBC file.\n")

if __name__ == "__main__":
    main()