#!/usr/bin/env bash

set -e

sudo modprobe vcan

# Create vcan0 if it doesn't exist
if ! ip link show vcan0 &> /dev/null; then
    sudo ip link add dev vcan0 type vcan
fi

sudo ip link set up vcan0

echo "vcan0 is up"
