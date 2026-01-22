import time
import random
import rascan
import cantools
import can

from rascan.bus import open_bus

DBC_PATH = "dbc/example.dbc"

def main():
    db = cantools.database.load_file(DBC_PATH)
    bus = open_bus("vcan0")

    vehicle_msg = db.get_message_by_name("VEHICLE_STATUS")
    turn_msg = db.get_message_by_name("TURN_SIGNALS")

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

            vehicle_data = vehicle_msg.encode({
                "Throttle": throttle,
                "Brake": 80 if braking else 0,
                "Speed": speed,
            })

            turn_data = turn_msg.encode({
                "Left": int(left),
                "Right": int(right),
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

            time.sleep(0.5)  # 50 Hz
    except KeyboardInterrupt:
        print("Exiting ECU Sim ...")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    main()
