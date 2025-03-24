import requests

def send_slack_notification(event_type, message, username=None, icon_emoji=None):
    """
    Envía una notificación a un webhook de Slack según el tipo de evento.
    
    Args:
        event_type (str): Tipo de evento para seleccionar el webhook ('error', 'warning', 'info', 'success')
        message (str): El mensaje a enviar
        username (str, optional): Sobreescribe el nombre de usuario. Por defecto es None.
        icon_emoji (str, optional): Emoji para usar como icono. Por defecto es None.
    
    Returns:
        requests.Response: La respuesta de la API de Slack
    """
    # Diccionario de webhooks por tipo de evento
    webhook_urls = {
        'auditoria': 'https://hooks.slack.com/services/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'
    }
    
    # Verificar si el tipo de evento es válido
    if event_type not in webhook_urls:
        print(f"Tipo de evento '{event_type}' no reconocido. Eventos disponibles: {', '.join(webhook_urls.keys())}")
        return None
    
    # Seleccionar la URL del webhook
    webhook_url = webhook_urls[event_type]
    
    # Configurar el payload
    payload = {
        "text": message
    }
    
    # Añadir parámetros opcionales
    if username:
        payload["username"] = username
    if icon_emoji:
        payload["icon_emoji"] = icon_emoji
    
    # Emojis predeterminados por tipo de evento si no se especifica uno
    default_emojis = {
        'auditoria': ':red_circle:'
    }
    
    if not icon_emoji and event_type in default_emojis:
        payload["icon_emoji"] = default_emojis[event_type]
    
    # Enviar la notificación
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
        print(f"Mensaje '{event_type}' enviado correctamente a Slack")
        return response
    except Exception as e:
        print(f"Error al enviar notificación a Slack: {e}")
        return None