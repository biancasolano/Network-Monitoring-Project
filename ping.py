"""
ping.py
--------------------
This module generates predictable ICMP traffic by periodically
pinging a target host and logging the round-trip time (RTT) to a CSV file.

The output is used as the input for later packet-capture and analysis steps:
    • tcpdump records all packets at the network interface
    • PyShark reads the resulting .pcap file
    • analyze_ping.py computes RTT directly from captured ICMP packets

This script therefore provides the controlled "ground truth" RTT values
that we compare against the packet capture.
"""

import os
from ping3 import ping
import csv, time

# -----------------------------------------------------------
# CONFIGURATION
# -----------------------------------------------------------

# The host to ping.
#   • Use "localhost" for loopback tests
#   • Replace with a CS server IP (64.106.20.211) or Google DNS server (8.8.8.8)
host = "localhost"

# Output CSV used for logging timestamps + measured RTT.
# Each row = (send_timestamp, latency_ms)
output_file = f"csv_files/ping_log_{host}.csv"

# Number of ping samples to send and the delay between them.
samples = 5  # total number of pings to send
interval = 1 # seconds between each ping


# -----------------------------------------------------------
# OPEN OUTPUT CSV + START TRAFFIC GENERATION LOOP
# -----------------------------------------------------------
with open(output_file, "w", newline="") as f:
	writer = csv.writer(f)
	writer.writerow(["timestamp", "latency_ms"])
	for i in range(samples):
		t = time.time()
		rtt = ping(host, unit="ms")
		writer.writerow([f"{t:.2f}",f"{rtt:.2f}" if rtt is not None else "lost"])
		print(i, rtt)
		f.flush() # Force flush ensures data is not lost if the script is interrupted
		time.sleep(interval) 
