"""
analyze_ping.py
---------------
This module parses a tcpdump-generated packet capture (.pcap) file, identifies
transport-layer protocols, and computes ICMP RTTs by matching Echo Requests
and Echo Replies. This replicates the logic of the `ping` utility, but using
packet timestamps directly from the network capture.

The output includes:
    • A protocol distribution summary (TCP / UDP / ICMP / Unknown)
    • An average RTT calculation based solely on observed packets
"""

import pyshark
from collections import Counter


# -----------------------------------------------------------
# Load the capture file produced by tcpdump.
# This reads packets lazily, so large files do not overwhelm memory.
# You can change the .pcap file it analyzes by changing the cap variable.
# capture_cs_server.pcap, capture_google.pcap, capture_localhost.pcap
# -----------------------------------------------------------
cap = pyshark.FileCapture("capture_cs_server.pcap")
# Tracks frequency of each protocol observed in the capture.
protocol_counts = Counter()
# ICMP tracking tables:
#  requests[(id, seq)] = timestamp of ICMP Echo Request
#  rtts = list of computed round-trip times (milliseconds)
requests = {}
rtts = []

# -----------------------------------------------------------
# Iterate through every packet in the capture file.
# PyShark decodes packet layers in real time as they are accessed.
# -----------------------------------------------------------
for pkt in cap:
	# ------------------------------
	# Determine the packet's protocol.
	# ------------------------------
	# If the packet has a well-defined transport layer (TCP/UDP/ICMP),
	# PyShark exposes it as `pkt.transport_layer`.
	#
	# Many packets (ARP, ICMP, encapsulated or encrypted traffic)
	# do not have traditional transport-layer headers. In those cases,
	# we fall back to `pkt.highest_layer`, which is PyShark's best guess
	# at the primary protocol.
	# ------------------------------
	protocol_counts[pkt.transport_layer if hasattr(pkt, "transport_layer") else pkt.highest_layer] += 1

	# -----------------------------------------------------------
	# ICMP RTT COMPUTATION
	# -----------------------------------------------------------
	# Only proceed if this packet contains an ICMP layer.
	# (PyShark allows `"ICMP" in pkt` as a convenient layer check.)
	# -----------------------------------------------------------
	if "ICMP" in pkt:
		# ICMP type field:
		#   8 = Echo Request
		#   0 = Echo Reply
		icmp_type = int(pkt.icmp.type)
		# ICMP Echo packets contain an (id, seq) pair that uniquely identifies
		# the request–reply relationship. These fields allow us to match them.
		ident = getattr(pkt.icmp, "id", None)
		seq = getattr(pkt.icmp, "seq", None)
		key = (ident, seq)
		# Timestamp of when this packet was sniffed (float, seconds).
		t = pkt.sniff_time.timestamp()

		# -----------------------------------------------------------
		# If packet is an Echo Request (type 8), record its timestamp.
		# -----------------------------------------------------------
		if icmp_type == 8:
			requests[key] = t
		# -----------------------------------------------------------
		# If packet is an Echo Reply (type 0), compute delta time.
		# -----------------------------------------------------------
		elif icmp_type == 0:
			if key in requests:
				# RTT = (reply_time - request_time)
				# Convert seconds to milliseconds.
				rtts.append((t- requests[key]) * 1000)

# -----------------------------------------------------------
# OUTPUT RESULTS
# -----------------------------------------------------------
print("Protocol counts: ", protocol_counts)

if rtts:
	print("Average RTT (ms): ", sum(rtts)/len(rtts))
else:
	print("No RTTs computed")

