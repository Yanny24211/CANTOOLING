from rascan.reader import CANReader

def main():
    reader = CANReader("dbc/example.dbc")

    while True:
        frame = reader.read()
        if frame:
            print(frame)

if __name__ == "__main__":
    main()
