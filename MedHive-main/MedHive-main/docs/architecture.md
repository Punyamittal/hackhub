# HachathonHub Architecture

## System Architecture Diagram

```
+------------------------+     +---------------------------+
|     Next.js Frontend   |     |   Frontend Components     |
|   +-----------------+  |     |  +-----------------+      |
|   |  Landing Page   |  |     |  |    Chatbot     |      |
|   +-----------------+  |     |  +-----------------+      |
|   |  Admin Portal   |  |     |  |   Model Hub    |      |
|   +-----------------+  |     |  +-----------------+      |
|   | Contributor UI  |  |     |  | User Dashboard |      |
|   +-----------------+  |     |  +-----------------+      |
+------------------------+     +---------------------------+
           |                                |
           v                                v
+----------------------------------------------------------+
|                  REST API (FastAPI)                      |
|   +-------------------+       +--------------------+     |
|   | Authentication    |       | Chatbot API        |     |
|   +-------------------+       +--------------------+     |
|   | User Management   |       | Model Inference    |     |
|   +-------------------+       +--------------------+     |
|   | FL Coordination   |       | Data Processing    |     |
|   +-------------------+       +--------------------+     |
+----------------------------------------------------------+
         |             |                |           |
         v             v                v           v
 +---------------+ +------------+ +------------+ +------------+
 | PostgreSQL DB | |  AstraDB   | |   Groq    | |  MLflow    |
 |   (Supabase)  | |  (Vector)  | |   API     | |  Tracking  |
 +---------------+ +------------+ +------------+ +------------+
         |             |                            |
         v             v                            v
 +----------------------------------------------------+
 |              Federated Learning System             |
 |  +------------------+  +---------------------+     |
 |  | Flower Server    |  | Model Aggregation  |     |
 |  +------------------+  +---------------------+     |
 |  | Client Management|  | Model Distribution |     |
 |  +------------------+  +---------------------+     |
 +----------------------------------------------------+
                              |
                              v
 +----------------------------------------------------+
 |               Model Deployment                      |
 |  +------------------+  +---------------------+     |
 |  | Hugging Face     |  | Model Monitoring   |     |
 |  | Spaces           |  |                    |     |
 |  +------------------+  +---------------------+     |
 +----------------------------------------------------+
```

## Data Flow Diagram

```
+------------------+        +-----------------+        +------------------+
| End User         |        | Data Provider   |        | Contributor      |
| (Patients,       |        | (Hospitals,     |        | (Computing       |
|  Healthcare      |<------>| Research        |<------>| Resources        |
|  Professionals)  |        | Centers)        |        | Providers)       |
+------------------+        +-----------------+        +------------------+
        |                         |                           |
        v                         v                           v
+----------------------------------------------------------+
|                        HachathonHub Platform                   |
+----------------------------------------------------------+
        |                         |                           |
        v                         v                           v
+------------------+     +-----------------+      +------------------+
| Query Processing |     | Secure Data     |      | Model Training   |
| & RAG System     |     | Storage &       |      | & Validation     |
| (Groq + AstraDB) |     | Management      |      | (Federated)      |
+------------------+     +-----------------+      +------------------+
        |                         |                           |
        v                         v                           v
+----------------------------------------------------------+
|                Global Model Aggregation                   |
|                 & Performance Tracking                    |
+----------------------------------------------------------+
        |                         |                           |
        v                         v                           v
+------------------+     +-----------------+      +------------------+
| Model Deployment |     | Admin           |      | Health Insights  |
| (Hugging Face)   |     | Monitoring      |      | & Recommendations|
+------------------+     +-----------------+      +------------------+
```

## Component Interactions

1. **User Authentication Flow:**
   - User signs up/logs in → Frontend → Auth API → Database → JWT Token → Frontend

2. **Chatbot Interaction Flow:**
   - User query → Frontend Chatbot → Backend API → Groq LLM API → Response → Frontend

3. **Federated Learning Flow:**
   - Data Provider uploads data → Stored locally
   - FL Server initiates training round → Contributors receive model
   - Local training at Contributors → Encrypted weights shared back
   - Model aggregation at FL Server → Performance evaluation
   - Admin reviews results → Model deployment if approved

4. **Model Inference Flow:**
   - User selects model → Frontend → API → Model Inference → Results displayed

## Database Schema Relationships

```
Role (1) -----< User (*)
User (1) -----< Dataset (*)
User (1) -----< MLModel (*)
User (1) -----< FLParticipant (*)
User (1) -----< ChatHistory (*)
MLModel (1) -----< FLRound (*)
MLModel (1) -----< ModelPerformance (*)
FLRound (1) -----< FLParticipant (*)
FLRound (1) -----< ModelPerformance (*)
Dataset (1) -----< ModelPerformance (*)
```

## Security Considerations

1. **Data Privacy:**
   - Raw patient data never leaves the data provider
   - Only model weights are shared, not the underlying data
   - Encryption of all model weights during transmission

2. **Authentication & Authorization:**
   - JWT-based authentication
   - Role-based access control
   - Strict permission management for sensitive operations

3. **Secure Communications:**
   - HTTPS for all API communications
   - Encrypted database connections
   - API key rotation for external services

## Scalability Considerations

1. **Horizontal Scaling:**
   - Stateless backend services can be scaled horizontally
   - Database read replicas for high query loads

2. **Performance Optimization:**
   - Caching for common queries and responses
   - Asynchronous processing for heavy computational tasks
   - Background job queues for model training

3. **Cost Management:**
   - Efficient resource utilization during FL training
   - Optimization of external API calls (Groq)
   - Proper database indexing and query optimization 