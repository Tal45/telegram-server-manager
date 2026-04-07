import subprocess
from datetime import datetime

def get_network_info():
    """Retrieves network status using nmcli."""
    try:
        # Get active connection and device
        active_conn = subprocess.check_output(
            ["nmcli", "-t", "-f", "NAME,DEVICE,TYPE", "connection", "show", "--active"],
            universal_newlines=True
        ).strip().split('\n')

        # Filter for wifi or ethernet
        if not active_conn or not active_conn[0]:
            return "No active connection."

        # Find the first non-loopback, relevant connection (prefer wifi)
        target_conn = None
        for line in active_conn:
            name, device, conn_type = line.split(':')
            if conn_type in ['802-11-wireless', 'wifi', '802-3-ethernet', 'ethernet']:
                target_conn = (name, device)
                break
        
        if not target_conn:
            return "No suitable active network connection found."

        ssid, device = target_conn

        # Get IP address
        ip_output = subprocess.check_output(
            ["nmcli", "-t", "-f", "IP4.ADDRESS", "dev", "show", device],
            universal_newlines=True
        ).strip()
        
        # IP output format: IP4.ADDRESS[1]:192.168.1.87/24
        ip_address = "Unknown"
        for line in ip_output.split('\n'):
            if "IP4.ADDRESS" in line:
                ip_address = line.split(':')[1].split('/')[0]
                break

        # Get Hostname
        hostname = subprocess.check_output(["hostname"], universal_newlines=True).strip()

        # Get Current Time
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

        return f"{hostname}\nSSID: {ssid}\nIP: {ip_address}\nTime: {timestamp}"

    except Exception as e:
        return f"Error retrieving network info: {str(e)}"
