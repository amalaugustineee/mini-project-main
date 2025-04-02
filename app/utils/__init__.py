import datetime
from . import seed_data

def register_filters(app):
    """
    Register custom Jinja2 filters
    """
    @app.template_filter('datetime')
    def format_datetime(timestamp):
        """
        Convert a UNIX timestamp to a formatted date string
        """
        dt = datetime.datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S') 