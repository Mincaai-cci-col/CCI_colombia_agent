# 🛠️ Backend Engineering Requirements - CCI Colombia Agent

## 📋 Project Context

**This project is very similar to CCI Mexico** - please reference that implementation for architectural patterns and deployment strategies.

## 1️⃣ Current State - What Has Been Done

### 🤖 **Core Agent System (COMPLETED)**
The conversational agent is **100% functional** with the following key components:

#### **Most Important Functions:**
```python
# Primary WhatsApp endpoint - stateless and Redis-backed
async def whatsapp_chat(user_id: str, user_input: str) -> str

# User state management with automatic persistence
async def get_user_status(user_id: str) -> Dict[str, Any]
async def reset_user_conversation(user_id: str) -> None

# Contact context enrichment from Excel database  
async def get_contact_info(user_id: str) -> Optional[Dict[str, Any]]
```

#### **Tech Stack (READY FOR PRODUCTION):**
- ✅ **LangChain Agent**: GPT-4o with RAG (Pinecone)
- ✅ **Redis Cloud**: State persistence configured and tested
- ✅ **Contact Database**: Excel-based client lookup (240 contacts loaded)
- ✅ **Bilingual Support**: French/Spanish auto-detection
- ✅ **Performance**: Sub-8s response times (Manychat compatible)

#### **Agent Capabilities:**
- Conducts 7-question structured questionnaire for member needs assessment
- Provides intelligent RAG-based answers about CCI services
- Automatically enriches responses with client context from contact database
- Maintains conversation state across multiple interactions
- Supports conversation reset and user management

#### **Testing Suite (VALIDATED):**
- ✅ Redis integration test: `python test/test_redis.py`
- ✅ Agent functionality test: `python test/test_langchain_agent.py` 
- ✅ WhatsApp handler test: `python test/test_whatsapp_chat.py`
- ✅ Performance benchmark: `python performance_test.py`
- ✅ Streamlit UI: `streamlit run streamlit_app.py`

---

## 2️⃣ Backend Implementation Requirements

### 🎯 **Your Mission: API Layer + Data Pipeline (Similar to CCI Mexico)**

You need to create the **production API wrapper** and **data extraction system** following the CCI Mexico pattern.

### **Phase 1: PostgreSQL Logging System** 📊

#### **Database Setup:**
- **Use Neo PostgreSQL** (access credentials available in Notion)
- Create conversation logging tables similar to CCI Mexico structure
- Log every user interaction, response, and agent state change

#### **Required Tables (minimum):**
```sql
-- User conversations log
CREATE TABLE conversations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    user_message TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    current_question INTEGER,
    detected_language VARCHAR(2),
    has_client_context BOOLEAN,
    client_company VARCHAR(255),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    response_time_ms INTEGER
);

-- User sessions tracking
CREATE TABLE user_sessions (
    user_id VARCHAR(50) PRIMARY KEY,
    first_interaction TIMESTAMP,
    last_interaction TIMESTAMP,
    total_questions_answered INTEGER,
    session_completed BOOLEAN,
    detected_language VARCHAR(2),
    client_context JSONB
);

-- API performance metrics
CREATE TABLE api_metrics (
    id SERIAL PRIMARY KEY,
    endpoint VARCHAR(100),
    response_time_ms INTEGER,
    status_code INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Phase 2: API Development** 🚀

#### **Create Production API Endpoints:**

**Main WhatsApp Endpoint:**
```python
POST /api/v1/whatsapp/message
{
    "user_id": "+573001234567",  # Real WhatsApp number
    "message": "Hola, soy una nueva empresa"
}

Response:
{
    "response": "¡Hola! Bienvenido a la CCI Francia-Colombia...",
    "user_status": {
        "current_question": 1,
        "language": "es",
        "has_context": true
    },
    "response_time_ms": 2340
}
```

**Additional Required Endpoints:**
```python
# User management
GET /api/v1/users/{user_id}/status
POST /api/v1/users/{user_id}/reset

# Health and monitoring  
GET /api/v1/health
GET /api/v1/metrics

# Admin endpoints
GET /api/v1/admin/stats
POST /api/v1/admin/contacts/reload
```

#### **Integration Points:**
- **Wrap existing functions**: The core agent functions are ready - you just need to create FastAPI/Flask wrappers
- **Add PostgreSQL logging**: Log every request/response to database
- **Preserve Redis state**: Don't modify the Redis state management - it works perfectly
- **Contact enrichment**: The contact database (240 entries) automatically enriches user context

### **Phase 3: Testing & Validation** 🧪

#### **Test with Real User Numbers:**
- Use actual WhatsApp numbers from the contact database
- Verify that client context enrichment works (company name, sector, role, etc.)
- Test conversation flow continuity across multiple API calls
- Validate performance metrics (< 8 seconds response time)

#### **Test Cases to Validate:**
```python
# Test 1: New user with context
POST /api/v1/whatsapp/message
{
    "user_id": "+573001234567",  # Real number from database
    "message": "Bonjour"
}
# Should return French response with client context

