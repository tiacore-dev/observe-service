import os
from app import create_app

config_name = os.environ.get('CONFIG_NAME', 'Development')
app = create_app(config_name, enable_scheduler=True)
