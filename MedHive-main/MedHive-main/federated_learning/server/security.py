import os
import logging
import json
import hashlib
import hmac
import base64
import secrets
from typing import Dict, Any, Optional, Tuple, List, Union
import time
from datetime import datetime, timedelta
import jwt
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.serialization import (
    load_pem_private_key,
    load_pem_public_key,
    Encoding,
    PublicFormat,
    PrivateFormat,
    NoEncryption
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Security")

# Default keys directory
KEYS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keys")
PRIVATE_KEY_PATH = os.path.join(KEYS_DIR, "private_key.pem")
PUBLIC_KEY_PATH = os.path.join(KEYS_DIR, "public_key.pem")
JWT_SECRET_PATH = os.path.join(KEYS_DIR, "jwt_secret.key")
ENCRYPTION_KEY_PATH = os.path.join(KEYS_DIR, "encryption.key")
SALT_PATH = os.path.join(KEYS_DIR, "salt")

class SecurityManager:
    """
    Manages security aspects of the federated learning server:
    - Authentication and authorization
    - Secure model encryption/decryption
    - Signature verification for models
    - Differential privacy (optional)
    """
    
    def __init__(self, generate_keys: bool = False):
        """
        Initialize the security manager.
        
        Args:
            generate_keys: Whether to generate new keys if they don't exist
        """
        # Ensure keys directory exists
        if not os.path.exists(KEYS_DIR):
            os.makedirs(KEYS_DIR, exist_ok=True, mode=0o700)  # Secure permissions
        
        self.keys_initialized = self._check_keys_exist()
        
        if not self.keys_initialized and generate_keys:
            self._generate_all_keys()
            self.keys_initialized = True
        
        if self.keys_initialized:
            self._load_keys()
        else:
            logger.warning("Security keys not initialized. Some functions will be unavailable.")
    
    def _check_keys_exist(self) -> bool:
        """Check if all required keys exist."""
        return (
            os.path.exists(PRIVATE_KEY_PATH) and
            os.path.exists(PUBLIC_KEY_PATH) and
            os.path.exists(JWT_SECRET_PATH) and
            os.path.exists(ENCRYPTION_KEY_PATH) and
            os.path.exists(SALT_PATH)
        )
    
    def _generate_all_keys(self) -> None:
        """Generate all security keys."""
        self._generate_rsa_keypair()
        self._generate_jwt_secret()
        self._generate_encryption_key()
        logger.info("All security keys generated successfully")
    
    def _load_keys(self) -> None:
        """Load keys from files."""
        try:
            # Load RSA keys
            with open(PRIVATE_KEY_PATH, "rb") as f:
                self.private_key = load_pem_private_key(f.read(), password=None)
            
            with open(PUBLIC_KEY_PATH, "rb") as f:
                self.public_key = load_pem_public_key(f.read())
            
            # Load JWT secret
            with open(JWT_SECRET_PATH, "rb") as f:
                self.jwt_secret = f.read()
            
            # Load encryption key
            with open(ENCRYPTION_KEY_PATH, "rb") as f:
                self.encryption_key = f.read()
            
            # Create Fernet cipher
            self.cipher = Fernet(self.encryption_key)
            
            logger.info("Security keys loaded successfully")
        except Exception as e:
            logger.error(f"Error loading security keys: {str(e)}")
            self.keys_initialized = False
    
    def _generate_rsa_keypair(self) -> None:
        """Generate RSA key pair for signing and verification."""
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        
        public_key = private_key.public_key()
        
        # Save private key
        private_pem = private_key.private_bytes(
            encoding=Encoding.PEM,
            format=PrivateFormat.PKCS8,
            encryption_algorithm=NoEncryption()
        )
        
        with open(PRIVATE_KEY_PATH, "wb") as f:
            f.write(private_pem)
        os.chmod(PRIVATE_KEY_PATH, 0o600)  # Secure permissions
        
        # Save public key
        public_pem = public_key.public_bytes(
            encoding=Encoding.PEM,
            format=PublicFormat.SubjectPublicKeyInfo
        )
        
        with open(PUBLIC_KEY_PATH, "wb") as f:
            f.write(public_pem)
        
        logger.info("RSA keypair generated")
    
    def _generate_jwt_secret(self) -> None:
        """Generate a secret for JWT token signing."""
        secret = secrets.token_bytes(32)
        
        with open(JWT_SECRET_PATH, "wb") as f:
            f.write(secret)
        os.chmod(JWT_SECRET_PATH, 0o600)  # Secure permissions
        
        logger.info("JWT secret generated")
    
    def _generate_encryption_key(self) -> None:
        """Generate encryption key and salt."""
        # Generate salt
        salt = os.urandom(16)
        with open(SALT_PATH, "wb") as f:
            f.write(salt)
        os.chmod(SALT_PATH, 0o600)  # Secure permissions
        
        # Generate Fernet key
        key = Fernet.generate_key()
        with open(ENCRYPTION_KEY_PATH, "wb") as f:
            f.write(key)
        os.chmod(ENCRYPTION_KEY_PATH, 0o600)  # Secure permissions
        
        logger.info("Encryption key and salt generated")
    
    def generate_token(self, user_id: str, role: str, expiry_days: int = 7) -> str:
        """
        Generate a JWT token for authentication.
        
        Args:
            user_id: User ID
            role: User role (e.g., 'admin', 'contributor')
            expiry_days: Token validity in days
            
        Returns:
            JWT token string
        """
        if not self.keys_initialized:
            raise ValueError("Security keys not initialized")
        
        payload = {
            "sub": user_id,
            "role": role,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=expiry_days)
        }
        
        token = jwt.encode(payload, self.jwt_secret, algorithm="HS256")
        return token
    
    def verify_token(self, token: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Verify a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Tuple of (is_valid, payload)
        """
        if not self.keys_initialized:
            return False, {"error": "Security keys not initialized"}
        
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
            return True, payload
        except jwt.ExpiredSignatureError:
            return False, {"error": "Token expired"}
        except jwt.InvalidTokenError as e:
            return False, {"error": f"Invalid token: {str(e)}"}
    
    def sign_data(self, data: bytes) -> bytes:
        """
        Sign data using RSA private key.
        
        Args:
            data: Data to sign
            
        Returns:
            Signature bytes
        """
        if not self.keys_initialized:
            raise ValueError("Security keys not initialized")
        
        signature = self.private_key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        
        return signature
    
    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """
        Verify a signature using RSA public key.
        
        Args:
            data: Original data
            signature: Signature to verify
            
        Returns:
            True if signature is valid
        """
        if not self.keys_initialized:
            return False
        
        try:
            self.public_key.verify(
                signature,
                data,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
    
    def encrypt_data(self, data: bytes) -> bytes:
        """
        Encrypt data using Fernet symmetric encryption.
        
        Args:
            data: Data to encrypt
            
        Returns:
            Encrypted data
        """
        if not self.keys_initialized:
            raise ValueError("Security keys not initialized")
        
        return self.cipher.encrypt(data)
    
    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data using Fernet symmetric encryption.
        
        Args:
            encrypted_data: Data to decrypt
            
        Returns:
            Decrypted data
        """
        if not self.keys_initialized:
            raise ValueError("Security keys not initialized")
        
        return self.cipher.decrypt(encrypted_data)
    
    def secure_hash(self, data: bytes) -> str:
        """
        Create a secure hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            Hexadecimal hash string
        """
        h = hashlib.sha256()
        h.update(data)
        return h.hexdigest()
    
    def verify_client(self, client_id: str, client_signature: bytes, challenge: bytes) -> bool:
        """
        Verify a client's identity using a signature challenge.
        
        Args:
            client_id: Client identifier
            client_signature: Client's signature of the challenge
            challenge: Challenge data that was sent to the client
            
        Returns:
            True if verification is successful
        """
        # In a real implementation, we would look up the client's public key
        # For now, just return True for testing
        return True

    def generate_client_challenge(self) -> Tuple[bytes, str]:
        """
        Generate a challenge for client authentication.
        
        Returns:
            Tuple of (challenge_bytes, challenge_id)
        """
        challenge = secrets.token_bytes(32)
        challenge_id = secrets.token_hex(8)
        
        # In a real implementation, we would store this challenge
        # with an expiry time to verify the response later
        
        return challenge, challenge_id
    
    def apply_differential_privacy(self, model_update: Dict[str, Any], epsilon: float = 1.0) -> Dict[str, Any]:
        """
        Apply differential privacy to model updates to protect privacy.
        
        Args:
            model_update: Model update parameters
            epsilon: Privacy parameter (lower means more privacy)
            
        Returns:
            Model update with differential privacy applied
        """
        # This is a placeholder implementation
        # A real implementation would add calibrated noise to the model parameters
        # based on sensitivity analysis and the privacy budget (epsilon)
        
        import numpy as np
        
        dp_update = {}
        for key, value in model_update.items():
            if isinstance(value, list) or isinstance(value, np.ndarray):
                # Add Laplace noise
                sensitivity = np.max(np.abs(value)) * 0.01  # Estimate sensitivity
                scale = sensitivity / epsilon
                noise = np.random.laplace(0, scale, size=np.array(value).shape)
                dp_update[key] = np.array(value) + noise
            else:
                dp_update[key] = value
        
        return dp_update


def generate_server_keys():
    """Utility function to generate all server security keys."""
    security_manager = SecurityManager(generate_keys=True)
    if security_manager.keys_initialized:
        logger.info("Server security keys generated successfully")
    else:
        logger.error("Failed to generate server security keys")


if __name__ == "__main__":
    # Generate keys if run directly
    import argparse
    
    parser = argparse.ArgumentParser(description="Federated Learning Security Management")
    parser.add_argument("--generate-keys", action="store_true", help="Generate new security keys")
    
    args = parser.parse_args()
    
    if args.generate_keys:
        generate_server_keys()
    else:
        # Test the security manager
        security_manager = SecurityManager()
        
        if not security_manager.keys_initialized:
            print("Security keys not initialized. Generating new keys...")
            security_manager = SecurityManager(generate_keys=True)
        
        # Test token generation and verification
        token = security_manager.generate_token("test_user", "contributor")
        print(f"Generated token: {token}")
        
        valid, payload = security_manager.verify_token(token)
        print(f"Token verification: {valid}")
        if valid:
            print(f"Token payload: {payload}")
        
        # Test encryption
        test_data = b"This is a test message for encryption"
        encrypted = security_manager.encrypt_data(test_data)
        print(f"Encrypted data: {base64.b64encode(encrypted).decode()}")
        
        decrypted = security_manager.decrypt_data(encrypted)
        print(f"Decrypted data: {decrypted.decode()}")
        
        # Test signing
        signature = security_manager.sign_data(test_data)
        print(f"Signature: {base64.b64encode(signature).decode()}")
        
        is_valid = security_manager.verify_signature(test_data, signature)
        print(f"Signature verification: {is_valid}")
