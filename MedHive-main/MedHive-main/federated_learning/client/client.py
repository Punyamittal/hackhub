import os
import json
import requests
import logging
from typing import Dict, Any, Optional
import torch

from federated_learning.client.encryption import encrypt_model, decrypt_model
from federated_learning.client.local_training import train_model

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Client")

class FederatedClient:
    def __init__(
        self, 
        client_id: str,
        server_url: str,
        data_path: str,
        model_type: str,
        api_key: Optional[str] = None
    ):
        """
        Initialize a federated learning client.
        
        Args:
            client_id: Unique identifier for this client
            server_url: URL of the federated learning server
            data_path: Path to local training data
            model_type: Type of model to train (e.g., 'pneumonia', 'ecg_analysis')
            api_key: Optional API key for authentication
        """
        self.client_id = client_id
        self.server_url = server_url
        self.data_path = data_path
        self.model_type = model_type
        self.api_key = api_key
        self.current_round_id = None
        self.participant_id = None
        
        logger.info(f"Initialized client {client_id} for model type {model_type}")
    
    def register(self) -> bool:
        """Register this client with the server."""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.server_url}/api/clients/register",
                json={
                    "client_id": self.client_id,
                    "model_type": self.model_type,
                    "device_info": self._get_device_info()
                },
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Successfully registered with server: {data}")
                return True
            else:
                logger.error(f"Failed to register with server: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            return False
    
    def check_for_rounds(self) -> Dict[str, Any]:
        """Check for available federated learning rounds."""
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.server_url}/api/federated-learning/available-rounds",
                params={"model_type": self.model_type},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Available rounds: {data}")
                return data
            else:
                logger.error(f"Failed to get available rounds: {response.text}")
                return {}
        except Exception as e:
            logger.error(f"Error checking for rounds: {str(e)}")
            return {}
    
    def join_round(self, round_id: int) -> bool:
        """Join a specific federated learning round."""
        try:
            headers = self._get_headers()
            response = requests.post(
                f"{self.server_url}/api/federated-learning/rounds/{round_id}/join",
                json={"client_id": self.client_id},
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.current_round_id = round_id
                self.participant_id = data.get("participant_id")
                logger.info(f"Successfully joined round {round_id} as participant {self.participant_id}")
                return True
            else:
                logger.error(f"Failed to join round {round_id}: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error joining round: {str(e)}")
            return False
    
    def download_global_model(self) -> str:
        """Download the current global model from the server."""
        if not self.current_round_id:
            logger.error("No active round to download model for")
            return ""
        
        try:
            headers = self._get_headers()
            response = requests.get(
                f"{self.server_url}/api/federated-learning/rounds/{self.current_round_id}/model",
                headers=headers
            )
            
            if response.status_code == 200:
                # Save the encrypted model
                encrypted_model_path = f"models/encrypted_global_{self.current_round_id}.pt"
                os.makedirs(os.path.dirname(encrypted_model_path), exist_ok=True)
                
                with open(encrypted_model_path, "wb") as f:
                    f.write(response.content)
                
                # Decrypt the model
                model_path = decrypt_model(encrypted_model_path)
                logger.info(f"Successfully downloaded and decrypted global model to {model_path}")
                return model_path
            else:
                logger.error(f"Failed to download global model: {response.text}")
                return ""
        except Exception as e:
            logger.error(f"Error downloading global model: {str(e)}")
            return ""
    
    def train_local_model(self, global_model_path: str) -> str:
        """Train a local model using the global model as a starting point."""
        if not global_model_path:
            logger.error("No global model provided for training")
            return ""
        
        try:
            local_model_path = train_model(
                global_model_path=global_model_path,
                data_path=self.data_path,
                model_type=self.model_type,
                round_id=self.current_round_id,
                client_id=self.client_id
            )
            
            logger.info(f"Successfully trained local model: {local_model_path}")
            return local_model_path
        except Exception as e:
            logger.error(f"Error training local model: {str(e)}")
            return ""
    
    def upload_local_model(self, local_model_path: str) -> bool:
        """Upload the locally trained model to the server."""
        if not self.current_round_id or not self.participant_id:
            logger.error("No active round or participant ID")
            return False
        
        if not local_model_path or not os.path.exists(local_model_path):
            logger.error(f"Local model not found at {local_model_path}")
            return False
        
        try:
            # Encrypt the model before sending
            encrypted_model_path = encrypt_model(local_model_path)
            
            headers = self._get_headers()
            headers.pop('Content-Type', None)  # Let requests set the correct content type for multipart
            
            # Calculate metrics on local validation data
            metrics = self._calculate_metrics(local_model_path)
            
            with open(encrypted_model_path, "rb") as f:
                files = {"model_file": f}
                data = {"training_metrics": json.dumps(metrics)}
                
                response = requests.post(
                    f"{self.server_url}/api/federated-learning/participants/{self.participant_id}/upload",
                    files=files,
                    data=data,
                    headers=headers
                )
            
            if response.status_code == 200:
                logger.info(f"Successfully uploaded local model for round {self.current_round_id}")
                return True
            else:
                logger.error(f"Failed to upload local model: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error uploading local model: {str(e)}")
            return False
    
    def complete_round(self) -> bool:
        """Mark the current round as completed for this client."""
        if not self.current_round_id or not self.participant_id:
            logger.error("No active round or participant ID")
            return False
        
        try:
            headers = self._get_headers()
            response = requests.put(
                f"{self.server_url}/api/federated-learning/participants/{self.participant_id}/complete",
                headers=headers
            )
            
            if response.status_code == 200:
                logger.info(f"Successfully completed round {self.current_round_id}")
                self.current_round_id = None
                self.participant_id = None
                return True
            else:
                logger.error(f"Failed to complete round: {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error completing round: {str(e)}")
            return False
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Content-Type": "application/json"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def _get_device_info(self) -> Dict[str, Any]:
        """Get information about the client's device."""
        device_info = {
            "os": os.name,
            "python_version": os.sys.version,
            "has_gpu": torch.cuda.is_available(),
        }
        
        if torch.cuda.is_available():
            device_info["gpu_name"] = torch.cuda.get_device_name(0)
            device_info["gpu_count"] = torch.cuda.device_count()
        
        return device_info
    
    def _calculate_metrics(self, model_path: str) -> Dict[str, float]:
        """Calculate model performance metrics on local validation data."""
        # This would normally load the model and evaluate it on validation data
        # For simplicity, we're just returning some dummy metrics
        return {
            "accuracy": 0.85,
            "loss": 0.23,
            "f1_score": 0.82,
            "precision": 0.86,
            "recall": 0.79
        }


def run_federated_client():
    """Main function to run a federated learning client."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Federated Learning Client")
    parser.add_argument("--client_id", type=str, required=True, help="Unique client ID")
    parser.add_argument("--server_url", type=str, required=True, help="FL server URL")
    parser.add_argument("--data_path", type=str, required=True, help="Path to local data")
    parser.add_argument("--model_type", type=str, required=True, help="Type of model to train")
    parser.add_argument("--api_key", type=str, help="API key for authentication")
    
    args = parser.parse_args()
    
    client = FederatedClient(
        client_id=args.client_id,
        server_url=args.server_url,
        data_path=args.data_path,
        model_type=args.model_type,
        api_key=args.api_key
    )
    
    # Register with the server
    if not client.register():
        logger.error("Failed to register with server. Exiting.")
        return
    
    # Main client loop
    while True:
        try:
            # Check for available rounds
            rounds = client.check_for_rounds()
            
            if not rounds or "rounds" not in rounds or not rounds["rounds"]:
                logger.info("No rounds currently available. Sleeping...")
                import time
                time.sleep(60)  # Check again in 1 minute
                continue
            
            # Join the first available round
            round_id = rounds["rounds"][0]["id"]
            if not client.join_round(round_id):
                logger.error(f"Failed to join round {round_id}. Trying again later.")
                time.sleep(30)
                continue
            
            # Download the global model
            global_model_path = client.download_global_model()
            if not global_model_path:
                logger.error("Failed to download global model. Aborting round.")
                time.sleep(30)
                continue
            
            # Train the local model
            local_model_path = client.train_local_model(global_model_path)
            if not local_model_path:
                logger.error("Failed to train local model. Aborting round.")
                time.sleep(30)
                continue
            
            # Upload the local model
            if not client.upload_local_model(local_model_path):
                logger.error("Failed to upload local model. Aborting round.")
                time.sleep(30)
                continue
            
            # Complete the round
            client.complete_round()
            logger.info(f"Successfully completed federated learning round {round_id}")
            
            # Sleep before checking for new rounds
            time.sleep(60)
            
        except KeyboardInterrupt:
            logger.info("Interrupted by user. Shutting down client.")
            break
        except Exception as e:
            logger.error(f"Unexpected error in client main loop: {str(e)}")
            time.sleep(60)

if __name__ == "__main__":
    run_federated_client()
