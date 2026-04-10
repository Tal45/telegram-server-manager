import subprocess
from datetime import datetime

def get_ip_address():
    """Retrieves the IP address using nmcli."""
    try:
        # Get active connection and device
        active_conn = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "connection", "show", "--active"],
            universal_newlines=True
        ).strip().split('\n')

        # Find the first non-loopback, relevant connection (prefer wifi)
        target_device = None
        for line in active_conn:
            parts = line.split(':')
            if len(parts) < 3: continue
            _, device, conn_type = parts
            if conn_type in ['802-11-wireless', 'wifi', '802-3-ethernet', 'ethernet']:
                target_device = device
                break
        
        if not target_device:
            return None

        # Get IP address
        ip_output = subprocess.check_output(
            ["nmcli", "-t", "-f", "IP4.ADDRESS", "dev", "show", target_device],
            universal_newlines=True
        ).strip()
        
        for line in ip_output.split('\n'):
            if "IP4.ADDRESS" in line:
                return line.split(':')[1].split('/')[0]
        return None
    except Exception:
        return None

def get_network_info():
    """Retrieves network status using nmcli."""
    try:
        # Get active connection and device (needed for SSID)
        active_conn = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "connection", "show", "--active"],
            universal_newlines=True
        ).strip().split('\n')

        target_conn = None
        for line in active_conn:
            parts = line.split(':')
            if len(parts) < 3: continue
            name, device, conn_type = parts
            if conn_type in ['802-11-wireless', 'wifi', '802-3-ethernet', 'ethernet']:
                target_conn = (name, device)
                break
        
        if not target_conn:
            return "No suitable active network connection found."

        ssid, _ = target_conn
        ip_address = get_ip_address() or "Unknown"
        hostname = subprocess.check_output(["hostname"], universal_newlines=True).strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        return f"{hostname}\nSSID: {ssid}\nIP: {ip_address}\nTime: {timestamp}"

    except Exception as e:
        return f"Error retrieving network info: {str(e)}"
