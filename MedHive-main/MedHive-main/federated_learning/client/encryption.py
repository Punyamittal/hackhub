import os
import io
import logging
from typing import Dict, Tuple, Any, Union
import torch
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Encryption")

# Default encryption key path
KEY_PATH = os.path.expanduser("~/.federated_learning/encryption_key")
SALT_PATH = os.path.expanduser("~/.federated_learning/salt")

def _ensure_key_directory():
    """Ensure the directory for encryption keys exists."""
    key_dir = os.path.dirname(KEY_PATH)
    if not os.path.exists(key_dir):
        os.makedirs(key_dir, exist_ok=True, mode=0o700)  # Secure permissions

def _generate_key(password: str = None) -> bytes:
    """Generate an encryption key, optionally from a password."""
    if password:
        # Load or create salt
        if os.path.exists(SALT_PATH):
            with open(SALT_PATH, "rb") as f:
                salt = f.read()
        else:
            salt = os.urandom(16)
            _ensure_key_directory()
            with open(SALT_PATH, "wb") as f:
                f.write(salt)
            os.chmod(SALT_PATH, 0o600)  # Secure permissions
        
        # Derive key from password and salt
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    else:
        # Generate a random key
        key = Fernet.generate_key()
    
    return key

def _get_encryption_key() -> bytes:
    """Get the encryption key, creating it if it doesn't exist."""
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, "rb") as f:
            key = f.read()
    else:
        key = _generate_key()
        _ensure_key_directory()
        with open(KEY_PATH, "wb") as f:
            f.write(key)
        os.chmod(KEY_PATH, 0o600)  # Secure permissions
    
    return key

def _get_cipher() -> Fernet:
    """Get the encryption cipher."""
    key = _get_encryption_key()
    return Fernet(key)

def encrypt_model(model_path: str) -> str:
    """
    Encrypt a PyTorch model file.
    
    Args:
        model_path: Path to the PyTorch model file (.pt or .pth)
        
    Returns:
        Path to the encrypted model file
    """
    try:
        # Load the model
        model_data = torch.load(model_path)
        
        # Serialize the model to a byte buffer
        buffer = io.BytesIO()
        torch.save(model_data, buffer)
        model_bytes = buffer.getvalue()
        
        # Encrypt the serialized model
        cipher = _get_cipher()
        encrypted_data = cipher.encrypt(model_bytes)
        
        # Save the encrypted model
        encrypted_path = f"{model_path}.encrypted"
        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)
        
        logger.info(f"Model encrypted and saved to {encrypted_path}")
        return encrypted_path
    except Exception as e:
        logger.error(f"Error encrypting model: {str(e)}")
        return ""

def decrypt_model(encrypted_path: str) -> str:
    """
    Decrypt an encrypted PyTorch model file.
    
    Args:
        encrypted_path: Path to the encrypted model file
        
    Returns:
        Path to the decrypted model file
    """
    try:
        # Read the encrypted data
        with open(encrypted_path, "rb") as f:
            encrypted_data = f.read()
        
        # Decrypt the data
        cipher = _get_cipher()
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Load the model from the decrypted data
        buffer = io.BytesIO(decrypted_data)
        model_data = torch.load(buffer)
        
        # Save the decrypted model
        decrypted_path = encrypted_path.replace(".encrypted", "")
        torch.save(model_data, decrypted_path)
        
        logger.info(f"Model decrypted and saved to {decrypted_path}")
        return decrypted_path
    except Exception as e:
        logger.error(f"Error decrypting model: {str(e)}")
        return ""

def encrypt_tensor(tensor: torch.Tensor) -> Tuple[bytes, Dict[str, Any]]:
    """
    Encrypt a PyTorch tensor.
    
    Args:
        tensor: The tensor to encrypt
        
    Returns:
        Tuple containing the encrypted data and metadata
    """
    try:
        # Serialize the tensor to a byte buffer
        buffer = io.BytesIO()
        torch.save(tensor, buffer)
        tensor_bytes = buffer.getvalue()
        
        # Encrypt the serialized tensor
        cipher = _get_cipher()
        encrypted_data = cipher.encrypt(tensor_bytes)
        
        # Prepare metadata
        metadata = {
            "shape": list(tensor.shape),
            "dtype": str(tensor.dtype),
            "device": str(tensor.device),
        }
        
        return encrypted_data, metadata
    except Exception as e:
        logger.error(f"Error encrypting tensor: {str(e)}")
        return None, {}

def decrypt_tensor(encrypted_data: bytes, metadata: Dict[str, Any]) -> Union[torch.Tensor, None]:
    """
    Decrypt an encrypted PyTorch tensor.
    
    Args:
        encrypted_data: The encrypted tensor data
        metadata: Metadata about the tensor
        
    Returns:
        The decrypted tensor, or None if decryption failed
    """
    try:
        # Decrypt the data
        cipher = _get_cipher()
        decrypted_data = cipher.decrypt(encrypted_data)
        
        # Load the tensor from the decrypted data
        buffer = io.BytesIO(decrypted_data)
        tensor = torch.load(buffer)
        
        return tensor
    except Exception as e:
        logger.error(f"Error decrypting tensor: {str(e)}")
        return None

def encrypt_gradients(gradients: Dict[str, torch.Tensor]) -> Dict[str, Any]:
    """
    Encrypt model gradients (dictionary of tensors).
    
    Args:
        gradients: Dictionary mapping parameter names to gradients
        
    Returns:
        Dictionary with encrypted gradients and metadata
    """
    encrypted_gradients = {}
    
    for name, grad in gradients.items():
        if grad is not None:
            encrypted_data, metadata = encrypt_tensor(grad)
            if encrypted_data is not None:
                encrypted_gradients[name] = {
                    "data": base64.b64encode(encrypted_data).decode('utf-8'),
                    "metadata": metadata
                }
    
    logger.info(f"Encrypted {len(encrypted_gradients)} gradient tensors")
    return encrypted_gradients

def decrypt_gradients(encrypted_gradients: Dict[str, Any]) -> Dict[str, torch.Tensor]:
    """
    Decrypt model gradients.
    
    Args:
        encrypted_gradients: Dictionary with encrypted gradients and metadata
        
    Returns:
        Dictionary mapping parameter names to decrypted gradients
    """
    gradients = {}
    
    for name, encrypted_item in encrypted_gradients.items():
        encrypted_data = base64.b64decode(encrypted_item["data"])
        metadata = encrypted_item["metadata"]
        grad = decrypt_tensor(encrypted_data, metadata)
        if grad is not None:
            gradients[name] = grad
    
    logger.info(f"Decrypted {len(gradients)} gradient tensors")
    return gradients

if __name__ == "__main__":
    # Simple test
    import argparse
    
    parser = argparse.ArgumentParser(description="Test model encryption/decryption")
    parser.add_argument("--model_path", type=str, required=True, help="Path to model file")
    parser.add_argument("--operation", type=str, choices=["encrypt", "decrypt"], required=True, help="Operation to perform")
    
    args = parser.parse_args()
    
    if args.operation == "encrypt":
        encrypted_path = encrypt_model(args.model_path)
        print(f"Encrypted model saved to: {encrypted_path}")
    else:
        decrypted_path = decrypt_model(args.model_path)
        print(f"Decrypted model saved to: {decrypted_path}")
