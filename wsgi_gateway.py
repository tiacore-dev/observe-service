# autopep8: off
from gevent import monkey # pylint: disable=import-error
monkey.patch_all(ssl=False)


from app import create_app
import os
# autopep8: on


config_name = os.environ.get('CONFIG_NAME', 'Development')
app = create_app(config_name, enable_gateway=True)
