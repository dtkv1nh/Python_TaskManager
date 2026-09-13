import csv
import hashlib
import os
import re
from pathlib import Path
from typing import Optional, Tuple

# Đường dẫn file users.csv
USERS_FILE = Path("account/users.csv")


def init_users_file() -> None:
    """Tạo thư mục account và file users.csv với header chuẩn nếu chưa tồn tại."""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not USERS_FILE.exists():
        with open(USERS_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password_hash", "salt_hex"])


def validate_password_strength(password: str) -> bool:
    """Kiểm tra độ mạnh mật khẩu bằng Regex.

    Mật khẩu phải có tối thiểu 8 ký tự, bao gồm chữ hoa, chữ thường, số và ký tự đặc biệt.
    """
    pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
    return bool(re.match(pattern, password))


def _hash_password_for_auth(password: str, salt: bytes) -> str:
    """Hàm private: Băm mật khẩu dùng cho mục đích XÁC THỰC DÂN NHẬP.

    Sử dụng kỹ thuật Domain Separation (thêm ':auth' scope) và 100.000 vòng lặp PBKDF2.
    """
    # Ghép suffix định danh ngữ cảnh để phân tách hoàn toàn với module mã hóa
    auth_scoped_password = f"{password}:auth".encode("utf-8")
    
    hashed = hashlib.pbkdf2_hmac(
        hash_name="sha256",
        password=auth_scoped_password,
        salt=salt,
        iterations=100_000,
        dklen=32
    )
    return hashed.hex()


def register_user(username: str, password: str) -> bool:
    """Xử lý đăng ký tài khoản mới.

    :param username: Tên đăng nhập
    :param password: Mật khẩu chưa băm
    :return: True nếu đăng ký thành công, False nếu thất bại/trùng username/mật khẩu yếu
    """
    init_users_file()
    username = username.strip().lower()

    if not username or not validate_password_strength(password):
        return False

    # Kiểm tra username đã tồn tại chưa
    with open(USERS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                return False

    # Sinh Salt ngẫu nhiên 16 bytes và băm mật khẩu
    salt = os.urandom(16)
    password_hash = _hash_password_for_auth(password, salt)

    # Lưu thông tin người dùng mới vào CSV
    with open(USERS_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, password_hash, salt.hex()])

    return True


def authenticate_user(username: str, password: str) -> Tuple[bool, Optional[bytes]]:
    """Xác thực người dùng khi đăng nhập.

    :param username: Tên đăng nhập
    :param password: Mật khẩu người dùng nhập
    :return: Tuple (True, salt_bytes) nếu đăng nhập đúng; ngược lại (False, None)
    """
    init_users_file()
    username = username.strip().lower()

    if not username or not password:
        return False, None

    with open(USERS_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["username"] == username:
                # Đổi chuỗi salt hex trong CSV ngược lại thành bytes
                salt = bytes.fromhex(row["salt_hex"])
                computed_hash = _hash_password_for_auth(password, salt)

                # So sánh chuỗi hash tính toán được với chuỗi hash trong CSV
                if computed_hash == row["password_hash"]:
                    return True, salt
                break

    return False, None