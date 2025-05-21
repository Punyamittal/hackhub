import os
import logging
import torch
import json
from typing import List, Dict, Any, Optional, Tuple
import importlib
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Aggregator")

class ModelAggregator:
    """
    Aggregates models from multiple clients to create a federated global model.
    Implements various aggregation strategies like Federated Averaging (FedAvg).
    """
    
    def __init__(self, model_type: str):
        """
        Initialize the model aggregator.
        
        Args:
            model_type: Type of model being aggregated (e.g., 'pneumonia', 'ecg_analysis')
        """
        self.model_type = model_type
        logger.info(f"Initialized model aggregator for {model_type}")
    
    def load_empty_model(self) -> torch.nn.Module:
        """
        Load an empty model of the specified type.
        
        Returns:
            PyTorch model with default initialization
        """
        try:
            # Import the model module dynamically
            module_path = f"federated_learning.models.{self.model_type}.model"
            model_module = importlib.import_module(module_path)
            
            # Get the model class and create an instance
            model_class = getattr(model_module, "Model")
            model = model_class()
            
            logger.info(f"Created empty model for {self.model_type}")
            return model
        except Exception as e:
            logger.error(f"Error creating empty model: {str(e)}")
            raise
    
    def aggregate_models(
        self, 
        model_paths: List[str], 
        weights: Optional[List[float]] = None,
        strategy: str = "fedavg"
    ) -> str:
        """
        Aggregate models using the specified strategy.
        
        Args:
            model_paths: List of paths to client models
            weights: Optional weights for each model (e.g., based on dataset size)
            strategy: Aggregation strategy ('fedavg', 'weighted_avg', etc.)
            
        Returns:
            Path to the aggregated model
        """
        if not model_paths:
            raise ValueError("No models provided for aggregation")
        
        if strategy.lower() == "fedavg":
            return self._federated_averaging(model_paths, weights)
        else:
            logger.warning(f"Unknown aggregation strategy: {strategy}, using FedAvg")
            return self._federated_averaging(model_paths, weights)
    
    def _federated_averaging(self, model_paths: List[str], weights: Optional[List[float]] = None) -> str:
        """
        Implement Federated Averaging (FedAvg) algorithm.
        
        Args:
            model_paths: List of paths to client models
            weights: Optional weights for each model
            
        Returns:
            Path to the aggregated model
        """
        try:
            # Load all client models
            client_models = []
            for path in model_paths:
                # Create a new model instance
                model = self.load_empty_model()
                
                # Load the state dict from the client model
                model.load_state_dict(torch.load(path))
                client_models.append(model)
            
            # Get the state dict of the first model as reference
            global_state_dict = client_models[0].state_dict()
            
            # If weights are not provided, use equal weighting
            if weights is None:
                weights = [1.0 / len(client_models)] * len(client_models)
            else:
                # Normalize weights to sum to 1
                weights = [w / sum(weights) for w in weights]
            
            # For each parameter in the model
            for key in global_state_dict.keys():
                # Skip batch normalization parameters
                if 'running_mean' in key or 'running_var' in key or 'num_batches_tracked' in key:
                    continue
                
                # Initialize parameter with weighted value from first model
                global_state_dict[key] = client_models[0].state_dict()[key] * weights[0]
                
                # Add weighted parameters from other models
                for i in range(1, len(client_models)):
                    global_state_dict[key] += client_models[i].state_dict()[key] * weights[i]
            
            # Create a new model and load the aggregated state dict
            global_model = self.load_empty_model()
            global_model.load_state_dict(global_state_dict)
            
            # Save the aggregated model
            aggregated_dir = os.path.join("models", "global", self.model_type)
            os.makedirs(aggregated_dir, exist_ok=True)
            
            aggregated_path = os.path.join(aggregated_dir, "aggregated.pt")
            torch.save(global_model.state_dict(), aggregated_path)
            
            logger.info(f"Successfully aggregated {len(client_models)} models using FedAvg")
            return aggregated_path
            
        except Exception as e:
            logger.error(f"Error during FedAvg aggregation: {str(e)}")
            raise
    
    def evaluate_aggregated_model(
        self, 
        model_path: str, 
        test_data_path: str
    ) -> Dict[str, float]:
        """
        Evaluate the aggregated model on a test dataset.
        
        Args:
            model_path: Path to the aggregated model
            test_data_path: Path to test data
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Import the evaluation module dynamically
            module_path = f"federated_learning.models.{self.model_type}.evaluate"
            try:
                eval_module = importlib.import_module(module_path)
                evaluate_func = getattr(eval_module, "evaluate_model")
                
                metrics = evaluate_func(model_path, test_data_path)
                logger.info(f"Evaluation metrics: {metrics}")
                return metrics
            except (ImportError, AttributeError):
                logger.warning(f"Custom evaluation module not found for {self.model_type}")
                
                # Fall back to a basic evaluation
                return self._basic_evaluate(model_path, test_data_path)
                
        except Exception as e:
            logger.error(f"Error evaluating aggregated model: {str(e)}")
            return {
                "error": str(e),
                "accuracy": 0.0,
                "f1_score": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "loss": float('inf')
            }
    
    def _basic_evaluate(self, model_path: str, test_data_path: str) -> Dict[str, float]:
        """
        Perform a basic evaluation of the model.
        
        Args:
            model_path: Path to the model
            test_data_path: Path to test data
            
        Returns:
            Dictionary with evaluation metrics
        """
        try:
            # Import necessary modules
            from torch.utils.data import DataLoader
            import torch.nn as nn
            
            device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
            
            # Load model
            model = self.load_empty_model()
            model.load_state_dict(torch.load(model_path))
            model = model.to(device)
            model.eval()
            
            # Load dataset
            try:
                module_path = f"federated_learning.models.{self.model_type}.dataset"
                dataset_module = importlib.import_module(module_path)
                dataset_class = getattr(dataset_module, "CustomDataset")
                test_dataset = dataset_class(test_data_path, train=False)
            except Exception as e:
                logger.error(f"Error loading test dataset: {str(e)}")
                return {"error": "Failed to load test dataset"}
            
            # Create data loader
            test_loader = DataLoader(
                test_dataset,
                batch_size=32,
                shuffle=False,
                num_workers=4,
                pin_memory=True if device.type == "cuda" else False
            )
            
            # Get loss function
            try:
                module_path = f"federated_learning.models.{self.model_type}.hyperparams"
                hyperparam_module = importlib.import_module(module_path)
                hyperparams = getattr(hyperparam_module, "HYPERPARAMS")
                loss_type = hyperparams.get("loss_function", "cross_entropy").lower()
                
                if loss_type == "cross_entropy":
                    loss_fn = nn.CrossEntropyLoss()
                elif loss_type == "bce":
                    loss_fn = nn.BCELoss()
                elif loss_type == "bce_with_logits":
                    loss_fn = nn.BCEWithLogitsLoss()
                elif loss_type == "mse":
                    loss_fn = nn.MSELoss()
                else:
                    loss_fn = nn.CrossEntropyLoss()
            except Exception:
                loss_fn = nn.CrossEntropyLoss()
            
            # Evaluation
            total_loss = 0.0
            total_correct = 0
            total_samples = 0
            
            true_positives = 0
            true_negatives = 0
            false_positives = 0
            false_negatives = 0
            
            with torch.no_grad():
                for batch in test_loader:
                    inputs, targets = batch
                    
                    # Move data to device
                    inputs = inputs.to(device)
                    targets = targets.to(device)
                    
                    # Forward pass
                    outputs = model(inputs)
                    
                    # Calculate loss
                    loss = loss_fn(outputs, targets)
                    total_loss += loss.item() * inputs.size(0)
                    
                    # Calculate accuracy and confusion matrix values
                    if targets.dim() == 1:  # Multi-class classification
                        _, predicted = torch.max(outputs, 1)
                        total_correct += (predicted == targets).sum().item()
                        
                        # For simplicity, we only calculate binary metrics for binary classification or first class in multi-class
                        binary_targets = (targets == 1).float()
                        binary_preds = (predicted == 1).float()
                    else:  # Binary classification
                        predicted = (outputs >= 0.5).float()
                        total_correct += (predicted == targets).sum().item()
                        
                        binary_targets = targets
                        binary_preds = predicted
                    
                    # Update confusion matrix values
                    true_positives += ((binary_preds == 1) & (binary_targets == 1)).sum().item()
                    true_negatives += ((binary_preds == 0) & (binary_targets == 0)).sum().item()
                    false_positives += ((binary_preds == 1) & (binary_targets == 0)).sum().item()
                    false_negatives += ((binary_preds == 0) & (binary_targets == 1)).sum().item()
                    
                    total_samples += targets.size(0)
            
            # Calculate metrics
            avg_loss = total_loss / total_samples
            accuracy = total_correct / total_samples
            
            # Avoid division by zero
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            metrics = {
                "loss": avg_loss,
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1
            }
            
            # Save metrics to file
            metrics_dir = os.path.join("models", "global", self.model_type)
            os.makedirs(metrics_dir, exist_ok=True)
            
            metrics_path = os.path.join(metrics_dir, "evaluation_metrics.json")
            with open(metrics_path, "w") as f:
                json.dump(metrics, f, indent=2)
            
            logger.info(f"Basic evaluation complete: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error in basic evaluation: {str(e)}")
            return {"error": str(e)}


if __name__ == "__main__":
    # Test the aggregator
    import argparse
    
    parser = argparse.ArgumentParser(description="Test model aggregation")
    parser.add_argument("--model_type", type=str, required=True, help="Type of model")
    parser.add_argument("--model_paths", type=str, nargs="+", required=True, help="Paths to client models")
    parser.add_argument("--weights", type=float, nargs="+", help="Weights for each model")
    parser.add_argument("--strategy", type=str, default="fedavg", help="Aggregation strategy")
    parser.add_argument("--test_data", type=str, help="Path to test data for evaluation")
    
    args = parser.parse_args()
    
    aggregator = ModelAggregator(args.model_type)
    
    # Aggregate models
    aggregated_path = aggregator.aggregate_models(
        model_paths=args.model_paths,
        weights=args.weights,
        strategy=args.strategy
    )
    
    print(f"Aggregated model saved to: {aggregated_path}")
    
    # Evaluate if test data is provided
    if args.test_data:
        metrics = aggregator.evaluate_aggregated_model(
            model_path=aggregated_path,
            test_data_path=args.test_data
        )
        
        print("Evaluation metrics:")
        for k, v in metrics.items():
            print(f"  {k}: {v}")
