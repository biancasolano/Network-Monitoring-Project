"""
collector.py
--------------
This script measures the average RTT (round-trip time) to a large batch
of websites under a given network condition (e.g., baseline, VPN1, VPN2).
It automates large-scale latency collection and stores results in a clean
CSV format for later analysis.

This script is typically used together with:
    • vpn_on / vpn_off tests
    • plotting scripts for multi-host RTT comparison
    • multi-condition RTT analysis (baseline vs VPN)
"""

import subprocess
import csv
import time

# -----------------------------------------------------------
# LIST OF WEBSITES TO TEST
# -----------------------------------------------------------
# Contains a mix of:
#   • Major tech companies
#   • Media sites
#   • Universities
#   • Government domains
#   • International and global sites
#
# This provides diversity in geography, routing paths, CDN locations,
# and DNS behavior — important when comparing VPN conditions.
# -----------------------------------------------------------
websites = [
    # --- Original batch ---
    "google.com", "cloudflare.com", "amazon.com", "apple.com", "microsoft.com",
    "facebook.com", "twitter.com", "reddit.com", "youtube.com", "netflix.com",
    "unm.edu", "mit.edu", "stanford.edu", "berkeley.edu", "arizona.edu",
    "utexas.edu", "gov.uk", "gov.in", "nic.jp", "korea.kr",
    "bund.de", "canada.ca", "australia.gov.au", "gov.za", "gov.br",
    "gov.sg", "gov.cn", "nasa.gov", "who.int", "wikipedia.org",

    # --- New batch to reach 100 ---
    "tesla.com", "spacex.com", "openai.com", "ibm.com", "oracle.com",
    "spotify.com", "twitch.tv", "linkedin.com", "bing.com", "weather.com",
    "nytimes.com", "cnn.com", "bbc.co.uk", "aljazeera.com", "foxnews.com",
    "hulu.com", "disneyplus.com", "paramountplus.com", "primevideo.com",

    "purdue.edu", "umich.edu", "harvard.edu", "princeton.edu", "yale.edu",
    "caltech.edu", "gatech.edu", "cornell.edu", "columbia.edu", "brown.edu",

    "gov.fr", "gov.es", "gov.it", "gov.au", "gov.jp",
    "gov.kr", "gov.tw", "gov.hk", "gov.sa", "gov.ae",

    "baidu.com", "qq.com", "bilibili.com", "weibo.com", "taobao.com",
    "jd.com", "alibaba.com", "rakuten.co.jp", "naver.com", "yandex.ru",

    "zara.com", "nike.com", "adidas.com", "shein.com", "etsy.com",
    "ebay.com", "costco.com", "walmart.com", "target.com", "bestbuy.com",

    "roblox.com", "fortnite.com", "epicgames.com", "steamcommunity.com", "playstation.com",
    "xbox.com", "nintendo.com", "riotgames.com", "leagueoflegends.com",
    "valorant.com"
]

# -----------------------------------------------------------
# OUTPUT CSV CONFIGURATION
# -----------------------------------------------------------
output_csv = "csv_files/combined_rtt_clean.csv"

# Label used to differentiate test conditions.
# Examples:
#   "baseline"        – no VPN
#   "VPN1(france)"    – connected to France endpoint
#   "VPN2(newyork)"   – connected to U.S. East endpoint
condition = "VPN1(france)"

# -----------------------------------------------------------
# MAIN RTT COLLECTION LOOP
# -----------------------------------------------------------
with open(output_csv, "a", newline="") as f:
    writer = csv.writer(f)
    # Write header for readability
    writer.writerow(["website", "rtt", "condition"])

    for site in websites:
        print(f"Pinging {site}...")

        result = subprocess.run(
            ["python3", "ping3", site],
            capture_output=True,
            text=True
        )

        rtts = []
        for line in result.stdout.splitlines():
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    rtts.append(float(parts[1]))
                except:
                    pass

        if rtts:
            avg_rtt = sum(rtts) / len(rtts)
            writer.writerow([site, avg_rtt, condition])
        else:
            print(f"WARNING: No RTT recorded for {site}")
            writer.writerow([site, "NaN", condition])

        time.sleep(0.2)

print("DONE: Clean RTT saved.")

