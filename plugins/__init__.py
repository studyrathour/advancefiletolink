from .stream import setup_stream_handlers
from .admin import setup_admin_handlers
from .common import setup_common_handlers
from .callbacks import setup_callback_handlers

def setup_all_handlers(app):
    setup_stream_handlers(app)
    setup_admin_handlers(app)
    setup_common_handlers(app)
    setup_callback_handlers(app)