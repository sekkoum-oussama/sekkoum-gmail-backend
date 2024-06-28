import os

if os.environ.get("ENVIRONMENT", "local") == "production":
    from .production_settings import *
else:
    from .local_settings import *