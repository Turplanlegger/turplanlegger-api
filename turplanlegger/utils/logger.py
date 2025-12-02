import logging
from sys import stdout

from turplanlegger.utils.config import config

log_level = config.log_level
log_format = '%(asctime)s - %(name)s: %(levelname)s - %(message)s'
if config.debug is True or config.log_level == 'DEBUG':
    log_level = 'DEBUG'
    log_format = '%(asctime)s - %(name)s[%(process)d]: %(levelname)s - %(message)s [in %(pathname)s:%(lineno)d]'

handlers = [logging.StreamHandler(stdout)]
if config.log_to_file is True:
    handlers.append(logging.FileHandler(config.log_file_path))

logging.basicConfig(level=log_level, format=log_format, handlers=handlers)

log = logging.getLogger('turplanlegger')
log_db = logging.getLogger('turplanlegger.database')
log_auth = logging.getLogger('turplanlegger.auth')
