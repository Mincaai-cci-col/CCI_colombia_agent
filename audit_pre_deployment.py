#!/usr/bin/env python3
"""
Audit pré-déploiement pour vérifier la cohérence des fichiers critiques
"""

import os
import sys
import ast
import importlib.util

def check_imports(file_path):
    """Vérifier les imports d'un fichier Python"""
    print(f"\n📋 Vérification imports: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse AST pour extraire les imports
        tree = ast.parse(content)
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    imports.append(f"{module}.{alias.name}")
        
        print(f"   ✅ {len(imports)} imports trouvés")
        return True
        
    except SyntaxError as e:
        print(f"   ❌ Erreur syntaxe: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False

def check_environment_variables():
    """Vérifier les variables d'environnement critiques"""
    print(f"\n🔐 Vérification variables d'environnement:")
    
    critical_vars = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY", 
        "PINECONE_INDEX",
        "REDIS_URL"
    ]
    
    missing = []
    for var in critical_vars:
        if os.getenv(var):
            print(f"   ✅ {var}: Définie")
        else:
            print(f"   ❌ {var}: MANQUANTE")
            missing.append(var)
    
    return len(missing) == 0, missing

def check_file_consistency():
    """Vérifier la cohérence entre les fichiers"""
    print(f"\n🔍 Vérification cohérence inter-fichiers:")
    
    issues = []
    
    # Vérifier que les prompts existent
    prompt_files = [
        "app/agents/prompts/prompt_fr.txt",
        "app/agents/prompts/prompt_es.txt",
        "app/agents/prompts/prompt_assistance_fr.txt", 
        "app/agents/prompts/prompt_assistance_es.txt"
    ]
    
    for prompt_file in prompt_files:
        if os.path.exists(prompt_file):
            print(f"   ✅ {prompt_file}: Existe")
        else:
            print(f"   ❌ {prompt_file}: MANQUANT")
            issues.append(f"Prompt manquant: {prompt_file}")
    
    # Vérifier les tools
    tools_file = "app/agents/tools/tools.py"
    if os.path.exists(tools_file):
        print(f"   ✅ {tools_file}: Existe")
    else:
        print(f"   ❌ {tools_file}: MANQUANT")
        issues.append(f"Tools manquant: {tools_file}")
    
    # Vérifier le RAG
    rag_file = "app/agents/tools/rag.py"
    if os.path.exists(rag_file):
        print(f"   ✅ {rag_file}: Existe")
    else:
        print(f"   ❌ {rag_file}: MANQUANT") 
        issues.append(f"RAG manquant: {rag_file}")
    
    return len(issues) == 0, issues

def check_function_signatures():
    """Vérifier les signatures de fonctions critiques"""
    print(f"\n🔧 Vérification signatures fonctions critiques:")
    
    issues = []
    
    # Vérifier whatsapp_chat function
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.agents.whatsapp_handler import whatsapp_chat
        
        # Vérifier que c'est bien une fonction async
        import inspect
        if inspect.iscoroutinefunction(whatsapp_chat):
            print(f"   ✅ whatsapp_chat: fonction async correcte")
        else:
            print(f"   ❌ whatsapp_chat: n'est pas async")
            issues.append("whatsapp_chat doit être async")
            
    except ImportError as e:
        print(f"   ❌ Import whatsapp_chat échoué: {e}")
        issues.append(f"Import error: {e}")
    
    return len(issues) == 0, issues

def check_memory_configuration():
    """Vérifier la configuration mémoire"""
    print(f"\n🧠 Vérification configuration mémoire:")
    
    issues = []
    
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from app.agents.langchain_agent import CCILangChainAgent
        
        # Créer une instance pour vérifier la config
        agent = CCILangChainAgent()
        
        # Vérifier BufferWindowMemory
        if hasattr(agent, 'memory') and hasattr(agent.memory, 'k'):
            k_value = agent.memory.k
            print(f"   ✅ BufferWindowMemory k={k_value}")
            
            if k_value <= 0 or k_value > 20:
                print(f"   ⚠️ k={k_value} pourrait être problématique (recommandé: 5-15)")
                issues.append(f"BufferWindowMemory k={k_value} non optimal")
        else:
            print(f"   ❌ BufferWindowMemory mal configurée")
            issues.append("BufferWindowMemory configuration invalide")
            
    except Exception as e:
        print(f"   ❌ Erreur test mémoire: {e}")
        issues.append(f"Memory test failed: {e}")
    
    return len(issues) == 0, issues

def main():
    print("🔍 AUDIT PRÉ-DÉPLOIEMENT AWS")
    print("=" * 50)
    
    all_good = True
    all_issues = []
    
    # 1. Check syntax des fichiers critiques
    critical_files = [
        "app/agents/langchain_agent.py",
        "app/agents/whatsapp_handler.py", 
        "app/agents/redis_manager.py",
        "app/agents/tools/tools.py",
        "app/agents/tools/rag.py"
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            if not check_imports(file_path):
                all_good = False
                all_issues.append(f"Problème syntaxe: {file_path}")
        else:
            print(f"   ❌ Fichier manquant: {file_path}")
            all_good = False
            all_issues.append(f"Fichier manquant: {file_path}")
    
    # 2. Check variables environnement
    env_ok, env_missing = check_environment_variables()
    if not env_ok:
        all_good = False
        all_issues.extend([f"Var env manquante: {var}" for var in env_missing])
    
    # 3. Check cohérence fichiers
    consistency_ok, consistency_issues = check_file_consistency()
    if not consistency_ok:
        all_good = False
        all_issues.extend(consistency_issues)
    
    # 4. Check signatures fonctions
    functions_ok, function_issues = check_function_signatures()
    if not functions_ok:
        all_good = False
        all_issues.extend(function_issues)
    
    # 5. Check configuration mémoire
    memory_ok, memory_issues = check_memory_configuration()
    if not memory_ok:
        all_good = False
        all_issues.extend(memory_issues)
    
    # Résumé final
    print(f"\n" + "=" * 50)
    print(f"📋 RÉSUMÉ AUDIT")
    print(f"=" * 50)
    
    if all_good:
        print(f"🎉 SUCCÈS: Tous les tests passent !")
        print(f"✅ Le code est prêt pour le déploiement AWS")
        return True
    else:
        print(f"⚠️ PROBLÈMES DÉTECTÉS:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        print(f"\n❌ Corriger ces problèmes avant déploiement")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

