# 🤖 CCI Colombia Agent

**Bilingual conversational agent for CCI France-Colombia member needs assessment with Redis persistence and WhatsApp contact integration**

A sophisticated LangChain-powered agent that conducts personalized questionnaires while providing intelligent RAG-based responses about CCI services and information. Features Redis-backed state persistence and intelligent client context enrichment.

## ✨ Features

- **🎯 Structured Questionnaire**: 7 sequential questions for CCI member needs assessment
- **🧠 RAG Intelligence**: Answers questions using Pinecone vector database + OpenAI
- **🌍 Bilingual Support**: Automatic French/Spanish language detection and adaptation
- **💬 Conversational Memory**: Maintains context across multi-turn conversations
- **📱 WhatsApp Ready**: Stateless architecture with Redis persistence for WhatsApp deployment
- **🎨 Interactive Testing**: Streamlit interface for easy testing and validation
- **📊 Contact Integration**: Automatic client context enrichment from Excel database
- **⚡ Performance Optimized**: Sub-8s response times for Manychat compatibility
- **🔄 Redis Persistence**: Production-ready state management with Redis Cloud support

## 🏗️ Architecture

- **Agent Framework**: LangChain with OpenAI Tools Agent
- **LLM**: OpenAI GPT-4o (conversation) + GPT-4o-mini (RAG reformulation)
- **Memory**: ConversationSummaryBufferMemory for efficient context management
- **Vector Database**: Pinecone with text-embedding-3-small
- **State Management**: Redis-backed persistence with memory fallback
- **Tools**: Modular tool system (RAG search, question tracking, contact lookup)
- **Contact Management**: Excel-based client database with phone number lookup

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone <repository>
cd CCI_colombia_agent
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file with:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...

# Pinecone Configuration  
PINECONE_API_KEY=...
PINECONE_INDEX=...

# Redis Configuration (Redis Cloud recommended)
REDIS_URL=redis://default:password@host:port/db
# OR individual parameters:
# REDIS_HOST=localhost
# REDIS_PORT=6379
# REDIS_PASSWORD=your_password
# REDIS_DB=0

# Optional Redis settings
REDIS_SESSION_TTL=86400
REDIS_KEY_PREFIX=cci_agent:

# WhatsApp Contacts Database (optional)
CONTACTS_EXCEL_PATH=whatsapp_contact/Base de datos proyecto IA (1).xlsx
```

### 3. Test the Agent

**Redis Integration Test:**
```bash
python test/test_redis.py
```

**Interactive Agent Test:**
```bash
python test/test_langchain_agent.py
```

**Streamlit Web Interface:**
```bash
streamlit run streamlit_app.py
```

**Performance Test:**
```bash
python performance_test.py
```

## 💻 Usage Examples

### Basic Conversation with Redis Persistence

```python
from app.agents.whatsapp_handler import whatsapp_chat, get_user_status

# Start conversation (state automatically saved to Redis)
response = await whatsapp_chat(
    user_id="whatsapp:+1234567890",
    user_input="Bonjour, je suis prêt"
)

# Check user status 
status = await get_user_status("whatsapp:+1234567890")
print(f"Question: {status['current_question']}, Language: {status['language']}")

# Continue conversation (state automatically restored)
response = await whatsapp_chat(
    user_id="whatsapp:+1234567890", 
    user_input="Oui, j'ai accédé à l'espace membre"
)
```

### Agent with Client Context Enrichment

```python
from app.agents.langchain_agent import CCILangChainAgent

# Create agent
agent = CCILangChainAgent()

# Set client context for personalized responses
client_info = {
    "empresa": "TechCorp SAS",
    "nombre": "Juan",
    "apellido": "Pérez", 
    "cargo": "CEO",
    "sector": "Tecnología",
    "descripcion": "Startup de fintech"
}
agent.set_client_context(client_info)

# Agent will now personalize responses based on client profile
response = await agent.chat("¿Qué servicios me recomiendan?")
```

### Contact Database Integration

```python
from whatsapp_contact.contacts_manager import get_contacts_manager

# Load contacts database
contacts_manager = get_contacts_manager()
contacts_manager.load_contacts('path/to/contacts.xlsx')

# Find contact by phone
contact = contacts_manager.find_contact_by_phone("+573001234567")
if contact:
    print(f"Found: {contact['empresa']} - {contact['nombre']}")
```

## 🧪 Testing

### Comprehensive Test Suite

```bash
# Redis integration test
python test/test_redis.py

# Agent functionality test  
python test/test_langchain_agent.py

# WhatsApp handler test
python test/test_whatsapp_chat.py

# Simple conversation test
python test/test_conversation_simple.py

