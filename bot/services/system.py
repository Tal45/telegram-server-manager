import os
import subprocess

def shutdown_system():
    """Shuts down the server using poweroff."""
    try:
        # Use poweroff as requested
        subprocess.run(["poweroff"], check=True)
        return True
    except Exception as e:
        return f"Error during shutdown: {str(e)}"
