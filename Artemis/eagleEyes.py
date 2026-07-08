import socket
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime


class EagleEyes:
    def __init__(self, port: int = 554, timeout: float = 3.0, log_file: str = "results/log.txt"):
        self.port = port
        self.timeout = timeout
        self.log_file = Path(log_file)
        self.ensure_results_dir()

    def ensure_results_dir(self) -> None:
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def build_request(self, target: str, command: str = "OPTIONS", path: str = "", cseq: int = 1) -> bytes:
        """
        Build an RTSP request.
        Example:
            OPTIONS rtsp://10.1.10.9:554/stream1 RTSP/1.0
            CSeq: 1
            Host: 10.1.10.9
        """
        uri = f"rtsp://{target}:{self.port}{path}"
        request = (
            f"{command} {uri} RTSP/1.0\r\n"
            f"CSeq: {cseq}\r\n"
            f"Host: {target}\r\n"
            f"\r\n"
        )
        return request.encode()

    def is_rtsp_open(self, ip: str, timeout: float = 0.5) -> str | None:
        """
        Check whether port 554 is open on a target IP.
        Returns the IP if open, otherwise None.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((ip, self.port)) == 0:
                    return ip
        except Exception:
            return None
        return None

    def send_request(self, target: str, command: str = "OPTIONS", path: str = "", cseq: int = 1) -> str | None:
        """
        Send one RTSP request and return the raw server response.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                print(f"Connecting to {target}:{self.port}...")
                s.connect((target, self.port))

                message = self.build_request(target, command=command, path=path, cseq=cseq)
                s.sendall(message)

                print(f"Sent:\n{message.decode().strip()}\n")

                data = s.recv(4096).decode(errors="ignore")
                print(f"Received:\n{data.strip()}\n")
                return data

        except ConnectionRefusedError:
            print(f"[-] Connection refused by {target}")
        except socket.timeout:
            print(f"[-] Connection timed out for {target}")
        except Exception as e:
            print(f"[-] Error communicating with {target}: {e}")

        return None

    def parse_response(self, response: str) -> dict:
        """
        Parse an RTSP response into a structured dictionary.
        """
        parsed = {
            "status_line": "",
            "status_code": None,
            "headers": {}
        }

        if not response:
            return parsed

        lines = response.splitlines()
        if not lines:
            return parsed

        parsed["status_line"] = lines[0].strip()

        parts = parsed["status_line"].split()
        if len(parts) >= 2 and parts[1].isdigit():
            parsed["status_code"] = int(parts[1])

        for line in lines[1:]:
            if ":" in line:
                key, value = line.split(":", 1)
                parsed["headers"][key.strip()] = value.strip()

        return parsed

    def log_result(self, info: str) -> None:
        """
        Append data to the log file.
        """
        try:
            with open(self.log_file, "a", encoding="utf-8") as outfile:
                outfile.write(f"[{datetime.now()}]\n")
                outfile.write(info)
                outfile.write("\n" + ("-" * 60) + "\n")
        except Exception as e:
            print(f"[-] Logging error: {e}")

    def scan_subnet(self, net_prefix: str) -> list[str]:
        """
        Scan a /24 subnet prefix like '10.1.10'
        """
        ips = [f"{net_prefix}.{i}" for i in range(1, 255)]
        print(f"Scanning {net_prefix}.0/24 for RTSP on port {self.port}...")

        with ThreadPoolExecutor(max_workers=50) as executor:
            results = list(executor.map(self.is_rtsp_open, ips))

        found_devices = [ip for ip in results if ip]

        print(f"\nScan complete. Found {len(found_devices)} device(s).")
        for ip in found_devices:
            print(f" [+] RTSP found at {ip}")

        return found_devices

    def probe_options(self, target: str) -> dict | None:
        """
        Send an OPTIONS request and return the parsed response.
        """
        response = self.send_request(target, command="OPTIONS")
        if response:
            parsed = self.parse_response(response)
            self.log_result(f"TARGET: {target}\nCOMMAND: OPTIONS\n{response}")
            return parsed
        return None

    def probe_describe(self, target: str, path: str) -> dict | None:
        """
        Send a DESCRIBE request to a specific RTSP path.
        """
        response = self.send_request(target, command="DESCRIBE", path=path)
        if response:
            parsed = self.parse_response(response)
            self.log_result(f"TARGET: {target}\nCOMMAND: DESCRIBE\nPATH: {path}\n{response}")
            return parsed
        return None

    def probe_common_paths(self, target: str) -> list[dict]:
        """
        Try a small list of common RTSP paths and collect results.
        """
        common_paths = [
            "",
            "/stream1",
            "/stream",
            "/live",
            "/h264",
            "/Streaming/Channels/101",
            "/cam/realmonitor",
        ]

        findings = []

        for i, path in enumerate(common_paths, start=1):
            print(f"[*] Probing {target} path: {path or '/'}")
            response = self.send_request(target, command="DESCRIBE", path=path, cseq=i)
            if response:
                parsed = self.parse_response(response)
                findings.append({
                    "target": target,
                    "path": path or "/",
                    "status_code": parsed["status_code"],
                    "status_line": parsed["status_line"],
                    "headers": parsed["headers"],
                })
                self.log_result(
                    f"TARGET: {target}\nCOMMAND: DESCRIBE\nPATH: {path or '/'}\n{response}"
                )

        return findings


def main() -> None:
    scanner = EagleEyes()

    mode = input("Choose mode ([1] single target, [2] subnet scan): ").strip()

    if mode == "1":
        target = input("Enter target IP address: ").strip()

        print("\n--- OPTIONS Probe ---")
        options_result = scanner.probe_options(target)
        if options_result:
            print(options_result)

        print("\n--- Common Path DESCRIBE Probes ---")
        describe_results = scanner.probe_common_paths(target)
        for result in describe_results:
            print(result)

    elif mode == "2":
        prefix = input("Enter network prefix (example 10.1.10): ").strip()
        targets = scanner.scan_subnet(prefix)

        for target in targets:
            print(f"\n=== Probing {target} ===")
            scanner.probe_options(target)

    else:
        print("Invalid mode selected.")


if __name__ == "__main__":
    main()



