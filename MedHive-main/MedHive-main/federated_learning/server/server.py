import os
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple, Union
import threading
import queue
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import torch

from federated_learning.server.security import SecurityManager
from federated_learning.server.aggregator import ModelAggregator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Server")

class FederatedLearningServer:
    """
    Main server class for coordinating federated learning rounds.
    Handles client communication, model distribution, aggregation, and evaluation.
    """
    
    def __init__(
        self,
        models_dir: str = "models",
        rounds_dir: str = "rounds",
        init_security: bool = True,
        worker_threads: int = 5
    ):
        """
        Initialize the federated learning server.
        
        Args:
            models_dir: Directory for storing global models
            rounds_dir: Directory for storing round information
            init_security: Whether to initialize security
            worker_threads: Number of worker threads for handling requests
        """
        self.models_dir = models_dir
        self.rounds_dir = rounds_dir
        self.worker_threads = worker_threads
        
        # Initialize directories
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.rounds_dir, exist_ok=True)
        
        # Initialize security
        if init_security:
            self.security = SecurityManager()
            if not self.security.keys_initialized:
                logger.warning("Security keys not initialized. Generating new keys...")
                self.security = SecurityManager(generate_keys=True)
        else:
            self.security = None
            logger.warning("Security not initialized. Running in insecure mode.")
        
        # Data structures for tracking clients and rounds
        self.registered_clients = {}  # client_id -> client info
        self.active_rounds = {}       # round_id -> round info
        self.client_rounds = {}       # client_id -> [round_id, ...]
        
        # Thread synchronization
        self.request_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.executor = ThreadPoolExecutor(max_workers=worker_threads)
        
        # Start worker threads
        self.workers = []
        for _ in range(worker_threads):
            worker = threading.Thread(target=self._worker_loop)
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        
        logger.info("Federated Learning Server initialized")
    
    def register_client(self, client_id: str, model_type: str, device_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register a new client with the server.
        
        Args:
            client_id: Unique identifier for the client
            model_type: Type of model the client is interested in
            device_info: Information about the client's device
            
        Returns:
            Registration result
        """
        if client_id in self.registered_clients:
            logger.info(f"Client {client_id} already registered, updating information")
        else:
            logger.info(f"Registering new client: {client_id}")
        
        # Store client information
        self.registered_clients[client_id] = {
            "id": client_id,
            "model_type": model_type,
            "device_info": device_info,
            "registered_at": time.time(),
            "last_active": time.time(),
            "rounds_participated": 0,
            "status": "active"
        }
        
        return {
            "status": "success",
            "client_id": client_id,
            "message": "Client registered successfully"
        }
    
    def create_round(
        self,
        model_id: int,
        model_type: str,
        round_number: int,
        min_clients: int = 2,
        max_clients: int = 10,
        aggregation_strategy: str = "fedavg",
        client_selection_strategy: str = "random",
        round_timeout: int = 3600,  # 1 hour
        hyperparameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a new federated learning round.
        
        Args:
            model_id: ID of the model
            model_type: Type of the model
            round_number: Round number
            min_clients: Minimum number of clients required
            max_clients: Maximum number of clients to include
            aggregation_strategy: Strategy for aggregating models
            client_selection_strategy: Strategy for selecting clients
            round_timeout: Timeout for the round in seconds
            hyperparameters: Additional hyperparameters for the round
            
        Returns:
            Round creation result
        """
        # Generate a unique round ID
        round_id = str(uuid.uuid4())
        
        # Create round information
        round_info = {
            "id": round_id,
            "model_id": model_id,
            "model_type": model_type,
            "round_number": round_number,
            "status": "created",
            "created_at": time.time(),
            "start_time": None,
            "end_time": None,
            "min_clients": min_clients,
            "max_clients": max_clients,
            "aggregation_strategy": aggregation_strategy,
            "client_selection_strategy": client_selection_strategy,
            "round_timeout": round_timeout,
            "hyperparameters": hyperparameters or {},
            "clients": {},  # client_id -> client status
            "results": None
        }
        
        # Create round directory
        round_dir = os.path.join(self.rounds_dir, round_id)
        os.makedirs(round_dir, exist_ok=True)
        
        # Create subdirectories for client models and global model
        os.makedirs(os.path.join(round_dir, "client_models"), exist_ok=True)
        os.makedirs(os.path.join(round_dir, "global_model"), exist_ok=True)
        
        # Save round information
        with open(os.path.join(round_dir, "round_info.json"), "w") as f:
            json.dump(round_info, f, indent=2)
        
        # Store round in active rounds
        self.active_rounds[round_id] = round_info
        
        logger.info(f"Created new round: {round_id} for model {model_id}, round number {round_number}")
        
        return {
            "status": "success",
            "round_id": round_id,
            "message": "Round created successfully"
        }
    
    def select_clients_for_round(self, round_id: str) -> List[str]:
        """
        Select clients to participate in a round.
        
        Args:
            round_id: ID of the round
            
        Returns:
            List of selected client IDs
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return []
        
        round_info = self.active_rounds[round_id]
        model_type = round_info["model_type"]
        max_clients = round_info["max_clients"]
        selection_strategy = round_info["client_selection_strategy"]
        
        # Filter eligible clients (those interested in this model type)
        eligible_clients = [
            client_id for client_id, client_info in self.registered_clients.items()
            if client_info["model_type"] == model_type and client_info["status"] == "active"
        ]
        
        if not eligible_clients:
            logger.warning(f"No eligible clients found for round {round_id}")
            return []
        
        selected_clients = []
        
        # Select clients based on the specified strategy
        if selection_strategy == "random":
            import random
            # Randomly select up to max_clients
            selected_clients = random.sample(eligible_clients, min(max_clients, len(eligible_clients)))
        
        elif selection_strategy == "resource_based":
            # Select based on device resources (prefer more powerful devices)
            # Sort clients by CPU/GPU power
            sorted_clients = sorted(
                eligible_clients,
                key=lambda client_id: self._calculate_client_score(self.registered_clients[client_id]),
                reverse=True  # Higher score first
            )
            selected_clients = sorted_clients[:max_clients]
        
        elif selection_strategy == "participation_based":
            # Prefer clients that have participated less frequently
            sorted_clients = sorted(
                eligible_clients,
                key=lambda client_id: self.registered_clients[client_id]["rounds_participated"]
            )
            selected_clients = sorted_clients[:max_clients]
        
        else:
            logger.warning(f"Unknown client selection strategy: {selection_strategy}, using random selection")
            import random
            selected_clients = random.sample(eligible_clients, min(max_clients, len(eligible_clients)))
        
        # Update round info with selected clients
        for client_id in selected_clients:
            round_info["clients"][client_id] = {
                "status": "invited",
                "invited_at": time.time(),
                "joined_at": None,
                "completed_at": None,
                "model_path": None,
                "training_metrics": None
            }
            
            # Update client-round mapping
            if client_id not in self.client_rounds:
                self.client_rounds[client_id] = []
            self.client_rounds[client_id].append(round_id)
        
        # Save updated round info
        round_dir = os.path.join(self.rounds_dir, round_id)
        with open(os.path.join(round_dir, "round_info.json"), "w") as f:
            json.dump(round_info, f, indent=2)
        
        logger.info(f"Selected {len(selected_clients)} clients for round {round_id}: {selected_clients}")
        
        return selected_clients
    
    def start_round(self, round_id: str) -> Dict[str, Any]:
        """
        Start a federated learning round.
        
        Args:
            round_id: ID of the round
            
        Returns:
            Round start result
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return {
                "status": "error",
                "message": f"Round {round_id} not found"
            }
        
        round_info = self.active_rounds[round_id]
        
        if round_info["status"] != "created":
            logger.error(f"Round {round_id} is already in progress or completed")
            return {
                "status": "error",
                "message": f"Round {round_id} is already in progress or completed"
            }
        
        # Check if we have enough clients
        if len(round_info["clients"]) < round_info["min_clients"]:
            logger.error(f"Not enough clients for round {round_id}. Need at least {round_info['min_clients']}")
            return {
                "status": "error",
                "message": f"Not enough clients for round {round_id}. Need at least {round_info['min_clients']}"
            }
        
        # Update round status
        round_info["status"] = "in_progress"
        round_info["start_time"] = time.time()
        
        # Save global model for this round
        self._prepare_global_model(round_id)
        
        # Save updated round info
        round_dir = os.path.join(self.rounds_dir, round_id)
        with open(os.path.join(round_dir, "round_info.json"), "w") as f:
            json.dump(round_info, f, indent=2)
        
        logger.info(f"Started round {round_id}")
        
        # Submit task to check for round timeout
        self.executor.submit(self._monitor_round_timeout, round_id)
        
        return {
            "status": "success",
            "message": f"Round {round_id} started successfully"
        }
    
    def client_join_round(self, round_id: str, client_id: str) -> Dict[str, Any]:
        """
        Handle a client joining a round.
        
        Args:
            round_id: ID of the round
            client_id: ID of the client
            
        Returns:
            Join result
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return {
                "status": "error",
                "message": f"Round {round_id} not found"
            }
        
        round_info = self.active_rounds[round_id]
        
        if round_info["status"] != "in_progress":
            logger.error(f"Round {round_id} is not in progress")
            return {
                "status": "error",
                "message": f"Round {round_id} is not in progress"
            }
        
        if client_id not in round_info["clients"]:
            logger.error(f"Client {client_id} not invited to round {round_id}")
            return {
                "status": "error",
                "message": f"Client {client_id} not invited to round {round_id}"
            }
        
        client_info = round_info["clients"][client_id]
        
        if client_info["status"] != "invited":
            logger.error(f"Client {client_id} already joined or completed round {round_id}")
            return {
                "status": "error",
                "message": f"Client {client_id} already joined or completed round {round_id}"
            }
        
        # Update client status
        client_info["status"] = "joined"
        client_info["joined_at"] = time.time()
        
        # Save updated round info
        round_dir = os.path.join(self.rounds_dir, round_id)
        with open(os.path.join(round_dir, "round_info.json"), "w") as f:
            json.dump(round_info, f, indent=2)
        
        logger.info(f"Client {client_id} joined round {round_id}")
        
        # Update last active timestamp for client
        if client_id in self.registered_clients:
            self.registered_clients[client_id]["last_active"] = time.time()
        
        # Return the global model path for this round
        global_model_path = os.path.join(round_dir, "global_model", "model.pt")
        
        return {
            "status": "success",
            "message": f"Client {client_id} joined round {round_id} successfully",
            "global_model_path": global_model_path
        }
    
    def upload_client_model(self, round_id: str, client_id: str, model_path: str, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle a client uploading their trained model.
        
        Args:
            round_id: ID of the round
            client_id: ID of the client
            model_path: Path to the client's trained model
            metrics: Training metrics from the client
            
        Returns:
            Upload result
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return {
                "status": "error",
                "message": f"Round {round_id} not found"
            }
        
        round_info = self.active_rounds[round_id]
        
        if round_info["status"] != "in_progress":
            logger.error(f"Round {round_id} is not in progress")
            return {
                "status": "error",
                "message": f"Round {round_id} is not in progress"
            }
        
        if client_id not in round_info["clients"]:
            logger.error(f"Client {client_id} not part of round {round_id}")
            return {
                "status": "error",
                "message": f"Client {client_id} not part of round {round_id}"
            }
        
        client_info = round_info["clients"][client_id]
        
        if client_info["status"] != "joined":
            logger.error(f"Client {client_id} has not joined or already completed round {round_id}")
            return {
                "status": "error",
                "message": f"Client {client_id} has not joined or already completed round {round_id}"
            }
        
        # Copy model to round directory
        round_dir = os.path.join(self.rounds_dir, round_id)
        client_model_dir = os.path.join(round_dir, "client_models")
        client_model_path = os.path.join(client_model_dir, f"{client_id}_model.pt")
        
        os.makedirs(client_model_dir, exist_ok=True)
        shutil.copy(model_path, client_model_path)
        
        # Update client status
        client_info["status"] = "completed"
        client_info["completed_at"] = time.time()
        client_info["model_path"] = client_model_path
        client_info["training_metrics"] = metrics
        
        # Update client participation count
        if client_id in self.registered_clients:
            self.registered_clients[client_id]["rounds_participated"] += 1
            self.registered_clients[client_id]["last_active"] = time.time()
        
        # Save updated round info
        with open(os.path.join(round_dir, "round_info.json"), "w") as f:
            json.dump(round_info, f, indent=2)
        
        logger.info(f"Client {client_id} uploaded model for round {round_id}")
        
        # Check if all clients have completed
        all_completed = all(c["status"] == "completed" for c in round_info["clients"].values())
        
        if all_completed:
            # Submit task to finish the round
            self.executor.submit(self._finish_round, round_id)
        
        return {
            "status": "success",
            "message": f"Client {client_id} model uploaded successfully for round {round_id}"
        }
    
    def get_round_status(self, round_id: str) -> Dict[str, Any]:
        """
        Get the status of a federated learning round.
        
        Args:
            round_id: ID of the round
            
        Returns:
            Round status information
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return {
                "status": "error",
                "message": f"Round {round_id} not found"
            }
        
        round_info = self.active_rounds[round_id]
        
        # Prepare a summary for clients
        client_summary = {}
        for client_id, client_info in round_info["clients"].items():
            client_summary[client_id] = {
                "status": client_info["status"],
                "joined_at": client_info["joined_at"],
                "completed_at": client_info["completed_at"]
            }
        
        # Create a response with essential information
        response = {
            "status": "success",
            "round_id": round_id,
            "model_id": round_info["model_id"],
            "model_type": round_info["model_type"],
            "round_number": round_info["round_number"],
            "round_status": round_info["status"],
            "created_at": round_info["created_at"],
            "start_time": round_info["start_time"],
            "end_time": round_info["end_time"],
            "client_count": len(round_info["clients"]),
            "completed_clients": sum(1 for c in round_info["clients"].values() if c["status"] == "completed"),
            "client_summary": client_summary,
            "results": round_info["results"]
        }
        
        return response
    
    def get_available_rounds(self, client_id: str, model_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available rounds for a client.
        
        Args:
            client_id: ID of the client
            model_type: Optional filter for model type
            
        Returns:
            List of available rounds
        """
        available_rounds = []
        
        for round_id, round_info in self.active_rounds.items():
            # Skip rounds that are not in progress
            if round_info["status"] != "in_progress":
                continue
            
            # Filter by model type if specified
            if model_type and round_info["model_type"] != model_type:
                continue
            
            # Check if client is part of this round
            if client_id in round_info["clients"]:
                client_info = round_info["clients"][client_id]
                
                # Only include rounds where the client is invited but not joined or completed
                if client_info["status"] == "invited":
                    available_rounds.append({
                        "round_id": round_id,
                        "model_id": round_info["model_id"],
                        "model_type": round_info["model_type"],
                        "round_number": round_info["round_number"],
                        "invited_at": client_info["invited_at"]
                    })
        
        return {
            "status": "success",
            "client_id": client_id,
            "available_rounds": available_rounds
        }
    
    def get_global_model(self, model_type: str, version: str = "latest") -> Dict[str, Any]:
        """
        Get the global model for a specific model type and version.
        
        Args:
            model_type: Type of model
            version: Model version (default: latest)
            
        Returns:
            Information about the global model
        """
        # Find the latest round for this model type
        latest_round_id = None
        latest_round_number = -1
        
        for round_id, round_info in self.active_rounds.items():
            if round_info["model_type"] == model_type and round_info["status"] == "completed":
                if round_info["round_number"] > latest_round_number:
                    latest_round_number = round_info["round_number"]
                    latest_round_id = round_id
        
        if not latest_round_id:
            logger.error(f"No completed rounds found for model type {model_type}")
            return {
                "status": "error",
                "message": f"No completed rounds found for model type {model_type}"
            }
        
        # Get the global model path
        round_dir = os.path.join(self.rounds_dir, latest_round_id)
        global_model_path = os.path.join(round_dir, "global_model", "aggregated.pt")
        
        if not os.path.exists(global_model_path):
            logger.error(f"Global model not found at {global_model_path}")
            return {
                "status": "error",
                "message": f"Global model not found for model type {model_type}"
            }
        
        return {
            "status": "success",
            "model_type": model_type,
            "version": str(latest_round_number),
            "round_id": latest_round_id,
            "global_model_path": global_model_path
        }
    
    def shutdown(self) -> None:
        """Shutdown the server gracefully."""
        logger.info("Shutting down Federated Learning Server...")
        
        # Signal worker threads to stop
        self.stop_event.set()
        
        # Wait for worker threads to finish
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        # Shutdown thread pool
        self.executor.shutdown(wait=False)
        
        logger.info("Federated Learning Server shut down")
    
    def _worker_loop(self) -> None:
        """Worker thread loop for handling requests."""
        while not self.stop_event.is_set():
            try:
                # Get a request from the queue with timeout
                request = self.request_queue.get(timeout=1.0)
                
                # Process the request
                try:
                    func = request["function"]
                    args = request["args"]
                    kwargs = request["kwargs"]
                    callback = request["callback"]
                    
                    # Call the function
                    result = func(*args, **kwargs)
                    
                    # Call the callback with the result
                    if callback:
                        callback(result)
                
                except Exception as e:
                    logger.error(f"Error processing request: {str(e)}")
                
                finally:
                    # Mark the request as done
                    self.request_queue.task_done()
            
            except queue.Empty:
                # Queue is empty, continue waiting
                continue
    
    def _prepare_global_model(self, round_id: str) -> str:
        """
        Prepare the global model for a round.
        
        Args:
            round_id: ID of the round
            
        Returns:
            Path to the global model
        """
        round_info = self.active_rounds[round_id]
        model_type = round_info["model_type"]
        model_id = round_info["model_id"]
        round_number = round_info["round_number"]
        
        round_dir = os.path.join(self.rounds_dir, round_id)
        global_model_dir = os.path.join(round_dir, "global_model")
        os.makedirs(global_model_dir, exist_ok=True)
        
        global_model_path = os.path.join(global_model_dir, "model.pt")
        
        # If this is the first round, create an initial model
        if round_number == 1:
            # Create an empty model
            try:
                aggregator = ModelAggregator(model_type)
                model = aggregator.load_empty_model()
                torch.save(model.state_dict(), global_model_path)
                logger.info(f"Created initial global model for round {round_id}")
            except Exception as e:
                logger.error(f"Error creating initial model: {str(e)}")
                # Create an empty file as a fallback
                with open(global_model_path, "wb") as f:
                    pass
        else:
            # Find the previous round
            prev_round_id = None
            prev_round_number = -1
            
            for r_id, r_info in self.active_rounds.items():
                if r_info["model_id"] == model_id and r_info["status"] == "completed":
                    if r_info["round_number"] == round_number - 1:
                        prev_round_id = r_id
                        prev_round_number = r_info["round_number"]
                        break
            
            if prev_round_id:
                # Copy the aggregated model from the previous round
                prev_round_dir = os.path.join(self.rounds_dir, prev_round_id)
                prev_model_path = os.path.join(prev_round_dir, "global_model", "aggregated.pt")
                
                if os.path.exists(prev_model_path):
                    shutil.copy(prev_model_path, global_model_path)
                    logger.info(f"Copied global model from round {prev_round_id} for round {round_id}")
                else:
                    logger.error(f"Previous round model not found at {prev_model_path}")
                    # Create an empty model as a fallback
                    try:
                        aggregator = ModelAggregator(model_type)
                        model = aggregator.load_empty_model()
                        torch.save(model.state_dict(), global_model_path)
                    except Exception as e:
                        logger.error(f"Error creating fallback model: {str(e)}")
                        # Create an empty file as a last resort
                        with open(global_model_path, "wb") as f:
                            pass
            else:
                logger.warning(f"No previous round found for round {round_id}, creating new model")
                # Create an empty model
                try:
                    aggregator = ModelAggregator(model_type)
                    model = aggregator.load_empty_model()
                    torch.save(model.state_dict(), global_model_path)
                except Exception as e:
                    logger.error(f"Error creating new model: {str(e)}")
                    # Create an empty file as a fallback
                    with open(global_model_path, "wb") as f:
                        pass
        
        return global_model_path
    
    def _finish_round(self, round_id: str) -> None:
        """
        Finish a federated learning round by aggregating models and updating the global model.
        
        Args:
            round_id: ID of the round
        """
        if round_id not in self.active_rounds:
            logger.error(f"Round {round_id} not found")
            return
        
        round_info = self.active_rounds[round_id]
        
        if round_info["status"] != "in_progress":
            logger.error(f"Round {round_id} is not in progress")
            return
        
        logger.info(f"Finishing round {round_id}")
        
        # Get model paths from completed clients
        client_model_paths = []
        client_weights = []
        
        for client_id, client_info in round_info["clients"].items():
            if client_info["status"] == "completed" and client_info["model_path"]:
                client_model_paths.append(client_info["model_path"])
                
                # Use training data size as weight if available
                if client_info["training_metrics"] and "data_size" in client_info["training_metrics"]:
                    weight = client_info["training_metrics"]["data_size"]
                else:
                    weight = 1.0
                
                client_weights.append(weight)
        
        if not client_model_paths:
            logger.error(f"No completed client models found for round {round_id}")
            
            # Mark round as failed
            round_info["status"] = "failed"
            round_info["end_time"] = time.time()
            
            # Save updated round info
            round_dir = os.path.join(self.rounds_dir, round_id)
            with open(os.path.join(round_dir, "round_info.json"), "w") as f:
                json.dump(round_info, f, indent=2)
            
            return
        
        # Aggregate client models
        try:
            model_type = round_info["model_type"]
            aggregation_strategy = round_info["aggregation_strategy"]
            
            aggregator = ModelAggregator(model_type)
            aggregated_path = aggregator.aggregate_models(
                model_paths=client_model_paths,
                weights=client_weights,
                strategy=aggregation_strategy
            )
            
            # Copy aggregated model to round directory
            round_dir = os.path.join(self.rounds_dir, round_id)
            global_model_dir = os.path.join(round_dir, "global_model")
            aggregated_model_path = os.path.join(global_model_dir, "aggregated.pt")
            
            shutil.copy(aggregated_path, aggregated_model_path)
            
            # Evaluate the aggregated model if a test dataset is available
            test_data_path = os.path.join("data", "test", model_type)
            if os.path.exists(test_data_path):
                metrics = aggregator.evaluate_aggregated_model(
                    model_path=aggregated_model_path,
                    test_data_path=test_data_path
                )
                
                # Save metrics
                metrics_path = os.path.join(global_model_dir, "metrics.json")
                with open(metrics_path, "w") as f:
                    json.dump(metrics, f, indent=2)
                
                # Store results in round info
                round_info["results"] = metrics
            else:
                logger.warning(f"Test data not found at {test_data_path}, skipping evaluation")
                round_info["results"] = {"message": "No test data available for evaluation"}
            
            # Mark round as completed
            round_info["status"] = "completed"
            round_info["end_time"] = time.time()
            
            # Save updated round info
            with open(os.path.join(round_dir, "round_info.json"), "w") as f:
                json.dump(round_info, f, indent=2)
            
            logger.info(f"Round {round_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Error aggregating models for round {round_id}: {str(e)}")
            
            # Mark round as failed
            round_info["status"] = "failed"
            round_info["end_time"] = time.time()
            
            # Save updated round info
            round_dir = os.path.join(self.rounds_dir, round_id)
            with open(os.path.join(round_dir, "round_info.json"), "w") as f:
                json.dump(round_info, f, indent=2)
    
    def _monitor_round_timeout(self, round_id: str) -> None:
        """
        Monitor a round for timeout.
        
        Args:
            round_id: ID of the round
        """
        if round_id not in self.active_rounds:
            return
        
        round_info = self.active_rounds[round_id]
        
        if round_info["status"] != "in_progress":
            return
        
        # Calculate time until timeout
        start_time = round_info["start_time"]
        timeout = round_info["round_timeout"]
        time_remaining = (start_time + timeout) - time.time()
        
        if time_remaining > 0:
            # Sleep until timeout
            time.sleep(time_remaining)
        
        # Check if round is still in progress
        if round_id in self.active_rounds and self.active_rounds[round_id]["status"] == "in_progress":
            logger.warning(f"Round {round_id} timed out")
            
            # Mark clients that didn't complete as timed out
            for client_id, client_info in round_info["clients"].items():
                if client_info["status"] != "completed":
                    client_info["status"] = "timed_out"
            
            # Finish the round with available models
            self._finish_round(round_id)
    
    def _calculate_client_score(self, client_info: Dict[str, Any]) -> float:
        """
        Calculate a score for a client based on its resources.
        
        Args:
            client_info: Client information
            
        Returns:
            Resource score
        """
        score = 1.0
        
        if "device_info" in client_info:
            device_info = client_info["device_info"]
            
            # Boost score for GPU availability
            if device_info.get("has_gpu", False):
                score *= 2.0
                
                # Consider GPU count
                gpu_count = device_info.get("gpu_count", 1)
                score *= (1.0 + 0.5 * (gpu_count - 1))
            
            # TODO: Consider other resource factors like CPU, memory, etc.
        
        return score


def run_server():
    """Run the federated learning server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Federated Learning Server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host")
    parser.add_argument("--port", type=int, default=5000, help="Server port")
    parser.add_argument("--models-dir", type=str, default="models", help="Directory for models")
    parser.add_argument("--rounds-dir", type=str, default="rounds", help="Directory for rounds")
    parser.add_argument("--no-security", action="store_true", help="Disable security")
    parser.add_argument("--workers", type=int, default=5, help="Number of worker threads")
    
    args = parser.parse_args()
    
    # Create the server
    server = FederatedLearningServer(
        models_dir=args.models_dir,
        rounds_dir=args.rounds_dir,
        init_security=not args.no_security,
        worker_threads=args.workers
    )
    
    try:
        # Here you would normally start a web server to handle API requests
        # For simplicity, we'll just sleep in this example
        logger.info(f"Server running on {args.host}:{args.port}")
        logger.info("Press Ctrl+C to stop")
        
        import time
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down")
    
    finally:
        server.shutdown()


if __name__ == "__main__":
    run_server()