# Performance benchmark
python performance_test.py
```

### Streamlit Interface

```bash
streamlit run streamlit_app.py
```

Features:
- Real-time conversation testing
- Agent status monitoring  
- Conversation reset functionality
- User ID management
- Redis connection status

## 📁 Project Structure

```
CCI_colombia_agent/
├── app/
│   └── agents/                    # Core agent system
│       ├── langchain_agent.py     # Main LangChain agent class
│       ├── redis_manager.py       # Redis state persistence
│       ├── whatsapp_handler.py    # Stateless WhatsApp wrapper
│       ├── language/              # Language detection system
│       │   ├── language_manager.py
│       │   └── language.py
│       ├── prompts/               # System prompts
│       │   ├── prompt_fr.txt      # French prompts
│       │   ├── prompt_es.txt      # Spanish prompts
│       │   ├── prompt_manager.py  # Dynamic prompt builder
│       │   └── prompts_utils.py   # Prompt loading utilities
│       └── tools/                 # Agent tools
│           ├── tools.py           # Agent tools (RAG, tracking)
│           └── rag.py             # RAG implementation
├── whatsapp_contact/              # Contact management
│   └── contacts_manager.py        # Excel-based contact database
├── test/                          # Test suite
│   ├── test_redis.py             # Redis integration tests
│   ├── test_langchain_agent.py   # Agent functionality tests
│   ├── test_whatsapp_chat.py     # WhatsApp handler tests
│   └── test_conversation_simple.py # Basic conversation tests
├── performance_test.py            # Performance benchmarking
├── streamlit_app.py               # Web testing interface
├── redis_config.md               # Redis setup guide
├── requirements.txt               # Python dependencies
├── .env                          # Environment variables (create this)
└── .gitignore                    # Git ignore rules
```

## 🛠️ Core Components

### Redis State Manager (`redis_manager.py`)
- **Redis Cloud Support**: Production-ready with redis:// URL support
- **Memory Fallback**: Graceful degradation when Redis unavailable
- **Session TTL**: Automatic cleanup of expired conversations
- **Statistics**: Real-time monitoring of connections and usage
- **Error Handling**: Robust error recovery and logging

### LangChain Agent (`langchain_agent.py`)
- **Client Context**: Dynamic prompt enrichment with contact information
- **Memory Management**: ConversationSummaryBufferMemory for context
- **Language Detection**: Automatic French/Spanish detection and adaptation
- **State Serialization**: Full agent state persistence for stateless deployment
- **Tool Integration**: Dynamic tool loading and management

### WhatsApp Handler (`whatsapp_handler.py`)
- **Stateless Design**: Load/save user state per message via Redis
- **Contact Enrichment**: Automatic client context from database
- **User Management**: Individual conversation state tracking
- **Reset Functionality**: Conversation restart capabilities
- **Error Handling**: Graceful fallbacks and user-friendly error messages

### Contact Manager (`contacts_manager.py`)
- **Excel Integration**: Load client database from spreadsheet
- **Phone Lookup**: Fast contact search by phone number
- **Data Validation**: Phone number normalization and validation
- **Statistics**: Contact database monitoring and stats
- **Flexible Mapping**: Configurable column mapping for different Excel formats

### Tools System (`tools/tools.py`)
- **RAG Search Tool**: Query CCI knowledge base with multilingual support
- **Question Tracking**: Collect and validate questionnaire responses
- **Progress Monitoring**: Track diagnostic completion status
- **Bilingual Support**: Language-aware tool responses

### RAG Implementation (`tools/rag.py`)
- **Vector Search**: Pinecone integration with embedding generation
- **Response Reformulation**: OpenAI-powered answer improvement
- **Multilingual**: Language-specific system prompts
- **Error Handling**: Graceful fallbacks for missing information

## 🌍 Multilingual Support

The agent automatically detects user language and adapts:

- **French Detection**: Loads `prompt_fr.txt`
- **Spanish Detection**: Loads `prompt_es.txt`  
- **Tool Synchronization**: All tools adapt to detected language
- **Response Formatting**: Language-appropriate error messages and responses
- **Dynamic Prompts**: Client context adapted per language

## 📊 Agent Workflow

```mermaid
graph TD
    A[User Message] --> B{First Interaction?}
    B -->|Yes| C[Detect Language]
    B -->|No| D[Load User State from Redis]
    C --> E[Adapt Agent & Tools]
    E --> F[Load Contact Info]
    D --> F
    F --> G[Enrich Prompt with Context]
    G --> H{Tool Call Needed?}
    H -->|RAG Query| I[Search Knowledge Base]
    H -->|Question Tracking| J[Count Question]
    H -->|No Tool| K[Direct Response]
    I --> L[Return Enhanced Answer]
    J --> M[Ask Next Question]
    K --> L
    L --> N[Save State to Redis]
    M --> N
    N --> O[Agent Response]
