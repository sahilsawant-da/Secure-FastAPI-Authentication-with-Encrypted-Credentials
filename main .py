from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv

app = FastAPI()

# Load environment variables
load_dotenv()

# Get the secret key 
secret_key = os.getenv("SECRET_KEY")

# If the secret key is not present, generate one
if not secret_key:
    def generate_key() -> str:
        return Fernet.generate_key().decode()

    secret_key = generate_key()
    print(f"Generated SECRET_KEY: {secret_key}")
    print("Please add the above key to your .env file as: SECRET_KEY=<generated_key>")

try:
    fernet = Fernet(secret_key.encode())
except Exception as e:
    raise ValueError(f"Error creating Fernet key: {str(e)}")

#  generate a new key
@app.get("/generate-key")
async def generate_key_endpoint():
    try:
        key = Fernet.generate_key().decode()
        return {"generated_key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Key generation failed: {str(e)}")

# encryption and decryption functions
def encrypt_data(data: str) -> str:
    encrypted = fernet.encrypt(data.encode())
    return encrypted.decode()

def decrypt_data(encrypted_data: str) -> str:
    decrypted = fernet.decrypt(encrypted_data.encode())
    return decrypted.decode()

# Define request and response models
class UserData(BaseModel):
    email: str
    password: str

class EncryptedData(BaseModel):
    encrypted_email: str
    encrypted_password: str

@app.post("/encrypt", response_model=EncryptedData)
async def encrypt_endpoint(user_data: UserData):
    try:
        encrypted_email = encrypt_data(user_data.email)
        encrypted_password = encrypt_data(user_data.password)
        return {
            "encrypted_email": encrypted_email,
            "encrypted_password": encrypted_password
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Encryption failed: {str(e)}")

@app.post("/decrypt", response_model=UserData)
async def decrypt_endpoint(encrypted_data: EncryptedData):
    try:
        decrypted_email = decrypt_data(encrypted_data.encrypted_email)
        decrypted_password = decrypt_data(encrypted_data.encrypted_password)
        return {
            "email": decrypted_email,
            "password": decrypted_password
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
