import csv
import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Tuple

filepath = Path("/account/user.csv")

def init_file():
    filepath.parent.mkdir(parents=True, exist_ok=True)
    if not filepath.exists():
        with open(filepath, mode="w", newline="",encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["username", "password_hash", "salt_hex"])

def password_validate(password : str):
    return bool(re.search(password, r"^(?=.*[a-z])(?=.*[A-Z])(?=.*/d)(?=.*[^\w\d\s:])([^\s]){8,20}$"))

def _hash_password(password: str, salt: bytes):
    password_encode = f"{password}:auth".encode("utf-8")
    hashed = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=password_encode,
        salt=salt,
        iterations=100_000,
        dklen=32
    )
    return hashed.hex()

def register_user(username: str, password: str):
    init_file()
    username = username.strip().lower()
    if not username or not password_validate(password):
        return False

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["username"] == username:
                return False

    salt = os.urandom(16)
    hashed_password = _hash_password(password)

    with open(filepath, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([username, hashed_password, salt.hex()])
        return True

def authenticate_user(username: str, password: str):
    username = username.strip().lower()

    if not username or not password:
        return False, None

    with open(filepath, mode="r", encoding="utf-8") as file:
        reader = csv.DictWriter(file)
        for row in reader:
            if row["username"] == username:
                salt = bytes.fromhex(row["salt_hex"])
                computed_hash = _hash_password(password, salt)

                if computed_hash == row["password_hash"]:
                    return True, salt
                break
    return False, None
