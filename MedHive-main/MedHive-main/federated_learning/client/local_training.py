import os
import logging
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
import numpy as np
from typing import Dict, Any, Optional, List, Tuple
import importlib
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("FL_Training")

def load_model(model_type: str, model_path: str) -> nn.Module:
    """
    Load a model of the specified type from the given path.
    
    Args:
        model_type: Type of model (e.g., 'pneumonia', 'ecg_analysis')
        model_path: Path to saved model weights
    
    Returns:
        PyTorch model loaded with weights
    """
    try:
        # Import the model module dynamically
        module_path = f"federated_learning.models.{model_type}.model"
        model_module = importlib.import_module(module_path)
        
        # Get the model class and create an instance
        model_class = getattr(model_module, "Model")
        model = model_class()
        
        # Load weights if the model path exists
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path))
            logger.info(f"Loaded model weights from {model_path}")
        else:
            logger.warning(f"Model path {model_path} not found, using default initialization")
        
        return model
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        raise

def load_dataset(model_type: str, data_path: str) -> Dataset:
    """
    Load a dataset for the specified model type from the given path.
    
    Args:
        model_type: Type of model (e.g., 'pneumonia', 'ecg_analysis')
        data_path: Path to the dataset
    
    Returns:
        PyTorch Dataset
    """
    try:
        # Import the dataset module dynamically
        module_path = f"federated_learning.models.{model_type}.dataset"
        dataset_module = importlib.import_module(module_path)
        
        # Get the dataset class and create an instance
        dataset_class = getattr(dataset_module, "CustomDataset")
        dataset = dataset_class(data_path)
        
        return dataset
    except Exception as e:
        logger.error(f"Error loading dataset: {str(e)}")
        raise

def get_optimizer(model: nn.Module, model_type: str) -> optim.Optimizer:
    """
    Get the appropriate optimizer for the model type.
    
    Args:
        model: PyTorch model
        model_type: Type of model
    
    Returns:
        PyTorch optimizer
    """
    # Load model-specific hyperparameters
    try:
        module_path = f"federated_learning.models.{model_type}.hyperparams"
        hyperparam_module = importlib.import_module(module_path)
        hyperparams = getattr(hyperparam_module, "HYPERPARAMS")
        
        lr = hyperparams.get("learning_rate", 0.001)
        optimizer_type = hyperparams.get("optimizer", "adam").lower()
        weight_decay = hyperparams.get("weight_decay", 0.0)
        
        if optimizer_type == "adam":
            return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
        elif optimizer_type == "sgd":
            momentum = hyperparams.get("momentum", 0.9)
            return optim.SGD(model.parameters(), lr=lr, momentum=momentum, weight_decay=weight_decay)
        elif optimizer_type == "rmsprop":
            return optim.RMSprop(model.parameters(), lr=lr, weight_decay=weight_decay)
        else:
            logger.warning(f"Unknown optimizer type: {optimizer_type}, using Adam")
            return optim.Adam(model.parameters(), lr=lr, weight_decay=weight_decay)
    except Exception as e:
        logger.warning(f"Error loading hyperparameters: {str(e)}, using default Adam optimizer")
        return optim.Adam(model.parameters(), lr=0.001)

def get_loss_function(model_type: str) -> nn.Module:
    """
    Get the appropriate loss function for the model type.
    
    Args:
        model_type: Type of model
    
    Returns:
        PyTorch loss function
    """
    # Load model-specific hyperparameters for loss function
    try:
        module_path = f"federated_learning.models.{model_type}.hyperparams"
        hyperparam_module = importlib.import_module(module_path)
        hyperparams = getattr(hyperparam_module, "HYPERPARAMS")
        
        loss_type = hyperparams.get("loss_function", "cross_entropy").lower()
        
        if loss_type == "cross_entropy":
            return nn.CrossEntropyLoss()
        elif loss_type == "bce":
            return nn.BCELoss()
        elif loss_type == "bce_with_logits":
            return nn.BCEWithLogitsLoss()
        elif loss_type == "mse":
            return nn.MSELoss()
        elif loss_type == "l1":
            return nn.L1Loss()
        else:
            logger.warning(f"Unknown loss type: {loss_type}, using CrossEntropyLoss")
            return nn.CrossEntropyLoss()
    except Exception as e:
        logger.warning(f"Error loading loss function: {str(e)}, using default CrossEntropyLoss")
        return nn.CrossEntropyLoss()

def evaluate_model(model: nn.Module, dataloader: DataLoader, loss_fn: nn.Module, device: torch.device) -> Dict[str, float]:
    """
    Evaluate a model on the given dataloader.
    
    Args:
        model: PyTorch model
        dataloader: DataLoader with validation/test data
        loss_fn: Loss function
        device: Device to run evaluation on
    
    Returns:
        Dictionary with evaluation metrics
    """
    model.eval()
    total_loss = 0.0
    total_correct = 0
    total_samples = 0
    
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    
    with torch.no_grad():
        for batch in dataloader:
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
    
    return metrics

