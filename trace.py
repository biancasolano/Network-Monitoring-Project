import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import math

# Load CSV
df = pd.read_csv("/Users/ok/Documents/combined_rtt_clean1.csv")
df["rtt"] = pd.to_numeric(df["rtt"], errors="coerce")

baseline = df[df["condition"].str.lower() == "baseline"]
vpn1 = df[df["condition"].str.contains("vpn1", case=False, na=False)]
vpn2 = df[df["condition"].str.contains("vpn2", case=False, na=False)]
vpn3= df[df["condition"].str.contains("vpn3", case=False, na=False)]

websites = sorted(df["website"].unique())
x = np.arange(len(websites))

def get_rtts(group):
    return np.array([
        group[group["website"] == site]["rtt"].mean()
        for site in websites
    ], dtype=float)

baseline_rtts = get_rtts(baseline)
vpn1_rtts = get_rtts(vpn1)
vpn2_rtts = get_rtts(vpn2)
vpn3_rtts= get_rtts(vpn3)

def plot_with_gap_dotted(x, y, label, color):
    # Plot real (solid)
    plt.plot(x, y, color=color, marker="o", linestyle="-", linewidth=2, label=label)

    # Add dotted lines where data is missing
    for i in range(len(y) - 1):
        left = y[i]
        right = y[i+1]

        # One of them missing → dotted line
        if np.isnan(left) or np.isnan(right):
            # Find previous real point
            prev_idx = i
            while prev_idx >= 0 and np.isnan(y[prev_idx]):
                prev_idx -= 1

            # Find next real point
            next_idx = i + 1
            while next_idx < len(y) and np.isnan(y[next_idx]):
                next_idx += 1

            if prev_idx >= 0 and next_idx < len(y):
                # Draw dotted line between real points around the missing region
                plt.plot(
                    [x[prev_idx], x[next_idx]],
                    [y[prev_idx], y[next_idx]],
                    linestyle="dotted",
                    color=color,
                    linewidth=2,
                    alpha=0.7
                )

plt.figure(figsize=(22, 7))

plot_with_gap_dotted(x, baseline_rtts, "Baseline", "blue")
plot_with_gap_dotted(x, vpn1_rtts, "VPN1 (Argentina)", "orange")
plot_with_gap_dotted(x, vpn2_rtts, "VPN2 (NewyYork)", "red")
plot_with_gap_dotted(x, vpn3_rtts, "VPN3(france)", "purple")


plt.xticks(x, websites, rotation=90)
plt.ylabel("RTT (ms)")
plt.title("Baseline vs VPN1 vs VPN2 RTT Comparison (Dotted = Missing Segment Interpolation)")
plt.grid(alpha=0.3)
plt.legend()

os.makedirs("plots", exist_ok=True)
plt.tight_layout()
plt.savefig("plots/rtt_multiline_dotted_correct.png", dpi=300)

print("SAVED → plots/rtt_multiline_dotted_correct.png")

