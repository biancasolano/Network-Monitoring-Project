# This module generates traffic by pinging a server

import os
from ping3 import ping
import csv, time

# the target being pinged, for simulating a problem change to localhost 
host = "8.8.8.8" # cs server IP

# csv file for results
output_file = "ping_log_google.csv"

samples = 5
interval = 1 #time in between pings


with open(output_file, "w", newline="") as f:
	writer = csv.writer(f)
	writer.writerow(["timestamp", "latency_ms"])
	for i in range(samples):
		t = time.time()
		rtt = ping(host, unit="ms")
		writer.writerow([f"{t:.2f}",f"{rtt:.2f}" if rtt is not None else "lost"])
		print(i, rtt)
		f.flush() # to not lose data 
		time.sleep(interval) 
