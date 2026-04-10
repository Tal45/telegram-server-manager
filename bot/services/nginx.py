import subprocess
from services.network import get_ip_address

def get_nginx_status():
    """Returns the status of the nginx service."""
    try:
        result = subprocess.run(["rc-service", "nginx", "status"], capture_output=True, text=True)
        if "started" in result.stdout.lower():
            return "started"
        if "stopped" in result.stdout.lower():
            return "stopped"
        return f"Unknown status: {result.stdout.strip()}"
    except Exception as e:
        return f"Error checking status: {str(e)}"

def start_nginx():
    """Starts the nginx service."""
    try:
        subprocess.run(["rc-service", "nginx", "start"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        return f"Failed to start: {e.stderr.strip()}"
    except Exception as e:
        return str(e)

def stop_nginx():
    """Stops the nginx service."""
    try:
        subprocess.run(["rc-service", "nginx", "stop"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        return f"Failed to stop: {e.stderr.strip()}"
    except Exception as e:
        return str(e)

def get_local_ip():
    """Gets the local IP address."""
    ip = get_ip_address()
    return ip if ip else "127.0.0.1"
