import os
import base64
import logging
from config import SSH_USER

logger = logging.getLogger(__name__)

SUPPORTED_KEY_TYPES = {
    "ssh-rsa",
    "ssh-dss",
    "ssh-ed25519",
    "ecdsa-sha2-nistp256",
    "ecdsa-sha2-nistp384",
    "ecdsa-sha2-nistp521",
    "sk-ssh-ed25519@openssh.com",
    "sk-ecdsa-sha2-nistp256@openssh.com",
}

def parse_and_validate_key(raw_key: str):
    """
    Validates an SSH public key string.
    Returns (is_valid, key_type, key_data, comment, error_message).
    """
    clean_key = raw_key.strip()
    if not clean_key:
        return False, None, None, None, "Empty key provided."

    # A key might contain options before the key type, or just key_type key_data comment
    parts = clean_key.split()
    if len(parts) < 2:
        return False, None, None, None, "Invalid key format. Expected at least type and key data."

    key_type = None
    key_data = None
    comment = ""

    # Check if the first part is a known key type
    if parts[0] in SUPPORTED_KEY_TYPES or parts[0].startswith("ssh-") or parts[0].startswith("ecdsa-"):
        key_type = parts[0]
        key_data = parts[1]
        if len(parts) > 2:
            comment = " ".join(parts[2:])
    elif len(parts) >= 3 and (parts[1] in SUPPORTED_KEY_TYPES or parts[1].startswith("ssh-") or parts[1].startswith("ecdsa-")):
        # Leading options present
        key_type = parts[1]
        key_data = parts[2]
        if len(parts) > 3:
            comment = " ".join(parts[3:])
    else:
        return False, None, None, None, f"Unsupported key type: {parts[0]}"

    # Validate base64 encoding of key_data
    try:
        base64.b64decode(key_data, validate=True)
    except Exception:
        return False, None, None, None, "Invalid base64 payload in public key."

    return True, key_type, key_data, comment, None

def get_authorized_keys_path(username: str = None) -> str:
    """Returns the authorized_keys path for a given username."""
    user = username or SSH_USER
    if user == "root":
        return "/root/.ssh/authorized_keys"
    return f"/home/{user}/.ssh/authorized_keys"

def add_authorized_key(raw_key: str, username: str = None) -> tuple:
    """
    Adds a validated SSH public key to the user's authorized_keys file.
    Returns (success: bool, message: str).
    """
    user = username or SSH_USER
    is_valid, key_type, key_data, comment, error = parse_and_validate_key(raw_key)
    if not is_valid:
        return False, f"Key validation error: {error}"

    target_file = get_authorized_keys_path(user)
    ssh_dir = os.path.dirname(target_file)

    try:
        # Ensure .ssh directory exists with 700 permissions
        if not os.path.exists(ssh_dir):
            os.makedirs(ssh_dir, mode=0o700, exist_ok=True)
        else:
            try:
                os.chmod(ssh_dir, 0o700)
            except OSError:
                pass

        # Check if key is already present
        clean_entry = f"{key_type} {key_data}"
        if comment:
            clean_entry += f" {comment}"

        if os.path.exists(target_file):
            with open(target_file, "r", encoding="utf-8", errors="ignore") as f:
                existing_lines = f.readlines()
                for line in existing_lines:
                    line_parts = line.strip().split()
                    if len(line_parts) >= 2:
                        # Compare key type and base64 data to detect duplicate
                        if line_parts[0] == key_type and line_parts[1] == key_data:
                            return True, f"Key is already present in authorized_keys for user '{user}'."

            # Ensure newline before appending if existing file does not end with one
            needs_leading_newline = False
            with open(target_file, "rb") as f:
                f.seek(0, os.SEEK_END)
                if f.tell() > 0:
                    f.seek(-1, os.SEEK_END)
                    if f.read(1) != b"\n":
                        needs_leading_newline = True

            with open(target_file, "a", encoding="utf-8") as f:
                if needs_leading_newline:
                    f.write("\n")
                f.write(f"{clean_entry}\n")
        else:
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(f"{clean_entry}\n")

        # Set 600 permissions on authorized_keys
        try:
            os.chmod(target_file, 0o600)
        except OSError:
            pass

        # Adjust ownership if running on POSIX with appropriate privileges
        try:
            import pwd
            user_info = pwd.getpwnam(user)
            os.chown(ssh_dir, user_info.pw_uid, user_info.pw_gid)
            os.chown(target_file, user_info.pw_uid, user_info.pw_gid)
        except Exception:
            pass

        comment_info = f"\nComment: {comment}" if comment else ""
        return True, f"SSH key successfully added for user '{user}'.\nType: {key_type}{comment_info}"

    except Exception as e:
        logger.error(f"Failed to add SSH key: {e}")
        return False, f"Failed to save key: {str(e)}"