```

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `OPENAI_API_KEY` | OpenAI API key | ✅ | - |
| `PINECONE_API_KEY` | Pinecone API key | ✅ | - |
| `PINECONE_INDEX` | Pinecone index name | ✅ | - |
| `REDIS_URL` | Redis connection URL | ❌ | - |
| `REDIS_HOST` | Redis host | ❌ | localhost |
| `REDIS_PORT` | Redis port | ❌ | 6379 |
| `REDIS_PASSWORD` | Redis password | ❌ | - |
| `REDIS_DB` | Redis database number | ❌ | 0 |
| `REDIS_SESSION_TTL` | Session expiry (seconds) | ❌ | 86400 |
| `REDIS_KEY_PREFIX` | Redis key prefix | ❌ | cci_agent: |
| `CONTACTS_EXCEL_PATH` | Path to contacts Excel file | ❌ | - |

### Agent Configuration

```python
# Customize agent behavior
agent = CCILangChainAgent(
    prompt_name="prompt_fr"  # Custom prompt file (fr or es)
)

# Force specific language (useful for testing)
from app.agents.language.language_manager import set_agent_language
set_agent_language(agent, "es")  # Force Spanish

# Get agent status
status = agent.get_status()
print(f"Question: {status['current_question']}/7")
print(f"Language: {status['detected_language']}")
```

## 🚀 Production Deployment

### Redis Configuration

**Option 1: Redis Cloud (Recommended)**
```bash
REDIS_URL=redis://default:password@host:port/db
```

**Option 2: Local Redis**
```bash
# Install Redis
brew install redis  # macOS
sudo apt install redis-server  # Ubuntu

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis-server  # Ubuntu
```

**Option 3: Docker**
```bash
docker run -d -p 6379:6379 redis:alpine
```

### WhatsApp Integration

```python
# Webhook endpoint example
from fastapi import FastAPI
from app.agents.whatsapp_handler import whatsapp_chat

app = FastAPI()

@app.post("/whatsapp/webhook")
async def whatsapp_webhook(webhook_data: dict):
    # Extract user data
    user_id = webhook_data.get("user_id")
    message = webhook_data.get("message")
    
    if not user_id or not message:
        return {"error": "Invalid webhook data"}
    
    # Process message with automatic state management
    response = await whatsapp_chat(user_id=user_id, user_input=message)
    
    # Send response back to WhatsApp
    return {"response": response}
```

### Performance Optimization

The agent is optimized for **sub-8 second response times** required by Manychat:

- **Contact Lookup**: ~50ms average
- **LLM Processing**: ~3-5s average  
- **Total Response**: ~6s average
- **Redis Operations**: ~10ms average

Run performance tests:
```bash
python performance_test.py
```

## 📈 Monitoring & Analytics

### Redis Statistics

```python
from app.agents.whatsapp_handler import get_redis_stats

stats = await get_redis_stats()
print(f"Active users: {stats['active_users']}")
print(f"Memory used: {stats['used_memory_human']}")
print(f"Redis status: {stats['status']}")
```

### Contact Database Stats

```python
from whatsapp_contact.contacts_manager import get_contacts_manager

manager = get_contacts_manager()
stats = manager.get_stats()
print(f"Total contacts: {stats['total_contacts']}")
print(f"Valid phones: {stats['valid_phones']}")
```

## 🔍 Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   ```bash
   # Check Redis status
   python test/test_redis.py
   
   # Verify environment variables
   echo $REDIS_URL
   ```

2. **Contact Database Not Loading**
   ```bash
   # Check file path and format
   python -c "from whatsapp_contact.contacts_manager import get_contacts_manager; m = get_contacts_manager('your_file.xlsx'); print(m.get_stats())"
   ```

3. **Slow Performance**
   ```bash
   # Run performance benchmark
   python performance_test.py
   
   # Check Redis latency
   redis-cli --latency -h your-redis-host
   ```

### Debug Mode

Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# All Redis operations and agent decisions will be logged
```

## 📚 API Reference

### Core Functions

```python
# WhatsApp Integration
await whatsapp_chat(user_id: str, user_input: str) -> str
await get_user_status(user_id: str) -> Dict[str, Any]
await reset_user_conversation(user_id: str) -> None

# Contact Management  
contacts_manager.load_contacts(excel_path: str) -> bool
contacts_manager.find_contact_by_phone(phone: str) -> Optional[Dict]

# Redis Management
await redis_manager.save_user_state(user_id: str, state: Dict) -> bool
await redis_manager.load_user_state(user_id: str) -> Optional[Dict]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite: `python test/test_*.py`
5. Submit a pull request

## 📄 License

This project is proprietary to CCI France-Colombia.

---

**Ready for production deployment with Redis Cloud and WhatsApp Business API! 🚀**