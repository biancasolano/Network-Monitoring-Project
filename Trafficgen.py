#!/usr/bin/env python3
"""FEATURES
- Generates test traffic:modes: ICMP, HTTP, DNS, TCP, and UDP.
- Logs each probe to CSV
- Optional live packet capture to a .pcap file using tcpdump
- refuses non-local targets unless --allow-external
-Tune sampling: --samples, --interval, --timeout, UDP payload size, and reply-wait.

CLI USAGE:
  --mode {icmp,http,dns,tcp,udp}
  --target HOST/IP          (default: 127.0.0.1)
  --port INT                (TCP/UDP, default: 9999)
  --samples INT             (default: 10)
  --interval FLOAT seconds  (default: 1.0)
  --timeout INT ms          (default: 1000)
  --output FILE.csv         (default: traffic_log.csv)
  --allow-external          (permit non-local targets)
  --udp-payload-size INT    (default: 128)
  --udp-await-reply         (wait for UDP response path)
  --dns-name NAME           (default: example.com)
  --pcap-out FILE.pcap      (enable live capture)
  --iface IFACE             (override interface for capture)
  --capture-filter BPF      (default: "icmp or icmp6")"""
import argparse, csv, time, socket, sys, ipaddress, subprocess, os, signal, shutil

try:
    from ping3 import ping
except Exception:
    ping = None
try:
    import requests
except Exception:
    requests = None
try:
    import dns.resolver, dns.message, dns.query
except Exception:
    dns = None

def is_local(addr):
    try:
        if addr.lower() in ("localhost", "::1", "127.0.0.1"):
            return True
        ip = ipaddress.ip_address(socket.gethostbyname(addr))
        return ip.is_private or ip.is_loopback
    except Exception:
        return False

def looks_like_ip(s):
    try:
        ipaddress.ip_address(s)
        return True
    except Exception:
        return False

def now():
    return time.time()

def icmp_mode(target, timeout):
    if not ping:
        return ("error", "ping3 not installed")
    try:
        rtt = ping(target, timeout=timeout / 1000)
    except PermissionError:
        return ("error", "ICMP needs sudo on macOS")
    return ("ok", rtt * 1000) if rtt else ("lost", None)

def http_mode(target, timeout):
    if not requests:
        return ("error", "requests not installed")
    url = target if target.startswith("http") else "http://" + target
    start = time.time()
    try:
        r = requests.head(url, timeout=timeout / 1000, allow_redirects=True)
        if 200 <= r.status_code < 400:
            return ("ok", (time.time() - start) * 1000)
        return ("error", f"HTTP {r.status_code}")
    except Exception as e:
        return ("error", str(e))

def dns_mode(target, timeout, qname):
    if dns:
        try:
            q = dns.message.make_query(qname, dns.rdatatype.A)
            start = time.time()
            if is_local(target) or looks_like_ip(target):
                dns.query.udp(q, target, timeout=timeout / 1000)
            else:
                res = dns.resolver.Resolver()
                res.resolve(qname, "A", lifetime=timeout / 1000)
            return ("ok", (time.time() - start) * 1000)
        except Exception as e:
            return ("error", str(e))
    start = time.time()
    try:
        out = subprocess.run(
            ["nslookup", qname, target],
            capture_output=True,
            text=True,
            timeout=max(1, timeout / 1000),
        )
        rtt = (time.time() - start) * 1000
        return ("ok", rtt) if out.returncode == 0 else ("error", out.stderr or out.stdout)
    except Exception as e:
        return ("error", str(e))

def tcp_mode(target, port, timeout):
    start = time.time()
    try:
        with socket.create_connection((target, port), timeout=timeout / 1000):
            return ("ok", (time.time() - start) * 1000)
    except Exception as e:
        return ("error", str(e))

def udp_mode(target, port, payload, timeout, wait=False):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(max(0.01, timeout / 1000))
    try:
        start = time.time()
        s.sendto(payload, (target, port))
        if wait:
            try:
                s.recvfrom(65535)
                return ("ok-reply", (time.time() - start) * 1000)
            except socket.timeout:
                return ("no-reply", None)
        return ("sent", None)
    except Exception as e:
        return ("error", str(e))
    finally:
        s.close()

