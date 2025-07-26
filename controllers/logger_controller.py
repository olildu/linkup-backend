import logging
from colorlog import ColoredFormatter

# Define log format with colors
LOG_FORMAT = (
    "%(log_color)s[%(asctime)s] [%(levelname)s] "
    "%(filename)s:%(lineno)d in %(funcName)s() - %(message)s"
)

# Set color scheme for each log level
LOG_COLORS = {
    'DEBUG': 'cyan',
    'INFO': 'green',
    'WARNING': 'yellow',
    'ERROR': 'red',
    'CRITICAL': 'bold_red',
}

# Create handler with colored formatter
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter(LOG_FORMAT, log_colors=LOG_COLORS))

# Configure logger
logger_controller = logging.getLogger(__name__)
logger_controller.setLevel(logging.INFO)
logger_controller.addHandler(handler)
logger_controller.propagate = False
