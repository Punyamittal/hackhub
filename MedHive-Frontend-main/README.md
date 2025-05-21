## HachathonHub-Frontend

HachathonHub is a Groq-powered AI companion delivering real-time health insights and recommendations. Leveraging a secure federated learning framework and Groq’s ultra-fast inference, HachathonHub ensures privacy, fairness, and seamless user experience in clinical and consumer health applications.

---

## 🚀 Problem Statement

Healthcare AI depends on large, diverse datasets to train models that generalize across different patient populations. However, strict privacy regulations (e.g., HIPAA, GDPR) prevent hospitals from sharing raw patient records, creating isolated "data silos". Models trained on narrow, homogeneous data sets often underrepresent minority groups, leading to biased predictions and unequal care outcomes.

Clinicians and patients also expect instantaneous AI-driven insights during consultations or at the point of care, but traditional cloud-based inference can introduce latency and disrupt workflows.

---

## 🔍 Understanding the Challenge

1. **Privacy & Compliance**: Hospitals cannot share raw patient data due to legal and ethical constraints, limiting access to diverse training data.
2. **Bias & Fairness**: Models trained on limited datasets may underperform for underrepresented groups, risking unequal care.
3. **Real-Time Performance**: Clinical workflows demand low-latency inference for seamless decision support, which conventional cloud solutions struggle to provide.

---

## 💡 HachathonHub’s Solution

### 1. Secure Federated Learning Framework
- **Local Training**: Participating hospitals train models on-premises using their own patient records.
- **Encrypted Aggregation**: Only encrypted model weight updates are shared with a central aggregator.
- **Global Model**: The aggregator combines updates via a privacy-preserving protocol and returns an improved global model without ever exposing raw data.

### 2. Groq-Powered Real-Time Inference
- **Ultra-Fast Inference**: Groq’s inference hardware (GroqCloud™/GroqRack™) processes large models (e.g., Llama-series) at hundreds of tokens per second.
- **Seamless UX**: Instantaneous analysis of patient inputs, medical images, or sensor data enables both clinical decision support and consumer-facing health apps.

**Combined Benefits:**
1. **Privacy**: Patients’ raw data stay on-premises; only encrypted model updates travel through the network.
2. **Fairness**: Training on heterogeneous, multi-institutional datasets reduces bias and improves generalization.
3. **Performance**: Real-time insights integrate smoothly into clinical workflows and mobile apps.

---

## ✨ Features

- **Federated Learning Pipeline**: Secure, scalable FL using Flower.
- **Real-Time Inference**: Powered by Groq API for sub-second response.
- **Model Management & Tracking**: Integrated with MLflow for performance monitoring.
- **Compliance by Design**: Meets HIPAA and GDPR requirements via encrypted weight aggregation.
- **Interactive Dashboard**: Visualize model performance, data contribution, and system health.

---

## 🛠 Tech Stack

- **Frontend**: Next.js, TypeScript, Tailwind CSS
- **Backend**: FastAPI (Python)
- **Database**: Supabase, AstraDB
- **Classical Models**: scikit-learn, TensorFlow
- **Federated Learning**: Flower
- **LLM & Inference**: Groq API, Hugging Face Spaces
- **Model Registry & Monitoring**: MLflow
- **Hosting**:
  - Frontend: Vercel
  - Model Serving: Hugging Face Spaces

---

## 📈 Data Flow Diagram

![Data Flow Diagram](docs/data_flow_diagram.png)

---

## 🏁 Getting Started

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Port-3000/HachathonHub-Frontend.git
   cd HachathonHub
   ```
2. **Configure your environment**:
   - Create a `.env.local` file in the `frontend` and `backend` directories with your API keys and database URLs.
3. **Install dependencies**:
   ```bash
   # Frontend
   cd frontend && npm install

   # Backend
   cd ../backend && pip install -r requirements.txt
   ```
4. **Run locally**:
   ```bash
   # Start backend
   uvicorn main:app --reload --port 8000

   # Start frontend
   cd ../frontend && npm run dev
   ```
5. **Access the app**:
   Visit `http://localhost:3000` for the frontend and `http://localhost:8000/docs` for the FastAPI docs.

---

## 🤝 Contributing

We welcome contributions! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

---

## ⚖️ License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

_Developed with ❤️ by the HachathonHub team._

