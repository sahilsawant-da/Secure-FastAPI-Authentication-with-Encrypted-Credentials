from cryptography.fernet import Fernet

key = Fernet.generate_key()
print(f"SECRET_KEY={key.decode()}")
