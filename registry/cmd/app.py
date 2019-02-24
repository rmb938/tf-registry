import logging

from clify.app import Application


class TFRegistryApplication(Application):
    def __init__(self):
        super().__init__('registry', 'CLI for TF Registry')

    @property
    def version(self):
        return "0.0.1"  # TODO: figure out how to do this

    def logging_config(self, log_level: int) -> dict:
        return {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
                    'datefmt': '%Y-%m-%dT%H:%M:%S%z'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'formatter': 'default'
                }
            },
            'loggers': {
                '': {
                    'level': logging.getLevelName(log_level),
                    'handlers': ['console']
                },
                'registry': {
                    'level': logging.getLevelName(log_level),
                    'handlers': ['console'],
                    'propagate': False
                },
                'sqlalchemy': {
                    'level': logging.WARN,
                    'handlers': ['console'],
                    'propagate': False
                },
                'alembic': {
                    'level': logging.INFO,
                    'handlers': ['console'],
                    'propagate': False
                }
            }
        }
