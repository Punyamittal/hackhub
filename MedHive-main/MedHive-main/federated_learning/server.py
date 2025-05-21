import flwr as fl
import os
import argparse
import numpy as np
import mlflow
from typing import Dict, List, Tuple, Optional
from flwr.common import Metrics, FitRes, Parameters, Scalar
from flwr.server.client_proxy import ClientProxy

# Configure MLflow
mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

def weighted_average(metrics: List[Tuple[int, Metrics]]) -> Metrics:
    """Aggregate metrics weighted by the number of samples."""
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]
    
    # Aggregate and return metrics
    return {"accuracy": sum(accuracies) / sum(examples)}

class SaveModelStrategy(fl.server.strategy.FedAvg):
    def __init__(
        self,
        *args,
        model_name: str = "model",
        model_type: str = "pneumonia_detection",
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.model_name = model_name
        self.model_type = model_type
        self.round_metrics = []
        
        # Start MLflow run
        mlflow.start_run(run_name=f"FL_{model_type}_{model_name}")
        
    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """Aggregate model weights and metrics from clients."""
        # Call aggregate_fit from base class (FedAvg)
        aggregated_parameters, aggregated_metrics = super().aggregate_fit(server_round, results, failures)
        
        if aggregated_parameters is not None:
            # Log the round metrics to MLflow
            print(f"Round {server_round} metrics: {aggregated_metrics}")
            mlflow.log_metrics(aggregated_metrics, step=server_round)
            self.round_metrics.append((server_round, aggregated_metrics))
            
            # Save aggregated model weights (typically would be done after conversion to model format)
            # Here we just simulate saving the aggregated parameters
            print(f"Saving aggregated parameters for round {server_round}")
            
            # In a real implementation, we would:
            # 1. Convert parameters to model weights
            # 2. Load them into the model architecture
            # 3. Save the model
            # model = create_model()
            # set_model_params(model, aggregated_parameters)
            # model_path = f"models/{self.model_type}/{self.model_name}_round_{server_round}.h5"
            # model.save(model_path)
            # mlflow.log_artifact(model_path)
            
        return aggregated_parameters, aggregated_metrics
    
    def aggregate_evaluate(
        self,
        server_round: int,
        results: List[Tuple[ClientProxy, FitRes]],
        failures: List[BaseException],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Aggregate evaluation metrics from clients."""
        if not results:
            return None, {}
        
        # Aggregate metrics from client evaluations
        metrics_aggregated = weighted_average([(r.num_examples, r.metrics) for _, r in results])
        
        # Log the evaluation metrics
        print(f"Round {server_round} evaluation metrics: {metrics_aggregated}")
        for metric_name, metric_value in metrics_aggregated.items():
            mlflow.log_metric(f"eval_{metric_name}", metric_value, step=server_round)
        
        return metrics_aggregated.get("accuracy", 0.0), metrics_aggregated
    
    def finalize(self, parameters: Parameters, metrics_distributed: Dict[str, Scalar]) -> None:
        """Called after the final round of federated learning."""
        # Log final model and metrics
        print("Federated learning completed")
        print(f"Final metrics: {metrics_distributed}")
        
        # End the MLflow run
        mlflow.end_run()

def main():
    """Start the Flower server for federated learning."""
    parser = argparse.ArgumentParser(description="Flower Federated Learning Server")
    parser.add_argument(
        "--model", type=str, default="pneumonia_model", help="Name of the model"
    )
    parser.add_argument(
        "--model_type", type=str, default="pneumonia_detection", 
        help="Type of model (pneumonia_detection, breast_cancer, etc.)"
    )
    parser.add_argument(
        "--rounds", type=int, default=3, help="Number of federated learning rounds"
    )
    parser.add_argument(
        "--min_clients", type=int, default=2, help="Minimum number of clients for training"
    )
    args = parser.parse_args()
    
    # Define strategy
    strategy = SaveModelStrategy(
        model_name=args.model,
        model_type=args.model_type,
        fraction_fit=0.5,  # Train on 50% of available clients
        fraction_evaluate=0.5,  # Evaluate on 50% of available clients
        min_fit_clients=args.min_clients,  # Minimum number of clients for training
        min_evaluate_clients=args.min_clients,  # Minimum number of clients for evaluation
        min_available_clients=args.min_clients,  # Minimum number of available clients
    )
    
    # Start Flower server
    fl.server.start_server(
        server_address="0.0.0.0:8080",
        config=fl.server.ServerConfig(num_rounds=args.rounds),
        strategy=strategy,
    )

if __name__ == "__main__":
    main() 


