# autopep8: off
import eventlet
eventlet.monkey_patch()


from app import create_app
import os
# autopep8: on

config_name = os.environ.get('CONFIG_NAME', 'Development')
app = create_app(config_name, enable_scheduler=True)
