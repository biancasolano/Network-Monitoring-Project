#!/usr/bin/env python3

"""
plot_rtt.py
-----------
This script loads RTT (round-trip time) measurements from one or more CSV files
and generates a variety of visualizations including:

    • Line plots       – RTT evolution over time
    • Scatter plots    – RTT variance at each sample
    • Histograms       – RTT distribution
    • VPN comparisons  – Baseline RTT vs VPN RTT overlay
    • Multi-file plots – Compare many RTT sources at once

This tool is used as the final stage of our network monitoring pipeline:
    (1) traffic_generator.py creates RTT logs,
    (2) tcpdump records the raw packets,
    (3) analyze_ping.py extracts timing from the capture, and
    (4) plot_rtt.py visualizes everything for analysis.

The script accepts paths to one baseline CSV and optional additional CSVs
(for VPN trials or multi-condition comparisons).
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt


# Helper: load a ping CSV safely
def load_ping_csv(path):
    if not os.path.exists(path):
        print(f"[WARN] File not found: {path}")
        return None

    try:
        df = pd.read_csv(path)
        # Expect a column representing round-trip time/latency
        if "status" in df.columns:
            df = df[df["status"].str.lower().isin(["ok", "ok-reply", "no-reply", "sent"])]
        rtt_column = None
        preferred_order = ("rtt", "latency", "ping")
        for name in preferred_order:
            for c in df.columns:
                if name in c.lower():
                    rtt_column = c
                    break
            if rtt_column:
                break

        # If  still didn't find anything, fall back to the first numeric column
        if rtt_column is None:
            numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
            rtt_column = numeric_cols[0] if numeric_cols else None

        if rtt_column is None:
            raise ValueError("No RTT/latency column found in CSV.")
        series = pd.to_numeric(df[rtt_column], errors="coerce").dropna()
        if series.empty:
            raise ValueError(f"No numeric RTT/latency values in column '{rtt_column}'.")
        return series
    except Exception as e:
        print(f"[ERROR] Failed to parse {path}: {e}")
        return None


# Plot: Time series line plot

def plot_line(rtt_series, title, outfile):
    plt.figure(figsize=(10, 4))
    plt.plot(rtt_series.index, rtt_series.values)
    plt.xlabel("Sample Number")
    plt.ylabel("RTT (ms)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()



# Plot: Scatter plot
def plot_scatter(rtt_series, title, outfile):
    plt.figure(figsize=(10, 4))
    plt.scatter(rtt_series.index, rtt_series.values)
    plt.xlabel("Sample Number")
    plt.ylabel("RTT (ms)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


# Plot: Histogram

def plot_histogram(rtt_series, title, outfile):
    plt.figure(figsize=(10, 4))
    plt.hist(rtt_series.values, bins=30)
    plt.xlabel("RTT (ms)")
    plt.ylabel("Frequency")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()



# Plot: VPN vs Normal RTT Overlay Comparison

def plot_comparison(normal_rtt, vpn_rtt, normal_label, vpn_label, outfile):
    plt.figure(figsize=(10, 4))
    plt.plot(normal_rtt.index, normal_rtt.values, label=normal_label)
    plt.plot(vpn_rtt.index, vpn_rtt.values, label=vpn_label)
    plt.xlabel("Sample Number")
    plt.ylabel("RTT (ms)")
    plt.title("RTT Comparison: Normal vs VPN")
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


# Main

def plot_multi(series_map, title, outfile):
    if not series_map or len(series_map) < 2:
        return
    plt.figure(figsize=(10, 4))
    for label, s in series_map.items():
        plt.plot(s.index, s.values, label=label)
    plt.xlabel("Sample Number")
    plt.ylabel("RTT (ms)")
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.savefig(outfile)
    plt.close()


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 plot_rtt.py <ping_csv> [<vpn_ping_csv>|<extra_csv>...]")
        sys.exit(1)

    paths = sys.argv[1:]
    normal_path = paths[0]
    vpn_path = paths[1] if len(paths) == 2 else None
    outdir = os.environ.get("PLOTS_DIR", "plots")

    normal_rtt = load_ping_csv(normal_path)
    if normal_rtt is None:
        sys.exit(1)

    base_name = os.path.splitext(os.path.basename(normal_path))[0]

    if not os.path.exists(outdir):
        os.makedirs(outdir)

    plot_line(normal_rtt, f"RTT Over Time: {base_name}", f"{outdir}/{base_name}_line.png")
    plot_scatter(normal_rtt, f"RTT Scatter: {base_name}", f"{outdir}/{base_name}_scatter.png")
    plot_histogram(normal_rtt, f"RTT Histogram: {base_name}", f"{outdir}/{base_name}_hist.png")

    if vpn_path and len(paths) == 2:
        vpn_rtt = load_ping_csv(vpn_path)
        if vpn_rtt is not None:
            vpn_name = os.path.splitext(os.path.basename(vpn_path))[0]
            plot_comparison(
                normal_rtt,
                vpn_rtt,
                base_name,
                vpn_name,
                f"{outdir}/{base_name}_vs_{vpn_name}_comparison.png"
            )
            print(f"[OK] VPN comparison plot saved to {outdir}/{base_name}_vs_{vpn_name}_comparison.png")

    if len(paths) > 2:
        series_map = {}
        for p in paths:
            s = load_ping_csv(p)
            if s is not None and not s.empty:
                series_map[os.path.splitext(os.path.basename(p))[0]] = s
        if len(series_map) >= 2:
            multi_name = os.path.splitext(os.path.basename(paths[0]))[0] + "_multi"
            plot_multi(series_map, "RTT Comparison", f"{outdir}/{multi_name}_comparison.png")
            print(f"[OK] Multi comparison plot saved to {outdir}/{multi_name}_comparison.png")

    print(f"[OK] RTT plots generated successfully in {outdir}.")


if __name__ == "__main__":
    main()
