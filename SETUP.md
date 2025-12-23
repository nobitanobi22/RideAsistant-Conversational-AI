# 🚀 Setup Guide - Deployment Instructions

This guide will walk you through deploying the AI-Powered Ride Management System using Docker.

---

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Docker** installed on your system
   - [Install Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/Mac)
   - [Install Docker Engine](https://docs.docker.com/engine/install/) (Linux)
   - Verify installation: `docker --version`

2. **API Keys** (all free tier available):
   - **Groq API Key** (Required) - Get it from [console.groq.com](https://console.groq.com)
   - **LangSmith API Key** (Optional) - For monitoring/tracing: [smith.langchain.com](https://smith.langchain.com)

---

## 🐳 Method 1: Docker Hub Image (Recommended)

### Step 1: Pull the Pre-Built Image

```bash
docker pull your-dockerhub-username/ride-agent:latest
```

### Step 2: Run the Container

**Option A: Pass API Keys Directly (Quick Start)**

```bash
docker run --rm -it \
  -e GROQ_API_KEY=your_groq_api_key_here \
  -e LANGSMITH_API_KEY=your_langsmith_key_here \
  your-dockerhub-username/ride-agent:latest
```

**Option B: Use Environment File (Recommended for Production)**

1. Create a `.env` file in your working directory:

```bash
# .env file
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxx
LANGSMITH_API_KEY=ls_xxxxxxxxxxxxxxxxxxxxx
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=ride-agent-production
```

2. Run with the env file:

```bash
docker run --rm -it \
  --env-file .env \
  your-dockerhub-username/ride-agent:latest
```

### Step 3: Interact with the Agent

Once the container starts, you'll see a welcome message. You can now interact with the chatbot:

```
🚖 Welcome to Ride Management Agent!
Type 'exit' to quit.

You: I need a ride from Times Square to JFK Airport
Agent: I'll help you book that ride...
```

---

## 🛠️ Method 2: Build from Source

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/ride-agent.git
cd ride-agent
```

### Step 2: Configure Environment

Copy the example environment file and add your keys:

```bash
cp .env.example .env
nano .env  # or use any text editor
```

Update the `.env` file:

```bash
GROQ_API_KEY=your_groq_key_here
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=my-ride-agent
```

### Step 3: Choose Your Version

The project includes multiple implementations:

- **agenticV1/** - ReAct agent (recommended for learning)
- **agenticV2/** - Instruction-based agent
- **agenticV3/** - Enhanced V1 with improvements (recommended for production)
- **workflow/** - Deterministic workflow system

Navigate to your chosen version:

```bash
cd agenticV3  # or agenticV1, agenticV2, workflow
```

### Step 4: Build the Docker Image

```bash
docker build -t ride-agent:local .
```

### Step 5: Run Your Local Build

```bash
docker run --rm -it \
  --env-file .env \
  ride-agent:local
```

---

## 🐍 Method 3: Local Python Development

For development and testing without Docker:

### Step 1: Set Up Python Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
cd agenticV3  # or your chosen version
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 4: Run the Application

```bash
python main.py
```

---

## ⚙️ Configuration Options

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `GROQ_API_KEY` | ✅ Yes | Groq LLM API key | - |
| `LANGSMITH_API_KEY` | ❌ No | LangSmith tracing key | - |
| `LANGSMITH_TRACING_V2` | ❌ No | Enable LangSmith tracing | `false` |
| `LANGSMITH_PROJECT` | ❌ No | LangSmith project name | `default` |

### Model Selection

You can specify different Groq models by modifying the configuration:

```python
# In graph.py or main.py
model = "llama-3.3-70b-versatile"  # Default
# or
model = "mixtral-8x7b-32768"       # Alternative
```

Available models:
- `llama-3.3-70b-versatile` (recommended)
- `llama-3.1-70b-versatile`
- `mixtral-8x7b-32768`
- `gemma-7b-it`

---

## 🧪 Testing the Installation

### 1. Test Booking Functionality

```
You: Book a ride from Central Park to Brooklyn Bridge
```

Expected output: Booking confirmation with details

### 2. Test Cancellation System

```
You: Cancel booking BK123456
```

Expected output: Cancellation processed with fee information

### 3. Test RAG Knowledge Base

```
You: What's your cancellation policy?
```

Expected output: Detailed policy from knowledge base

### 4. Test Active Bookings

```
You: Show my active bookings
```

Expected output: List of current rides (if any)

---

## 🔧 Troubleshooting

### Issue: "API key not found"

**Solution:** Verify your `.env` file or environment variables are correctly set.

```bash
# Check if variable is set
echo $GROQ_API_KEY

# If using Docker, verify the env file path
docker run --rm -it --env-file /full/path/to/.env ride-agent:latest
```

### Issue: "Module not found" errors

**Solution:** Ensure all dependencies are installed:

```bash
pip install -r requirements.txt --upgrade
```

### Issue: "FAISS index not found"

**Solution:** The RAG system needs to build the vector index on first run:

```bash
cd RAG
python indexing.py
```

### Issue: Docker container exits immediately

**Solution:** Run in interactive mode with `-it` flags and check logs:

```bash
docker run --rm -it your-dockerhub-username/ride-agent:latest
# or
docker logs container_id
```

### Issue: Slow response times

**Solution:** This is usually due to:
- Cold start of Groq API (first request is slower)
- Network latency
- Large document retrieval in RAG

Consider using a local embedding model or caching for faster responses.

---

## 📊 Monitoring with LangSmith

To enable detailed tracing and monitoring:

1. Sign up for [LangSmith](https://smith.langchain.com)
2. Create a new project
3. Get your API key from settings
4. Add to your `.env`:

```bash
LANGSMITH_API_KEY=ls_xxxxxxxxxxxxxxxxxxxxx
LANGSMITH_TRACING_V2=true
LANGSMITH_PROJECT=my-ride-agent
```

5. View traces at [smith.langchain.com](https://smith.langchain.com)

---

## 🐛 Debugging with LangGraph Studio

For visual debugging of agent flows:

1. Install LangGraph Studio (separate application)
2. Open your project in the studio
3. View real-time graph execution
4. Set breakpoints and inspect state

[Download LangGraph Studio](https://github.com/langchain-ai/langgraph-studio)

---

## 🔄 Updating the Application

### Pull Latest Docker Image

```bash
docker pull your-dockerhub-username/ride-agent:latest
```

### Update Source Code

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

## 🗑️ Cleanup

### Remove Docker Images

```bash
# List images
docker images | grep ride-agent

# Remove specific image
docker rmi ride-agent:latest

# Remove all unused images
docker image prune -a
```

### Remove Python Virtual Environment

```bash
deactivate  # if activated
rm -rf venv
```

---

## 🆘 Getting Help

If you encounter issues not covered here:

1. Check the [Issues](https://github.com/your-username/ride-agent/issues) page
2. Review [ARCHITECTURE.md](./ARCHITECTURE.md) for technical details
3. Open a new issue with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Docker version, Python version)

---

## 📚 Next Steps

After successful setup:

- ✅ Read [ARCHITECTURE.md](./ARCHITECTURE.md) to understand the system design
- ✅ Explore different agent versions (V1, V2, V3, workflow)
- ✅ Customize the system prompts in `system_prompts.txt`
- ✅ Train your own cancellation clustering model with custom data
- ✅ Extend the RAG knowledge base with your own documents

---

<div align="center">

**🎉 Setup Complete! Ready to explore AI-powered ride management! 🎉**

[← Back to README](./README.md) | [Architecture Guide →](./ARCHITECTURE.md)

</div>
