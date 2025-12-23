# 🏗️ Architecture Documentation

This document provides a comprehensive technical overview of the AI-Powered Ride Management System's architecture, design patterns, and implementation details.

---

## 📐 Table of Contents

1. [System Overview](#system-overview)
2. [Agent Architectures](#agent-architectures)
3. [Core Components](#core-components)
4. [Data Flow](#data-flow)
5. [Machine Learning Pipeline](#machine-learning-pipeline)
6. [RAG Implementation](#rag-implementation)
7. [Database Design](#database-design)
8. [API Integration](#api-integration)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    (CLI / Future: Web/API)                  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestrator                        │
│                      (LangGraph Core)                        │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │  ReAct   │  │Workflow  │  │  Router  │  │   State  │  │
│  │  Agent   │  │  Engine  │  │  Logic   │  │  Manager │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                        Tool Layer                            │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │ Booking  │  │Cancella- │  │  Active  │  │   RAG    │  │
│  │   Tool   │  │tion Tool │  │ Bookings │  │  System  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data & ML Layer                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │
│  │   JSON   │  │  K-Means │  │  FAISS   │  │Embedding │  │
│  │Database  │  │Clustering│  │  Vector  │  │  Models  │  │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │
└─────────────────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                 │
│  │   Groq   │  │LangSmith │  │HuggingFace                  │
│  │   LLM    │  │ Tracing  │  │ Embeddings                  │
│  └──────────┘  └──────────┘  └──────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Agent Architectures

### 1. Agentic V1: ReAct Pattern

**Philosophy**: Autonomous tool selection by LLM reasoning

```python
# Simplified agent loop
while not task_complete:
    # Reasoning Phase
    thought = llm.reason(current_state, available_tools)
    
    # Action Phase  
    tool, args = llm.select_tool(thought)
    result = execute_tool(tool, args)
    
    # Observation Phase
    current_state.update(result)
    
    # Decision
    task_complete = llm.should_finish(current_state)
```

**LangGraph Implementation:**

```python
from langgraph.graph import StateGraph, END

# Define state
class AgentState(TypedDict):
    messages: list[Message]
    next_action: str

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("agent", agent_reasoning_node)
workflow.add_node("booking", booking_tool_node)
workflow.add_node("cancel", cancellation_tool_node)
workflow.add_node("rag", rag_tool_node)

# Add edges
workflow.add_conditional_edges(
    "agent",
    route_to_tool,
    {
        "booking": "booking",
        "cancel": "cancel",
        "query": "rag",
        "finish": END
    }
)

# Compile
app = workflow.compile()
```

**Pros:**
- Maximum flexibility
- Natural conversation flow
- Self-correcting behavior

**Cons:**
- Higher token usage
- Less predictable
- Requires careful prompt engineering

---

### 2. Agentic V2: Instruction-Based

**Philosophy**: LLM generates structured commands; system executes them

```python
# Example execution
user_input = "Book me a ride to airport"

# LLM generates instruction
instruction = llm.generate_instruction(user_input)
# Returns: {"tool": "booking", "args": {"pickup": "current", "dropoff": "airport"}}

# System executes
result = tools[instruction["tool"]].execute(**instruction["args"])

# LLM formats response
response = llm.format_response(result)
```

**Key Difference:**
- Tool selection is done by LLM
- Execution is deterministic
- Better for debugging and testing

---

### 3. Workflow: Deterministic State Machine

**Philosophy**: Pre-defined paths with conditional branching

```python
# State machine definition
workflow = StateGraph(WorkflowState)

# Fixed sequence
workflow.add_edge(START, "authenticate")
workflow.add_edge("authenticate", "detect_intent")

# Conditional routing
workflow.add_conditional_edges(
    "detect_intent",
    lambda x: x["intent"],
    {
        "book": "process_booking",
        "cancel": "process_cancellation",
        "query": "handle_query",
        "list": "list_bookings"
    }
)

# Each path has fixed sequence
workflow.add_edge("process_booking", "confirm")
workflow.add_edge("confirm", END)
```

**Use Cases:**
- Production systems requiring deterministic behavior
- Compliance and auditing requirements
- Systems where conversation context is less important

---

## Core Components

### Booking Tool

**Functionality:** Create new ride bookings

**Input Schema:**
```python
class BookingRequest(BaseModel):
    rider_id: str = Field(pattern=r'^R\d{6}$')
    pickup_location: str
    dropoff_location: str  
    ride_type: Literal['UberX', 'UberXL', 'Uber Black', 'Uber Green']
    payment_method: Literal['card', 'cash', 'wallet']
```

**Processing Logic:**
1. Validate rider credentials
2. Check driver availability
3. Calculate estimated fare
4. Generate booking ID
5. Match with nearest driver
6. Store booking in database
7. Return confirmation

**Output:**
```json
{
  "booking_id": "BK789456",
  "driver": {
    "id": "D123456",
    "name": "Sarah Johnson",
    "rating": 4.9,
    "vehicle": "Toyota Camry",
    "eta_minutes": 5
  },
  "fare_estimate": 28.50,
  "status": "confirmed"
}
```

---

### Cancellation Tool

**Functionality:** Process ride cancellations with ML-based fee calculation

**ML Model Architecture:**

```
┌─────────────────┐
│  Feature Vector │
│  [8 dimensions] │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   K-Means       │
│   Clustering    │
│   (k=3)         │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Fee Category   │
│  0: Waived      │
│  1: Base        │
│  2: Enhanced    │
└─────────────────┘
```

**Feature Engineering:**

```python
def extract_features(booking, rider, driver):
    return [
        booking['wait_time_minutes'],
        int(booking['driver_arrived']),
        rider['rating'],
        driver['rating'],
        rider['cancellation_rate'],
        driver['cancellation_rate'],
        booking['time_to_pickup'],
        booking['surge_multiplier']
    ]
```

**Cluster Interpretation:**

| Cluster | Characteristics | Fee Decision |
|---------|-----------------|--------------|
| 0 | Early cancel, high ratings, rare cancellations | Waived |
| 1 | Normal cancel, average metrics | Base ($5) |
| 2 | Late cancel, low ratings, frequent cancellations | Enhanced ($10-15) |

**Model Training:**

```python
# Synthetic data generation
wait_times = np.random.gamma(2, 3, 10000)
ratings = np.random.normal(4.2, 0.8, 10000)
cancel_rates = np.random.exponential(0.05, 10000)

# Feature matrix
X = np.column_stack([wait_times, ratings, cancel_rates, ...])

# Train K-Means
kmeans = KMeans(n_clusters=3, random_state=42)
kmeans.fit(X)

# Save model
joblib.dump(kmeans, 'rider_cancels_model.pkl')
```

---

### Active Bookings Tool

**Functionality:** Query current ride status

**Database Schema:**
```json
{
  "bookings": {
    "BK789456": {
      "rider_id": "R123456",
      "driver_id": "D654321",
      "pickup": "Times Square",
      "dropoff": "JFK Airport",
      "status": "in_progress",
      "created_at": "2024-12-23T10:30:00Z",
      "fare": 45.00
    }
  }
}
```

**Query Methods:**
- By rider ID: List all active bookings for a rider
- By booking ID: Get specific booking details
- By status: Filter by status (pending, in_progress, completed, cancelled)

---

### RAG System

**Architecture:**

```
┌──────────────┐
│  PDF/Text    │
│  Documents   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Text Splitter│
│ (Recursive)  │
│ chunk=1000   │
│ overlap=200  │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Embeddings  │
│ HuggingFace  │
│ all-MiniLM   │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ FAISS Index  │
│ 384-dim      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Similarity  │
│   Search     │
│   (k=4)      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│     LLM      │
│  Synthesis   │
└──────────────┘
```

**Implementation:**

```python
# Document loading
from langchain.document_loaders import PDFLoader, TextLoader

loaders = [
    PDFLoader("policies.pdf"),
    TextLoader("faq.txt"),
    TextLoader("terms.txt")
]

docs = []
for loader in loaders:
    docs.extend(loader.load())

# Text splitting
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)

chunks = splitter.split_documents(docs)

# Embedding generation
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# FAISS index creation
from langchain.vectorstores import FAISS

vectorstore = FAISS.from_documents(chunks, embeddings)
vectorstore.save_local("vector_store")

# Query processing
def query_rag(question: str) -> str:
    # Retrieve relevant chunks
    docs = vectorstore.similarity_search(question, k=4)
    
    # Construct prompt
    context = "\n\n".join([doc.page_content for doc in docs])
    prompt = f"""
    Based on the following context, answer the question.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:
    """
    
    # LLM generation
    response = llm.invoke(prompt)
    return response
```

---

## Data Flow

### Booking Flow

```
┌──────┐
│ User │
└───┬──┘
    │ "Book ride to airport"
    ▼
┌─────────────┐
│   Agent     │
│  Reasoning  │
└─────┬───────┘
      │ Tool: booking
      │ Args: {pickup, dropoff}
      ▼
┌─────────────┐
│  Booking    │
│   Tool      │
└─────┬───────┘
      │
      ▼
┌─────────────┐    ┌─────────────┐
│  Validate   │───▶│   Match     │
│   Input     │    │   Driver    │
└─────────────┘    └─────┬───────┘
                         │
                         ▼
                   ┌─────────────┐
                   │  Calculate  │
                   │    Fare     │
                   └─────┬───────┘
                         │
                         ▼
                   ┌─────────────┐
                   │    Store    │
                   │   Booking   │
                   └─────┬───────┘
                         │
                         ▼
                   ┌─────────────┐
                   │   Return    │
                   │Confirmation │
                   └─────────────┘
```

### Cancellation Flow

```
┌──────┐
│ User │
└───┬──┘
    │ "Cancel booking BK123"
    ▼
┌─────────────┐
│  Retrieve   │
│  Booking    │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Extract   │
│  Features   │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   K-Means   │
│  Clustering │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│  Determine  │
│     Fee     │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Process   │
│   Refund    │
└─────┬───────┘
      │
      ▼
┌─────────────┐
│   Update    │
│   Status    │
└─────────────┘
```

---

## Machine Learning Pipeline

### Data Generation

**Purpose:** Create realistic synthetic data for model training

**Distribution Strategies:**

1. **Rider Ratings:**
   - Skewed normal distribution
   - μ = 4.2, σ = 0.8
   - Range: [1.0, 5.0]

```python
ratings = np.clip(
    np.random.normal(4.2, 0.8, 10000),
    1.0, 5.0
)
```

2. **Wait Times:**
   - Gamma distribution (shape=2, scale=3)
   - Models realistic wait time patterns

```python
wait_times = np.random.gamma(2, 3, 10000)
```

3. **Cancellation Rates:**
   - Exponential distribution (λ=0.05)
   - Most users cancel rarely, some cancel frequently

```python
cancel_rates = np.random.exponential(0.05, 10000)
```

### Model Training Process

```python
# 1. Feature engineering
features = create_feature_matrix(raw_data)

# 2. Normalization
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)

# 3. Optimal k selection (Elbow method)
inertias = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(features_scaled)
    inertias.append(kmeans.inertia_)

optimal_k = find_elbow(inertias)  # k=3

# 4. Final model training
model = KMeans(n_clusters=3, random_state=42)
model.fit(features_scaled)

# 5. Cluster labeling
labels = model.labels_
cluster_stats = analyze_clusters(features, labels)

# 6. Fee mapping
fee_map = assign_fees_to_clusters(cluster_stats)

# 7. Model persistence
joblib.dump(model, 'cancellation_model.pkl')
joblib.dump(scaler, 'feature_scaler.pkl')
joblib.dump(fee_map, 'fee_mapping.pkl')
```

---

## Database Design

### JSON-Based Storage

**Structure:**

```
data/
├── riders.json      # User profiles
├── drivers.json     # Driver profiles
├── bookings.json    # Active/historical bookings
└── cancellations.json  # Cancellation records
```

**Schema Examples:**

**riders.json:**
```json
{
  "R123456": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "rating": 4.8,
    "total_rides": 127,
    "cancellation_rate": 0.03,
    "payment_methods": ["card_1234", "wallet"],
    "created_at": "2023-01-15T00:00:00Z"
  }
}
```

**bookings.json:**
```json
{
  "BK789456": {
    "rider_id": "R123456",
    "driver_id": "D654321",
    "pickup": {
      "address": "123 Main St",
      "lat": 40.7128,
      "lon": -74.0060
    },
    "dropoff": {
      "address": "456 Airport Rd",
      "lat": 40.6413,
      "lon": -73.7781
    },
    "ride_type": "UberX",
    "status": "in_progress",
    "fare": 45.00,
    "created_at": "2024-12-23T10:30:00Z",
    "started_at": "2024-12-23T10:35:00Z"
  }
}
```

**Advantages:**
- Simple to implement
- Easy to inspect and debug
- No database server required
- Git-friendly for version control

**Limitations:**
- Not suitable for high concurrency
- No transaction support
- Limited query capabilities

**Production Alternative:**
For production systems, consider:
- PostgreSQL for relational data
- MongoDB for document storage
- Redis for caching and session management

---

## API Integration

### Groq LLM API

**Configuration:**

```python
from langchain_groq import ChatGroq

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.7,
    max_tokens=1024,
    api_key=os.getenv("GROQ_API_KEY")
)
```

**Usage Patterns:**

1. **Agent Reasoning:**
```python
response = llm.invoke([
    SystemMessage(content=system_prompt),
    HumanMessage(content=user_input)
])
```

2. **Tool Selection:**
```python
response = llm.bind_tools(tools).invoke(messages)
tool_calls = response.tool_calls
```

3. **RAG Synthesis:**
```python
prompt = rag_prompt.format(context=context, query=query)
answer = llm.invoke(prompt)
```

### LangSmith Tracing

**Instrumentation:**

```python
from langsmith import Client

client = Client(api_key=os.getenv("LANGSMITH_API_KEY"))

# Automatic tracing
with tracing_v2_enabled(project_name="ride-agent"):
    result = agent.invoke({"input": user_query})
```

**Metrics Collected:**
- Token usage per request
- Latency for each component
- Tool invocation frequency
- Error rates and types
- User satisfaction scores

---

## Performance Considerations

### Optimization Strategies

1. **Caching:**
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_driver_info(driver_id):
    return load_from_db(driver_id)
```

2. **Batch Processing:**
```python
# Embed multiple documents at once
embeddings = model.embed_documents(chunks)  # Vectorized
```

3. **Async Operations:**
```python
async def process_booking(request):
    driver, fare = await asyncio.gather(
        find_driver_async(request),
        calculate_fare_async(request)
    )
    return create_booking(driver, fare)
```

### Scalability Roadmap

**Current (MVP):**
- Single-threaded execution
- JSON file storage
- Synchronous tool calls

**Phase 1 (Production):**
- Multi-threaded request handling
- PostgreSQL database
- Redis caching layer

**Phase 2 (Scale):**
- Microservices architecture
- Kubernetes deployment
- Load balancing
- Message queues (RabbitMQ/Kafka)

---

## Security Considerations

### Current Implementation

1. **Input Validation:** Pydantic models
2. **API Key Management:** Environment variables
3. **User Authentication:** Simple ID-based (demo)

### Production Requirements

1. **Authentication:**
   - JWT tokens
   - OAuth 2.0 integration
   - Session management

2. **Authorization:**
   - Role-based access control (RBAC)
   - Resource-level permissions

3. **Data Protection:**
   - Encryption at rest (AES-256)
   - TLS for data in transit
   - PII anonymization

4. **Rate Limiting:**
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@limiter.limit("10/minute")
def api_endpoint():
    pass
```

---

## Testing Strategy

### Unit Tests

```python
def test_booking_validation():
    request = BookingRequest(
        rider_id="INVALID",
        pickup="Location A",
        dropoff="Location B"
    )
    with pytest.raises(ValidationError):
        validate_booking(request)
```

### Integration Tests

```python
def test_full_booking_flow():
    result = agent.invoke({
        "input": "Book ride to airport"
    })
    assert result["booking_id"].startswith("BK")
    assert result["status"] == "confirmed"
```

### Load Tests

```python
from locust import HttpUser, task

class AgentUser(HttpUser):
    @task
    def book_ride(self):
        self.client.post("/book", json={
            "pickup": "Location A",
            "dropoff": "Location B"
        })
```

---

## Monitoring & Observability

### Metrics to Track

1. **Performance:**
   - Average response time
   - P95, P99 latencies
   - Token usage per request

2. **Business:**
   - Bookings per hour
   - Cancellation rate
   - Average fare

3. **Quality:**
   - Tool selection accuracy
   - RAG relevance scores
   - User satisfaction ratings

### Alerting Rules

```yaml
alerts:
  - name: HighLatency
    condition: p95_latency > 5000ms
    action: notify_team
  
  - name: HighErrorRate
    condition: error_rate > 5%
    action: page_oncall
```

---

## Future Enhancements

1. **Multi-Modal Support:**
   - Voice interface integration
   - Image-based location selection

2. **Advanced ML:**
   - Demand prediction models
   - Dynamic pricing optimization
   - Driver matching algorithms

3. **Real-time Features:**
   - Live location tracking
   - WebSocket connections
   - Push notifications

4. **Analytics Dashboard:**
   - Real-time metrics
   - Business intelligence
   - A/B testing framework

---

<div align="center">

[← Back to README](./README.md) | [Setup Guide →](./SETUP.md)

**For questions or contributions, open an issue on GitHub**

</div>
