# Network-Monitoring-Project

Instructions:

1. install things
   - scapy, pyshark, ping3, matplotlib, wireshark, tcpdump, python3-pip, ping3
2. Run tcpdump but capture the data, use the command:
   - sudo tcpdump -i en0 -w capture.pcap
   - if you get errors run ifconfig -a to see your interfaces and replace en0 with one that works on your system
3. On a new terminal run ping.py:
   - "python3 ping.py"
   - once it finishes ~5 secs ctrl-c the tcpdump terminal
4. open wireshark with the capture.pcap file:
   - "open -a Wirehshark capture.pcap"
   - this should give you insite on the packet caputure
5. then you can run analyze_ping.py:
   - "python3 analyze_ping.py"
   - you can also see the log file from ping.py under ping_log.csv
6. for further inspection you can run:
   - tshark -r capture.pcap -Y "tcp.analysi.retransmission" -T fields -e frame.number | wc -l
   - this command tells you the number of retransmissions (transport layer problems).

Next steps:
- look at proposal and start simulating problems
- analyze them
- make plots
