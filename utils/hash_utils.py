# utils/hash_utils.py
import hashlib

def get_file_hash(file_path):
    """Generate SHA-256 hash of the file content."""
    with open(file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()
