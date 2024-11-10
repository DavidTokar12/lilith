from __future__ import annotations

import logging
from tqdm import tqdm


class ConsoleError(Exception):
    pass


logger = logging.getLogger(__name__)

class TqdmToLogger(tqdm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = kwargs.pop("logger", logger)

    def display(self, msg=None, pos=None):
        """Overrides the default tqdm display function to log instead of print."""
        if msg:
            self.logger.info(msg)