# Test 2: Conversation continuity  
POST /api/v1/whatsapp/message
{
    "user_id": "+573001234567",
    "message": "Oui, j'ai accédé à l'espace membre"
}
# Should continue questionnaire from question 2

# Test 3: Reset functionality
POST /api/v1/users/+573001234567/reset
# Should clear user state and restart conversation
```

### **Phase 4: Deployment** 🚀

#### **Deploy to AWS App Runner:**
- **App Runner is acceptable** for this deployment
- Configure environment variables (Redis URL, OpenAI API key, Pinecone, PostgreSQL)
- Set up health checks and monitoring
- Configure auto-scaling based on request volume

#### **Required Environment Variables:**
```bash
# Core AI Services
OPENAI_API_KEY=sk-...
PINECONE_API_KEY=...
PINECONE_INDEX=...

# Redis (already configured and tested)
REDIS_URL=redis://default:password@host:port/db

# PostgreSQL (from Notion - Neo PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/dbname

# Contact Database
CONTACTS_EXCEL_PATH=path/to/contacts.xlsx
```

### **Phase 5: Data Extraction API** 📊

#### **Create Data Export System (Like CCI Mexico):**

**Export Endpoint:**
```python
GET /api/v1/export/conversations
Query params:
- start_date: YYYY-MM-DD
- end_date: YYYY-MM-DD  
- format: excel|csv|json
- user_id: optional filter

Response:
- Excel file download (SharePoint compatible)
- OR Google Sheets API integration
- OR direct file upload to specified location
```

#### **Export Data Structure:**
```
Columns to export:
- User ID (WhatsApp number)
- Company Name  
- Contact Name
- Conversation Start Date
- Conversation End Date
- Total Questions Answered
- Completion Status
- Detected Language
- All Q&A pairs
- Performance Metrics
```

#### **Integration Options (Choose One):**
1. **SharePoint Upload**: Direct file upload to SharePoint folder
2. **Google Sheets**: Create/update Google Sheet via API
3. **Download Endpoint**: Generate Excel file for manual download

---

## 3️⃣ Implementation Priorities

### **Week 1: Database + Basic API**
- [ ] Set up PostgreSQL tables (Neo PostgreSQL from Notion)
- [ ] Create basic FastAPI wrapper around existing functions
- [ ] Implement conversation logging
- [ ] Deploy basic version to App Runner

### **Week 2: Testing + Optimization**  
- [ ] Test with real WhatsApp numbers from contact database
- [ ] Validate client context enrichment works correctly
- [ ] Performance testing and optimization
- [ ] API documentation and monitoring

### **Week 3: Data Export System**
- [ ] Implement conversation export API
- [ ] Create Excel/SharePoint integration (like CCI Mexico)
- [ ] Admin dashboard for data management
- [ ] Final testing and production deployment

---

## 🔧 Technical Notes

### **Important: DON'T MODIFY THE CORE AGENT**
The agent system is **production-ready**. Your job is to:
- ✅ **Wrap it with an API** (FastAPI recommended)
- ✅ **Add PostgreSQL logging** for analytics
- ✅ **Create data export features** for business users
- ❌ **Don't modify** the agent logic, Redis setup, or core functions

### **Reference Implementation**
- **Follow CCI Mexico patterns** for:
  - Database schema design
  - API endpoint structure  
  - Data export functionality
  - Deployment configuration

### **Key Integration Points**
```python
# Your API will primarily call these existing functions:
from app.agents.whatsapp_handler import whatsapp_chat, get_user_status, reset_user_conversation
from whatsapp_contact.contacts_manager import get_contacts_manager

# Example API endpoint implementation:
@app.post("/api/v1/whatsapp/message")
async def handle_whatsapp_message(request: WhatsAppRequest):
    start_time = time.time()
    
    # Call existing agent function (don't modify this)
    response = await whatsapp_chat(request.user_id, request.message)
    
    # Add your logging here
    log_conversation(request.user_id, request.message, response, time.time() - start_time)
    
    return {"response": response}
```

---

## 📞 Support & Questions

- **Code Repository**: Full agent implementation available for reference
- **Testing Scripts**: Use existing test files to understand functionality  
- **Performance Benchmarks**: `python performance_test.py` shows expected metrics
- **CCI Mexico Reference**: Use same patterns for database and export features

**The agent is ready - you just need to build the production wrapper around it! 🚀**