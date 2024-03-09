import functools
import time


def stats_gatherer(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        bytes_no, msgs_no, should_continue = func(self, *args, **kwargs)
        if not hasattr(self, "stats"):
            setattr(self, "stats", dict())
        self.stats["bytes_no"] = self.stats.get("bytes_no", 0) + bytes_no
        self.stats["msgs_no"] = self.stats.get("msgs_no", 0) + msgs_no
        self.stats["transmission_time"] = self.stats.get("msgs_no", float(0)) + time.perf_counter() - start_time
        self.logger.info(f"Current stats:\n{self.stats}")
        return bytes_no, msgs_no, should_continue

    return wrapper


def stats_after_run(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        if not hasattr(self, "stats"):
            setattr(self, "stats", dict())
        self.logger.info(f"Final stats:\n{self.stats}")

    return wrapper
