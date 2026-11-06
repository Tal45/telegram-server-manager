import re
import subprocess
import time
from datetime import datetime

def get_current_connection():
    """
    Returns (name, device) of the current active wireless or wired connection.
    """
    try:
        active_conn = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "connection", "show", "--active"],
            universal_newlines=True,
            timeout=10
        ).strip().split("\n")

        for line in active_conn:
            parts = line.split(":")
            if len(parts) < 3:
                continue
            name = parts[0].replace(r"\:", ":")
            device = parts[1]
            conn_type = parts[2]
            if conn_type in ["802-11-wireless", "wifi", "802-3-ethernet", "ethernet"]:
                return name, device
        return None, None
    except Exception:
        return None, None

def get_ip_address():
    """Retrieves the IP address using nmcli."""
    try:
        _, target_device = get_current_connection()
        if not target_device:
            return None

        ip_output = subprocess.check_output(
            ["nmcli", "-t", "-f", "IP4.ADDRESS", "dev", "show", target_device],
            universal_newlines=True,
            timeout=10
        ).strip()
        
        for line in ip_output.split("\n"):
            if "IP4.ADDRESS" in line:
                return line.split(":")[1].split("/")[0]
        return None
    except Exception:
        return None

def get_network_info():
    """Retrieves network status using nmcli."""
    try:
        ssid, _ = get_current_connection()
        if not ssid:
            return "No suitable active network connection found."

        ip_address = get_ip_address() or "Unknown"
        hostname = subprocess.check_output(["hostname"], universal_newlines=True).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        return f"{hostname}\nSSID: {ssid}\nIP: {ip_address}\nTime: {timestamp}"

    except Exception as e:
        return f"Error retrieving network info: {str(e)}"

def scan_wifi():
    """
    Scans for available Wi-Fi networks using nmcli.
    Returns (success: bool, networks: list[dict] | error: str).
    Each dict contains: in_use (bool), ssid (str), signal (int), security (str).
    """
    try:
        # Attempt rescan first
        cmd = ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list", "--rescan", "yes"]
        try:
            output = subprocess.check_output(cmd, universal_newlines=True, timeout=15)
        except Exception:
            # Fall back without rescan flag if busy
            output = subprocess.check_output(
                ["nmcli", "-t", "-f", "IN-USE,SSID,SIGNAL,SECURITY", "dev", "wifi", "list"],
                universal_newlines=True,
                timeout=15
            )

        networks_by_ssid = {}
        for raw_line in output.strip().split("\n"):
            line = raw_line.strip()
            if not line:
                continue

            # Split on unescaped colons per nmcli terse mode specification
            fields = re.split(r"(?<!\\):", line)
            if len(fields) < 4:
                continue

            in_use = (fields[0].strip() == "*")
            raw_ssid = fields[1].replace(r"\:", ":").strip()
            raw_signal = fields[2].strip()
            security = fields[3].replace(r"\:", ":").strip() or "Open"

            if not raw_ssid or raw_ssid == "--":
                continue

            try:
                signal = int(raw_signal)
            except ValueError:
                signal = 0

            if raw_ssid not in networks_by_ssid:
                networks_by_ssid[raw_ssid] = {
                    "in_use": in_use,
                    "ssid": raw_ssid,
                    "signal": signal,
                    "security": security
                }
            else:
                if in_use:
                    networks_by_ssid[raw_ssid]["in_use"] = True
                if signal > networks_by_ssid[raw_ssid]["signal"]:
                    networks_by_ssid[raw_ssid]["signal"] = signal
                    networks_by_ssid[raw_ssid]["security"] = security

        sorted_networks = sorted(
            networks_by_ssid.values(),
            key=lambda x: (1 if x["in_use"] else 0, x["signal"]),
            reverse=True
        )
        return True, sorted_networks

    except subprocess.TimeoutExpired:
        return False, "Wi-Fi scan timed out."
    except Exception as e:
        return False, f"Error scanning Wi-Fi: {str(e)}"

def get_saved_wifi_connections():
    """
    Returns a list of saved Wi-Fi connection profile names.
    """
    try:
        output = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show"],
            universal_newlines=True,
            timeout=10
        )
        saved = []
        for line in output.strip().split("\n"):
            parts = line.strip().split(":")
            if len(parts) >= 2:
                conn_type = parts[-1]
                conn_name = ":".join(parts[:-1]).replace(r"\:", ":").strip()
                if conn_type in ["802-11-wireless", "wifi"]:
                    saved.append(conn_name)
        return saved
    except Exception:
        return []

def connect_wifi(ssid: str, password: str = None) -> tuple:
    """
    Connects to a Wi-Fi network using nmcli.
    If already saved and password is not supplied, brings up the saved connection.
    Otherwise initiates a connection using dev wifi connect.
    Returns (success: bool, message: str).
    """
    try:
        saved_conns = get_saved_wifi_connections()

        if ssid in saved_conns and not password:
            cmd = ["nmcli", "connection", "up", "id", ssid]
        elif password:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
        else:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            time.sleep(3)
            new_ip = get_ip_address() or "Acquiring IP..."
            return True, f"Connected to '{ssid}' successfully.\nIP: {new_ip}"
        else:
            err = result.stderr.strip() or result.stdout.strip()
            return False, f"Failed to connect to '{ssid}': {err}"

    except subprocess.TimeoutExpired:
        return False, f"Connection attempt to '{ssid}' timed out."
    except Exception as e:
        return False, f"Error connecting to '{ssid}': {str(e)}"