def log(writer, seq, mode, status, val):
    writer.writerow([f"{now():.3f}", seq, mode, status, val])

def default_iface(target):
    #when local, Wi-Fi usually en0
    return "lo0" if is_local(target) else "en0"

class PcapCapture:
    def __init__(self, iface, out_path, flt):
        self.iface = iface
        self.out_path = out_path
        self.filter = flt
        self.proc = None

    def start(self):
        if not shutil.which("tcpdump"):
            print("Warning: tcpdump not found", file=sys.stderr)
            return
        cmd = ["tcpdump", "-i", self.iface, "-s", "0", "-U", "-w", self.out_path, self.filter]
        # Needs root on macOS; if not sudo, tcpdump will likely fail
        try:
            self.proc = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                preexec_fn=os.setsid
            )
            # ensure file is created
            time.sleep(0.3)
        except Exception as e:
            print(f"Failed to start tcpdump: {e}", file=sys.stderr)
            self.proc = None

    def stop(self):
        if not self.proc:
            return
        try:
            os.killpg(os.getpgid(self.proc.pid), signal.SIGINT)  # flush and close pcap
            try:
                self.proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgid(self.proc.pid), signal.SIGKILL)
        except Exception:
            pass
        self.proc = None

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=["icmp", "http", "dns", "tcp", "udp"], required=True)
    p.add_argument("--target", default="127.0.0.1")
    p.add_argument("--port", type=int, default=9999)
    p.add_argument("--samples", type=int, default=10)
    p.add_argument("--interval", type=float, default=1)
    p.add_argument("--timeout", type=int, default=1000)
    p.add_argument("--output", default="csv_files/traffic_log.csv")
    p.add_argument("--allow-external", action="store_true")
    p.add_argument("--udp-payload-size", type=int, default=128)
    p.add_argument("--udp-await-reply", action="store_true")
    p.add_argument("--dns-name", default="example.com")
    # New: pcap capture options
    p.add_argument("--pcap-out", default=None, help="write live capture to this pcap")
    p.add_argument("--iface", default=None, help="interface for tcpdump (default: lo0 if local else en0)")
    p.add_argument("--capture-filter", default="icmp or icmp6", help="tcpdump filter")
    args = p.parse_args()

    if not args.allow_external and not is_local(args.target):
        print(f"Refusing external address {args.target}")
        sys.exit(1)

    # live capture if requested
    cap = None
    if args.pcap_out:
        iface = args.iface or default_iface(args.target)
        cap = PcapCapture(iface, args.pcap_out, args.capture_filter)
        cap.start()

    try:
        with open(args.output, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp", "seq", "mode", "status", "latency_ms_or_info"])
            for i in range(args.samples):
                try:
                    if args.mode == "icmp":
                        st, v = icmp_mode(args.target, args.timeout)
                    elif args.mode == "http":
                        st, v = http_mode(args.target, args.timeout)
                    elif args.mode == "dns":
                        st, v = dns_mode(args.target, args.timeout, args.dns_name)
                    elif args.mode == "tcp":
                        st, v = tcp_mode(args.target, args.port, args.timeout)
                    elif args.mode == "udp":
                        data = b"A" * max(1, args.udp_payload_size)
                        st, v = udp_mode(args.target, args.port, data, args.timeout, wait=args.udp_await_reply)
                    else:
                        st, v = ("bad-mode", "")
                    log(w, i, args.mode, st, f"{v:.3f}" if isinstance(v, float) else v)
                except Exception as e:
                    log(w, i, args.mode, "exception", str(e))
                f.flush()
                if i < args.samples - 1:
                    time.sleep(args.interval)
    finally:
        if cap:
            cap.stop()

    print(f"Done. Output: {args.output}")
    if args.pcap_out:
        print(f"PCAP saved: {args.pcap_out}")

if __name__ == "__main__":
    main()

