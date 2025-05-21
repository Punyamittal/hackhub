# HachathonHub

HachathonHub is a Groq-powered AI companion providing real-time health insights and recommendations through federated learning.

## Problem Statement

HachathonHub addresses a key gap in healthcare AI: the inability to access diverse patient data due to privacy concerns. Traditional ML models are often biased because they're trained on limited populations.

## Solution

A secure federated learning (FL) system where hospitals and research centers (data providers) train local models on sensitive patient data. The model weights are then encrypted and shared to build a robust, global model.

## User Categories

1. **Admin/Developers:** Full access to system controls, monitoring, and configuration.
2. **Data Providers:** Hospitals and research centers that upload encrypted data and participate in training.
3. **Contributors:** Participants in the federated chain that offer compute resources and local model updates.
4. **Users:** End users who consume the AI-driven health insights and recommendations.

## Features

- **Groq-Powered Chat:** Ultra-fast AI inference for health-related questions
- **Model Hive:** Access to various medical AI models
- **Federated Learning:** Privacy-preserving collaborative model training
- **Admin Dashboard:** Monitor model performance and system metrics

## Tech Stack

- **Frontend:** Next.js, Tailwind CSS
- **Backend:** Python, FastAPI
- **Database:** Supabase, AstraDB (Vector Database)
- **ML Models:** Scikit-learn, TensorFlow
- **LLM Models:** Groq API
- **Federated Learning:** Flower
- **Model Performance Tracking:** MLflow

## Model Hive

1. **LLM Symptom Analysis:** AI-powered health assessment using Groq inference and RAG
2. **ECG Curve Analysis:** Graph-based retrieval augmented generation
3. **Pneumonia Analysis:** X-ray image analysis for pneumonia detection
4. **Breast Cancer Detection:** Early detection using advanced imaging analysis
5. **Glaucoma Detection:** FUNDUS image analysis for glaucoma screening

## Architecture

HachathonHub uses a microservices architecture with a Next.js frontend, FastAPI backend, Supabase for structured data, and AstraDB for vector embeddings. The federated learning system is built using Flower, allowing training to happen at the data source with only model updates being shared.

## Getting Started

### Prerequisites

- Node.js (v18.x or later)
- Python (v3.10 or later)
- Docker and Docker Compose

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/your-org/HachathonHub.git
   cd HachathonHub
   ```

2. Set up the frontend
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Set up the backend
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```

4. Set up the database
   ```bash
   docker-compose up -d db
   ```

## Contributing

Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.