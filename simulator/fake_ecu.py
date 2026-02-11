import time
import random
import rascan
import cantools
import can
import time

from rascan.bus import open_bus

DBC_PATH = "dbc/example.dbc"


start_time = time.time()

def get_timestamp_seconds():
    return time.time() - start_time

def main():
    db = cantools.database.load_file(DBC_PATH)
    bus = open_bus("vcan0")

    vehicle_msg = db.get_message_by_name("VEHICLE_STATUS")
    turn_msg = db.get_message_by_name("TURN_SIGNALS")
    time_msg = db.get_message_by_name("TIME_STATUS")
    
    steering = 0.0
    throttle = 0.0
    speed = 0.0
    braking = False
    left = False
    right = False
    try:
        while True:
            # Simulate driving
            throttle = max(0, min(100, throttle + random.uniform(-5, 5)))
            speed = max(0, speed + throttle * 0.01 - (5 if braking else 0))
            braking = random.random() < 0.1
            left = random.random() < 0.05
            right = not left and random.random() < 0.05
            turn_strength = max(0.3, 1-speed/180) #limited steering at high speed
            if left: 
                steering += random.uniform(3, 8)*turn_strength
            elif right: 
                steering -= random.uniform(3, 8)*turn_strength
            
            if not left and not right: 
                steering *= 0.92
            else: 
                steering *= 0.97
        
            steering = max(-720, min(720, steering))

            timestamp_raw = get_timestamp_seconds()
            

            vehicle_data = vehicle_msg.encode({
                "Throttle": throttle,
                "Brake": 80 if braking else 0,
                "Speed": speed,
                "Steering": steering,
            })

            

            turn_data = turn_msg.encode({
                "Left": int(left),
                "Right": int(right),
            })

            time_status = time_msg.encode({
                "Timestamp": timestamp_raw
            })

            bus.send(can.Message(
                arbitration_id=vehicle_msg.frame_id,
                data=vehicle_data,
                is_extended_id=False
            ))

            bus.send(can.Message(
                arbitration_id=turn_msg.frame_id,
                data=turn_data,
                is_extended_id=False
            ))

            bus.send(can.Message(
                arbitration_id=time_msg.frame_id,
                data=time_status,
                is_extended_id=False
            ))

            time.sleep(0.5)  # 50 Hz
    except KeyboardInterrupt:
        print("Exiting ECU Sim ...")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()
