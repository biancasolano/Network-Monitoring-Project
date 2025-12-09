import matplotlib.pyplot as plt

# ======================================
# Data
# ======================================
# These dictionaries represent protocol distributions extracted
# from PyShark after analyzing packet captures from three sources:
#
#   • Localhost       – loopback interface traffic
#   • Google          – external Internet host
#   • CS server       – campus network host
#
# Keys represent detected protocol types.
# Values represent packet counts for each protocol type.
#
# The avg_rtt_* variables store the average ICMP RTT for each host
# based on earlier capture/analysis (from analyze_ping.py).
# =========================================================

# Localhost
protocols_local = {'TCP': 4, 'UDP': 1, 'Unknown': 10}
avg_rtt_local = 0.0286102294921875

# Google
protocols_google = {'TCP': 80, 'UDP': 25, 'Unknown': 16}
avg_rtt_google = 47.40400314331055

# CS server
protocols_cs = {'TCP': 4, 'UDP': 0, 'Unknown': 10}   # No UDP in dataset
avg_rtt_cs = 88.59925270080566


# ======================================
# Helper function to plot each dataset
# ======================================

def plot_protocol_distribution(data, title, avg_rtt, filename):
    labels = list(data.keys())
    counts = list(data.values())

    plt.figure(figsize=(8,4))
    plt.bar(labels, counts)
    plt.title(f"Protocol Distribution: {title}\nAverage RTT = {avg_rtt:.2f} ms")
    plt.xlabel("Protocol")
    plt.ylabel("Count")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()


# ======================================
# Generate each plot
# ======================================

plot_protocol_distribution(protocols_local, "Localhost", avg_rtt_local, "graphs/localhost_protocols.png")
plot_protocol_distribution(protocols_google, "Google", avg_rtt_google, "graphs/google_protocols.png")
plot_protocol_distribution(protocols_cs, "CS Server", avg_rtt_cs, "graphs/cs_server_protocols.png")

