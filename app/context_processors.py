from flask import session

def register_context_processors(app):
    @app.context_processor
    def inject_notification_utils():
        def get_page_notifications(page):
            """Récupère les notifications spécifiques à une page et les supprime de la session"""
            return session.pop(f'notifications_{page}', [])
        
        return dict(
            get_page_notifications=get_page_notifications,
            add_page_notification=lambda page, category, message: session.setdefault(
                f'notifications_{page}', []
            ).append((category, message)))