# this module will count packets and compute simple icmp (ping) rtts

import pyshark
from collections import Counter
from datetime import datetime

# opens the capture file from running tcpdump
cap = pyshark.FileCapture("capture_google.pcap")
protocol_counts = Counter()
requests = {}
rtts = []

# loops through every packet in file
for pkt in cap:
	# checks if it has a transport layer attribute like TCP,UDP, ICMP, if yes use that as a protocol name
	# if no, fall back to the highest layer. Increment the count
	protocol_counts[pkt.transport_layer if hasattr(pkt, "transport_layer") else pkt.highest_layer] += 1

	# if it is a ICMP (ping) check for echo request (8) or reply (0)
	if "ICMP" in pkt:
		icmp_type = int(pkt.icmp.type)
		# id and seq are pair that uniquely identify each ping
		ident = getattr(pkt.icmp, "id", None)
		seq = getattr(pkt.icmp, "seq", None)
		key = (ident, seq)
		t = pkt.sniff_time.timestamp()

		#This is basically replicating what ping does internally
		# — measuring the time between sending and receiving
		# — but using the captured packets instead of your Python script’s timers.
		if icmp_type == 8: # request
			requests[key] = t
		elif icmp_type == 0: # reply
			if key in requests:
				rtts.append((t- requests[key]) * 1000) #ms


print("Protocol counts: ", protocol_counts)

if rtts:
	print("Average RTT (ms): ", sum(rtts)/len(rtts))
else:
	print("No RTTs computed")

