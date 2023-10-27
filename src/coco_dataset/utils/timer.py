from datetime import datetime, timedelta
import time

from loguru import logger

TODAY = datetime.today().strftime("%Y-%m-%d")


class Timer(object):
    """Context manager to measure the time of execution.
    Use like:
    >>> with Timer():
    ...     pass
    <prints time for execution>
    """

    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, type, value, traceback):
        self.end = time.perf_counter()
        self.duration = timedelta(seconds=self.end - self.start)
        logger.debug(f"{self.duration=}")
