# Network-Monitoring-Project
This project implements a complete network-monitoring workflow that collects traffic, 
captures packets, analyzes protocol behavior, measures RTT performance, and visualizes 
results across baseline and VPN conditions. It combines Python traffic generators, 
tcpdump/pcap analysis, PyShark parsing, and multi-condition RTT comparison.

# Python Scripts:
# Setting up baseline (ICMP)
- `ping.py`:
  - Generates predictable ICMP traffic by periodically pinging a target host. 
  Logs timestamps and RTTs to CSV for baseline analysis.
- `analyze_pcap.py`:
  - Parses a tcpdump-generated .pcap file using PyShark, counts transport-layer protocols, 
  and computes ICMP RTTs by matching Echo Requests and Echo Replies.
- `project_plots.py`:
  - This module makes plots based on the .csv produced from ping.py.
- `project_bar_plots.py`:
  - This module makes plots that represent protocol distributions extracted from 
  analyze_pcap.py. 

# Other Protocols
- `Trafficgen.py`
  - Generates multi-protocol traffic (ICMP, HTTP, DNS, TCP, UDP). Each probe is logged to 
  CSV. Optional: simultaneous live packet capture to a .pcap file

# VPN Tunneling
- `trace.py`
  - Loads baseline and VPN RTT datasets and generates a multi-line comparison plot. 
  Missing RTTs (common under VPN instability) are visualized with dotted-line interpolation.
- `collector.py`
  - Measures RTT to many websites under a specific network condition (baseline or VPN). 
  Produces clean RTT CSV files for large-scale comparison.
- `plot_rtt.py`
  - This script loads RTT (round-trip time) measurements from one or more CSV files
and generates a variety of visualizations.


# How to run programs: 

`ping.py` & `analyze_pcap.py`:
1. Run tcpdump but capture the data, use the command:
        `sudo tcpdump -i en0 -w capture_<host_name>.pcap`
if you get errors run `ifconfig -a` to see your interfaces and replace en0 with one that works on your system
2. On a new terminal run ping.py:
     `python3 ping.py`
3. Once it finishes ~5 secs `ctrl-c` the tcpdump terminal
4. Open wireshark with the capture.pcap file:
      `open -a Wirehshark capture.pcap`
   this should give you insite on the packet capture
5. Then you can run analyze_ping.py:
      `python3 analyze_ping.py`
   you may also need to update the log file from ping.py under `csv_files/ping_log_<host>.csv`
6. For further inspection you can run:
      `tshark -r capture.pcap -Y "tcp.analysis.retransmission" -T fields -e frame.number | wc -l`
   this command tells you the number of retransmissions (transport layer problems).

project_bar_plots.py & project_plots.py:
1. For both of these as long as you update the data you can simply run:
      `python3 <filename>`

`trace.py` & `collector.py` & `plot_rtt.py`:
1. Run `python collector.py`
2. Run `python trace.py`
3. Run `plot_rtt.py`

`Trafficgen.py`: 
1. Run `python Trafficgen.py`

# Other
- In our project structure we have two directories:
  - `graphs`: Contains all the graphs in our report. 
  - `csv_files`: Contains .csv files that we generated in our project. 