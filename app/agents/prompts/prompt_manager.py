"""
Gestion du prompt dynamique pour l'agent CCI
"""

def get_client_info_variable(client_context, detected_language):
    """Retourne la variable Client_info à inclure dans le prompt"""
    return format_client_context(client_context, detected_language)

def format_client_context(client_context, detected_language):
    if not client_context:
        return ""
    if detected_language == "es":
        header = "=== INFORMACIÓN DEL CLIENTE ACTUAL ==="
        footer = "=== FIN INFORMACIÓN DEL CLIENTE ==="
        instructions = ("Tienes esta información sobre el cliente con quien estás hablando. "
                      "Úsala para personalizar tus respuestas de manera apropiada y profesional.")
    else:
        header = "=== INFORMATIONS DU CLIENT ACTUEL ==="
        footer = "=== FIN INFORMATIONS CLIENT ==="
        instructions = ("Tu as ces informations sur le client avec qui tu discutes. "
                      "Utilise-les pour personnaliser tes réponses de manière appropriée et professionnelle.")
    context_parts = []
    if 'empresa' in client_context:
        context_parts.append(f"Entreprise/Empresa: {client_context['empresa']}")
    if 'nombre' in client_context and 'apellido' in client_context:
        context_parts.append(f"Contact: {client_context['nombre']} {client_context['apellido']}")
    elif 'nombre' in client_context:
        context_parts.append(f"Contact: {client_context['nombre']}")
    if 'cargo' in client_context:
        context_parts.append(f"Poste/Cargo: {client_context['cargo']}")
    if 'sector' in client_context:
        context_parts.append(f"Secteur/Sector: {client_context['sector']}")
    if 'descripcion' in client_context:
        context_parts.append(f"Description/Descripción: {client_context['descripcion']}")
    if context_parts:
        context_text = "\n".join(context_parts)
        return f"{header}\n{context_text}\n{footer}\n\n{instructions}"
    return ""

def build_dynamic_prompt(base_system_prompt, client_context, detected_language, ChatPromptTemplate, MessagesPlaceholder):
    system_prompt = base_system_prompt
    if client_context:
        client_context_text = format_client_context(client_context, detected_language)
        system_prompt = f"{base_system_prompt}\n\n{client_context_text}"
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder("agent_scratchpad")
    ]) 