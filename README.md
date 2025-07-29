# 🤖 Colia - Agent CCI Colombia

Agent conversationnel multilingue (français/espagnol) pour le diagnostic relationnel de la CCI France-Colombie.

## 🎯 Fonctionnalités

- **Diagnostic relationnel** : 8 questions séquentielles pour les membres CCI
- **RAG intelligent** : Répond aux questions via base de connaissances vectorisée (Pinecone)
- **Multilingue** : Détection automatique français/espagnol
- **Conversations asynchrones** : Reprise de conversation multi-jours
- **Gestion d'interruptions** : Questions utilisateur pendant le diagnostic

## 🏗️ Architecture

- **Orchestration** : LangGraph (workflow conversationnel)
- **LLM** : OpenAI GPT-4o (génération + détection d'intention)
- **RAG** : Pinecone + text-embedding-3-small
- **Base de données** : PostgreSQL (états + interactions + sessions)
- **API** : FastAPI
- **Interface** : Streamlit

## 🚀 Installation

1. **Cloner le projet**
```bash
git clone <repository>
cd CCI_colombia_agent
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Variables d'environnement**
```bash
export OPENAI_API_KEY="sk-..."
export PINECONE_API_KEY="..."
export PINECONE_INDEX="..."
export POSTGRES_URL="postgresql://user:password@localhost:5432/cci_colombia"
```

4. **Démarrer l'API**
```bash
uvicorn app.main:app --reload
```

5. **Démarrer l'interface Streamlit**
```bash
streamlit run streamlit_app.py
```

## 🖥️ Utilisation

### Interface Web (Streamlit)
1. Ouvrir http://localhost:8501
2. Saisir un ID utilisateur
3. Commencer la conversation
4. Colia pose automatiquement les 8 questions diagnostiques
5. Possibilité d'interrompre pour poser des questions sur la CCI

### API REST
```bash
curl -X POST "http://localhost:8000/colia" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test123", "message": "Bonjour"}'
```

### Scripts CLI
```bash
# Test interactif
python scripts/test_chat.py

# Simulation automatique
python scripts/simulate_user_flow.py
```

## 🔧 Tests

```bash
# Tests unitaires
pytest tests/

# Test du graphe
python -m pytest tests/test_graph.py

# Test RAG
python -m pytest tests/test_rag.py
```

## 📊 Workflow Conversationnel

```mermaid
graph TD
    A[ask_question] --> B[check_intent]
    B --> C{Intent?}
    C -->|question| D[answer_user_question - RAG]
    C -->|réponse| E[route_after_answer]
    D --> A
    E --> F{Question 8?}
    F -->|Non| A
    F -->|Oui| G[save_and_thank]
    G --> H[END]
```

## 🗂️ Structure du Projet

```
CCI_colombia_agent/
├── app/
│   ├── main.py              # API FastAPI
│   ├── graph.py             # Workflow LangGraph
│   ├── memory.py            # Gestion états utilisateur
│   ├── rag.py               # Système RAG Pinecone
│   ├── prompts.py           # Prompts système multilingues
│   ├── nodes/               # Nœuds du graphe
│   │   ├── question_nodes.py    # Questions diagnostiques
│   │   ├── intent_detection.py  # Classification LLM
│   │   ├── answer_user_node.py  # Réponses RAG
│   │   └── end_node.py          # Finalisation
│   └── utils/               # Utilitaires
│       ├── language.py          # Détection langue
│       ├── postgres.py          # Pool connexions
│       └── tools.py             # Fonctions helper
├── scripts/                 # Scripts de test
├── tests/                   # Tests unitaires
├── streamlit_app.py         # Interface web
└── requirements.txt         # Dépendances
```

## 🔐 Sécurité

- Validation entrées utilisateur
- Pool connexions PostgreSQL sécurisé
- Gestion d'erreur robuste
- Logs détaillés pour audit

## 📈 Performance

- **Pool PostgreSQL** : 2-10 connexions réutilisables
- **Embedding moderne** : text-embedding-3-small (80% moins cher)
- **Clients lazy** : Pinecone/OpenAI initialisés à la demande
- **Gestion mémoire** : États persistés entre sessions

## 🛠️ Production

L'agent est prêt pour la production avec :
- Gestion d'erreur complète
- Fallbacks gracieux
- Logging structuré
- Validation données
- Pool connexions optimisé 