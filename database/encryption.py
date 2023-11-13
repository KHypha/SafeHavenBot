# encryption.py

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from base64 import urlsafe_b64encode, urlsafe_b64decode
import sqlite3

def derive_key(password):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b'some_salt',  # Use a unique salt for each user
        iterations=100000,
        backend=default_backend()
    )
    key = kdf.derive(password.encode())
    return key

# Function to encrypt text
def encrypt_text(text, key):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(text.encode()) + encryptor.finalize()
    return urlsafe_b64encode(ciphertext)

# Function to decrypt text
def decrypt_text(ciphertext, key):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.ECB(), backend=backend)
    decryptor = cipher.decryptor()
    decrypted_text = decryptor.update(urlsafe_b64decode(ciphertext)) + decryptor.finalize()
    return decrypted_text.decode()

# Function to save encrypted API credentials
def save_encrypted_credentials(user_id, api_key, api_secret):
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()

    # Encrypt the API key and secret
    key = derive_key('some_password')  # Use a password unique to each user
    encrypted_api_key = encrypt_text(api_key, key)
    encrypted_api_secret = encrypt_text(api_secret, key)

    # Save the encrypted credentials
    cursor.execute('REPLACE INTO user_credentials (user_id, api_key, api_secret) VALUES (?, ?, ?)',
                   (user_id, encrypted_api_key, encrypted_api_secret))
    conn.commit()
    conn.close()

# Function to get decrypted API credentials
def get_decrypted_credentials(user_id):
    conn = sqlite3.connect('credentials.db')
    cursor = conn.cursor()
    cursor.execute("SELECT api_key, api_secret FROM user_credentials WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        api_key, api_secret = result
        key = derive_key('some_password')  # Use the same password used for encryption
        decrypted_api_key = decrypt_text(api_key, key)
        decrypted_api_secret = decrypt_text(api_secret, key)
        return decrypted_api_key, decrypted_api_secret
    else:
        return None, None