def train_model(
    global_model_path: str,
    data_path: str,
    model_type: str,
    round_id: int,
    client_id: str,
    epochs: Optional[int] = None,
    batch_size: Optional[int] = None,
    device: Optional[str] = None
) -> str:
    """
    Train a model locally.
    
    Args:
        global_model_path: Path to the global model to start from
        data_path: Path to local data
        model_type: Type of model to train
        round_id: Current federated learning round ID
        client_id: Client ID
        epochs: Number of training epochs (if None, will use model-specific default)
        batch_size: Batch size for training (if None, will use model-specific default)
        device: Device to train on (if None, will use GPU if available)
    
    Returns:
        Path to the trained model
    """
    # Set device
    if device is None:
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
    else:
        device = torch.device(device)
    
    logger.info(f"Training on {device}")
    
    # Load model
    model = load_model(model_type, global_model_path).to(device)
    
    # Load dataset
    full_dataset = load_dataset(model_type, data_path)
    
    # Split dataset into train and validation
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    
    train_dataset, val_dataset = random_split(
        full_dataset, [train_size, val_size],
        generator=torch.Generator().manual_seed(42)  # For reproducibility
    )
    
    # Try to load model-specific hyperparameters
    try:
        module_path = f"federated_learning.models.{model_type}.hyperparams"
        hyperparam_module = importlib.import_module(module_path)
        hyperparams = getattr(hyperparam_module, "HYPERPARAMS")
        
        if epochs is None:
            epochs = hyperparams.get("epochs", 5)
        
        if batch_size is None:
            batch_size = hyperparams.get("batch_size", 32)
    except Exception as e:
        logger.warning(f"Error loading hyperparameters: {str(e)}, using defaults")
        if epochs is None:
            epochs = 5
        if batch_size is None:
            batch_size = 32
    
    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=4,
        pin_memory=True if device.type == "cuda" else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=4,
        pin_memory=True if device.type == "cuda" else False
    )
    
    # Get optimizer and loss function
    optimizer = get_optimizer(model, model_type)
    loss_fn = get_loss_function(model_type)
    
    # Training loop
    logger.info(f"Starting training for {epochs} epochs")
    
    metrics_history = []
    best_val_metric = 0.0
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        for batch_idx, batch in enumerate(train_loader):
            inputs, targets = batch
            
            # Move data to device
            inputs = inputs.to(device)
            targets = targets.to(device)
            
            # Zero the parameter gradients
            optimizer.zero_grad()
            
            # Forward pass
            outputs = model(inputs)
            
            # Compute loss
            loss = loss_fn(outputs, targets)
            
            # Backward pass and optimize
            loss.backward()
            optimizer.step()
            
            # Update statistics
            running_loss += loss.item()
            
            if batch_idx % 10 == 9:  # Log every 10 batches
                logger.info(f"Epoch {epoch+1}/{epochs}, Batch {batch_idx+1}, Loss: {running_loss / 10:.4f}")
                running_loss = 0.0
        
        # Evaluate on validation set
        val_metrics = evaluate_model(model, val_loader, loss_fn, device)
        metrics_history.append(val_metrics)
        
        logger.info(f"Epoch {epoch+1}/{epochs}, Validation: {val_metrics}")
        
        # Save best model (based on F1 score for simplicity)
        if val_metrics["f1_score"] > best_val_metric:
            best_val_metric = val_metrics["f1_score"]
            
            # Save the best model
            best_model_dir = os.path.join("models", "local", model_type, f"round_{round_id}")
            os.makedirs(best_model_dir, exist_ok=True)
            
            best_model_path = os.path.join(best_model_dir, f"client_{client_id}_best.pt")
            torch.save(model.state_dict(), best_model_path)
            logger.info(f"Saved best model to {best_model_path}")
    
    # Save the final model
    final_model_dir = os.path.join("models", "local", model_type, f"round_{round_id}")
    os.makedirs(final_model_dir, exist_ok=True)
    
    final_model_path = os.path.join(final_model_dir, f"client_{client_id}_final.pt")
    torch.save(model.state_dict(), final_model_path)
    logger.info(f"Saved final model to {final_model_path}")
    
    # Save training metrics
    metrics_path = os.path.join(final_model_dir, f"client_{client_id}_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_history, f, indent=2)
    
    # Return the best model path
    return best_model_path


if __name__ == "__main__":
    # Simple test
    import argparse
    
    parser = argparse.ArgumentParser(description="Test local training")
    parser.add_argument("--global_model", type=str, required=True, help="Path to global model")
    parser.add_argument("--data_path", type=str, required=True, help="Path to data")
    parser.add_argument("--model_type", type=str, required=True, help="Type of model")
    parser.add_argument("--round_id", type=int, default=1, help="Round ID")
    parser.add_argument("--client_id", type=str, default="test_client", help="Client ID")
    parser.add_argument("--epochs", type=int, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, help="Batch size")
    
    args = parser.parse_args()
    
    local_model_path = train_model(
        global_model_path=args.global_model,
        data_path=args.data_path,
        model_type=args.model_type,
        round_id=args.round_id,
        client_id=args.client_id,
        epochs=args.epochs,
        batch_size=args.batch_size
    )
    
    print(f"Trained model saved to: {local_model_path}")
