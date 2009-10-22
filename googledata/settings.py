from django.conf import settings

LOGIN = getattr(settings, 'GDATA_LOGIN', '')
PASSWORD = getattr(settings, 'GDATA_PASSWORD', '')
CACHE_LENGTH = getattr(settings, 'GDATA_CACHE_LENGTH', 3600 )
CALL_LENGTH = 10
