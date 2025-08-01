# Configuration Redis pour CCI Agent

## Variables d'environnement requises

Ajoutez ces variables à votre fichier `.env` :

### Option 1: REDIS_URL (recommandé pour services hébergés)

```bash
# URL Redis complète (Redis Cloud, Heroku, AWS, etc.)
REDIS_URL=redis://username:password@host:port/db

# Configuration optionnelle
REDIS_SESSION_TTL=86400
REDIS_KEY_PREFIX=cci_agent:
```

### Option 2: Paramètres individuels (local)

```bash
# Redis Configuration pour la persistance des états
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_SESSION_TTL=86400
REDIS_KEY_PREFIX=cci_agent:
```

**Note**: Si `REDIS_URL` est définie, elle prend la priorité sur les paramètres individuels.

## Installation Redis

### Local (développement)
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server

# Windows
# Utilisez Docker ou WSL
```

### Production (options)

1. **Redis Cloud** (recommandé)
   - Création d'un compte sur Redis Cloud
   - Configuration automatique avec SSL

2. **Docker**
   ```bash
   docker run -d -p 6379:6379 redis:alpine
   ```

3. **AWS ElastiCache**
   - Service Redis managé par AWS

## Test de connexion

```python
# Vérifier la connexion Redis
from app.agents.redis_manager import get_redis_manager

manager = get_redis_manager()
stats = manager.get_stats()
print(stats)
```

## Fonctionnalités

- ✅ **Persistance** : État des conversations sauvegardé
- ✅ **TTL** : Sessions expirent automatiquement (24h par défaut)
- ✅ **Fallback** : Retombe sur mémoire si Redis indisponible
- ✅ **Monitoring** : Statistiques de connexion et usage
- ✅ **Compatible** : API identique à l'ancien système 