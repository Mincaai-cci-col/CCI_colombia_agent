# ⚠️ ATTENTION : Problème de concurrence de langue pour l'API

## Problème identifié

La variable globale `_current_language` dans `tools.py` va causer des problèmes dans un environnement API avec requêtes simultanées :

### Scénario problématique :
```
User A (français) -> set_tools_language("fr") -> _current_language = "fr"
User B (espagnol) -> set_tools_language("es") -> _current_language = "es"  # ❌ Écrase le français !
User A continue    -> rag_search_tool()        -> utilise "es"              # ❌ Mauvaise langue !
```

## Solutions recommandées

### Solution immédiate (garde le code actuel)
- Le problème existe mais l'impact est limité car :
  - Chaque utilisateur a son agent persisté dans Redis
  - La langue est restaurée à chaque chargement d'agent
  - Les requêtes WhatsApp sont généralement séquentielles par utilisateur

### Solution future (refactoring recommandé)
1. Passer la langue comme paramètre aux tools au lieu d'utiliser le global
2. Ou utiliser thread-local storage
3. Ou intégrer la langue dans le contexte de l'agent

## Actions immédiates prises
- ✅ Optimisation des performances (cache timezone, prints commentés)
- ✅ Documentation du problème
- ✅ Avertissements ajoutés dans le code

## Priorité
- **Court terme** : Fonctionnel mais pas idéal
- **Moyen terme** : Refactoring recommandé avant mise en production intensive