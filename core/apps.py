from django.apps import AppConfig

class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Auto-start scheduler when app starts"""
        import threading
        from django.core.management import call_command
        
        # Start scheduler in a background thread
        def start_scheduler():
            try:
                call_command('start_scheduler')
            except Exception as e:
                print(f"Error starting scheduler: {e}")
        
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
