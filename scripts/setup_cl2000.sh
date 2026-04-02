# Load kernel modules
sudo modprobe can
sudo modprobe can_raw
sudo modprobe slcan

# Create SLCAN interface from the CL2000
# -o: opens device
# -c: closes device on exit
# -s6: sets speed to 500 kbps (adjust as needed)
#      s0=10k, s1=20k, s2=50k, s3=100k, s4=125k, s5=250k, s6=500k, s7=800k, s8=1M
# /dev/ttyACM0: your CL2000 device (verify with dmesg)
# can0: name of the SocketCAN interface to create

sudo slcand -o -c -s6 /dev/ttyACM0 can0

# Bring the interface up
sudo ip link set up can0