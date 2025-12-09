from datetime import datetime
import matplotlib.pyplot as plt

# ============================================
# Data
# ============================================

## CS Server results
latency_cs = [154.81, 77.72, 66.18, 76.29, 69.67]
timestamps_cs = [1761665091.37, 1761665092.54, 1761665093.62, 1761665094.69, 1761665095.77]
times_cs = [datetime.fromtimestamp(t) for t in timestamps_cs]

## Google server results
latency_g = [58.70, 54.52, 47.82, 43.05, 34.02]
timestamps_g = [1761665402.42, 1761665403.48, 1761665404.54, 1761665405.59, 1761665406.64]
times_g = [datetime.fromtimestamp(t) for t in timestamps_g]

## Localhost results
latency = [0.09, 0.14, 0.74, 0.20, 0.36]
timestamps = [1761665888.37, 1761665889.38, 1761665890.38, 1761665891.39, 1761665892.39]
times = [datetime.fromtimestamp(t) for t in timestamps]


# ============================================
# Plot
# ============================================

plt.figure(figsize=(8,5))
plt.plot(times_cs, latency_cs, marker='o')
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.title("ICMP Baseline Performance (CS Servers)")
plt.grid(True)
plt.gcf().autofmt_xdate()
plt.show()

plt.figure(figsize=(8,5))
plt.plot(times_g, latency_g, marker='o')
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.title("ICMP Baseline Performance (Google Servers)")
plt.grid(True)
plt.gcf().autofmt_xdate()
plt.show()

plt.figure(figsize=(8,5))
plt.plot(times, latency, marker='o')
plt.xlabel("Time")
plt.ylabel("Latency (ms)")
plt.title("ICMP Baseline Performance (Localhost)")
plt.grid(True)
plt.gcf().autofmt_xdate()
plt.show()
