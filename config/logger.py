import logging.config
import logging

import config.settings as settings


def log(logger_name: str = None):
    if logger_name is None:
        logger_name = settings.get_settings().NAME

    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': '%(levelname)s | %(asctime)s | %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'handlers': {
            'default': {
                'level': 'DEBUG',
                'formatter': 'default',
                'class': 'logging.StreamHandler',
                'stream': 'ext://sys.stderr',
            },
        },
        'loggers': {
            settings.get_settings().NAME: {
                'handlers': ['default'],
                'level': 'DEBUG',
                'propagate': True,
            },
        }
    }

    logging.config.dictConfig(log_config)
    return logging.getLogger(logger_name)
