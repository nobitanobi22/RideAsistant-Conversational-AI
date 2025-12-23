# 🚖 AI-Powered Ride Management System

> An intelligent, multi-agent conversational platform for autonomous ride-hailing operations powered by LangGraph, LangChain, and Large Language Models

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-brightgreen.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Overview

This project demonstrates an advanced **agentic AI framework** that simulates a complete ride-hailing platform similar to Uber. It showcases modern AI orchestration patterns, retrieval-augmented generation (RAG), and machine learning-based decision systems.

### Key Capabilities

- 🎯 **Intelligent Ride Booking** - Natural language ride requests with location understanding
- 💰 **Smart Cancellation Processing** - ML-driven fee calculation using unsupervised clustering
- 📋 **Active Ride Management** - Real-time booking status and ride tracking
- 💬 **Context-Aware Q&A** - RAG-powered knowledge retrieval for policy and support queries

## 🏗️ Architecture Variants

The project includes three distinct implementation approaches:

### 🤖 Agentic V1: ReAct Agent Pattern
- LLM-driven decision making with tool selection
- LangGraph orchestrated autonomous agent
- Dynamic tool invocation based on conversation context

### 🎯 Agentic V2: Instruction-Based Execution  
- LLM generates explicit tool execution instructions
- Manual tool triggering with structured commands
- Enhanced controllability and debugging

### 🔄 Workflow: Deterministic Flow
- Pre-defined state machine for task execution
- LangGraph nodes and edges define fixed paths
- LLM only used for RAG retrieval operations

> **Quick Start**: See [SETUP.md](./SETUP.md) for Docker deployment instructions

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **LLM Orchestration** | LangGraph, LangChain, Groq API |
| **Vector Store** | FAISS (Facebook AI Similarity Search) |
| **Embeddings** | HuggingFace Transformers |
| **ML Clustering** | Scikit-learn K-Means |
| **Data Validation** | Pydantic v2 |
| **Development** | LangSmith (tracing), LangGraph Studio (debugging) |
| **Data Storage** | JSON-based persistence layer |
| **Synthetic Data** | NumPy probabilistic distributions |

---

## 📐 System Design

### Agent Architecture (V1)

The ReAct agent uses a reasoning-action loop where the LLM:
1. Observes the current state and user input
2. Reasons about which tool to invoke
3. Executes the selected tool
4. Observes the result and continues or completes

```
[User Input] → [Agent Reasoning] → [Tool Selection] → [Tool Execution] → [Result Processing] → [Response]
                       ↑                                                           ↓
                       └─────────────────────[Feedback Loop]──────────────────────┘
```

![Agent Flow Diagram](docs/images/agent-architecture.png)

### Workflow Architecture

The workflow system uses deterministic state transitions:

```
[Entry] → [Auth] → [Intent Detection] → [Tool Router] → [Execution] → [Response] → [Exit]
```

![Workflow Diagram](docs/images/workflow-architecture.png)

---

## 🔧 Core Components

### 1. Booking Engine
- Processes ride requests with pickup and destination
- Validates locations and matches with available drivers
- Generates unique booking IDs and confirmation details

### 2. Cancellation Processor  
Uses an **unsupervised K-Means clustering model** trained on:
- Driver arrival status and wait time
- Rider/Driver historical ratings
- Past cancellation patterns
- Time of day and surge pricing factors

**Cancellation Fee Categories:**
- ✅ Fee Waived - Early cancellations, driver delays
- 💵 Base Fee - Standard cancellations  
- 💵💵 Enhanced Fee - Late cancellations, repeated patterns

![Clustering Analysis](docs/images/cancellation-clusters.png)

### 3. Active Ride Management
- Real-time booking status queries
- JSON-based datastore for ride state
- Efficient lookup by rider ID or booking ID

### 4. RAG Knowledge System

**Document Processing Pipeline:**
```
PDF/Text Docs → Text Splitting → Embedding Generation → FAISS Index → Similarity Search → LLM Synthesis
```

The RAG system handles queries about:
- Platform policies and terms of service
- Payment and refund procedures  
- Safety guidelines and emergency protocols
- Feature explanations and how-to guides

---

## 📊 Machine Learning Model

### Dataset Generation

Synthetic datasets created using statistical distributions to simulate realistic user behavior:

- **Rating Distribution**: Skewed normal distribution (μ=4.2, σ=0.8)
- **Cancellation Patterns**: Gamma distribution modeling time-based behavior
- **Wait Times**: Exponential distribution for realistic delays

