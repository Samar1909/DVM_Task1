from django.apps import AppConfig



class HomeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'home'

    def ready(self):
        # from home.updaters import start
        import home.signals
        # start()