![Rating Distribution](docs/images/rating-distribution.png)

### Clustering Model Training

```python
# Features used for cancellation fee clustering
features = [
    'wait_time_minutes',
    'driver_arrived',
    'rider_rating',
    'driver_rating', 
    'rider_cancellation_rate',
    'driver_cancellation_rate',
    'time_to_pickup'
]

# K-Means with optimal k=3 clusters
model = KMeans(n_clusters=3, random_state=42)
```

![Cluster Analysis](docs/images/cluster-visualization.png)

---

## 🔍 Observability

### LangSmith Integration
- Trace every agent decision and tool invocation
- Measure latency and token usage per operation
- Debug conversation flows and failure points

### LangGraph Studio
- Visual graph representation of agent flows
- Step-through debugging of state transitions
- Real-time monitoring of node executions

---

## 🔒 Security & Validation

### Pydantic Models
All inputs validated using strict schemas:

```python
class RideBooking(BaseModel):
    rider_id: str = Field(..., pattern=r'^R\d{6}$')
    pickup_location: str = Field(..., min_length=3)
    dropoff_location: str = Field(..., min_length=3)
    ride_type: Literal['UberX', 'UberXL', 'Uber Black']
```

### Authentication
- User registration with email validation
- Driver verification with license checks
- Session-based authentication for API calls

---

## 📁 Project Structure

```
├── agenticV1/          # ReAct agent implementation
├── agenticV2/          # Instruction-based agent  
├── agenticV3/          # Enhanced V1 with improvements
├── workflow/           # Deterministic workflow system
├── docs/
│   └── images/         # Architecture diagrams (your custom images go here)
├── Data_Generation/    # Synthetic dataset scripts
├── RAG/               # Vector store and retrieval logic
├── cancelation_models/ # K-Means clustering models
├── README.md          # This file
├── SETUP.md           # Installation and deployment guide
├── ARCHITECTURE.md    # Detailed technical documentation
└── .env.example       # Environment configuration template
```

---

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+ installed
- Groq API key (free tier available at [groq.com](https://groq.com))

### Deploy with Docker

```bash
# Pull the latest image
docker pull your-dockerhub-username/ride-agent:latest

# Run with API key
docker run --rm -it \
  -e GROQ_API_KEY=your_groq_key_here \
  your-dockerhub-username/ride-agent:latest
```

For detailed setup instructions, see **[SETUP.md](./SETUP.md)**

---

## 💡 Example Interactions

**Booking a Ride:**
```
User: I need a ride from Downtown Plaza to Airport Terminal 3
Agent: I'll book an UberX for you. Estimated arrival: 5 minutes. Fare: $28.50. Confirm?
User: Yes
Agent: ✅ Booking confirmed! Booking ID: BK789456. Driver: Sarah (4.9⭐) arriving in 5 mins.
```

**Cancellation Query:**
```
User: I need to cancel booking BK789456
Agent: Analyzing your cancellation... Driver hasn't arrived yet and booking was made 2 minutes ago.
       ✅ Cancellation fee waived. Refund processed. Booking BK789456 cancelled.
```

**Policy Question (RAG):**
```
User: What's your refund policy?
Agent: According to our terms: Cancellations before driver arrival are fully refunded. After driver 
       arrival, cancellation fees apply based on wait time. Standard fee is $5, increased to $10 
       after 5 minutes of driver waiting. [Source: Terms of Service, Section 8.2]
```

---

## 📚 Documentation

- [Setup Guide](./SETUP.md) - Installation and configuration
- [Architecture Deep Dive](./ARCHITECTURE.md) - Technical implementation details
- [API Documentation](./docs/API.md) - Tool schemas and endpoints
- [Model Training](./docs/MODEL_TRAINING.md) - Clustering model methodology

---

## 🤝 Contributing

Contributions are welcome! This project is designed as an educational resource for learning about:
- Agent-based AI systems
- LangGraph orchestration patterns
- RAG implementation
- ML model integration in production systems

Please feel free to:
- Open issues for bugs or questions
- Submit pull requests for improvements
- Fork and experiment with your own variations

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [LangChain](https://www.langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/)
- Powered by [Groq](https://groq.com/) inference
- Inspired by real-world ride-hailing platforms

---

## 📧 Contact

For questions or collaboration opportunities, feel free to reach out:

- **GitHub**: nobitanobi22
- **Email**: kankita32v901@gmail.com
- **LinkedIn**: https://www.linkedin.com/in/kumari-ankita-31b2bb250

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Built with ❤️ 

</div>
