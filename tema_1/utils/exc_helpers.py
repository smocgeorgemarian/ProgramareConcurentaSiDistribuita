import functools
import inspect
import time
import traceback


class Result:
    def __init__(self, data=None, is_success=True, err_msg=None):
        self._is_success = is_success
        self._data = data
        self._err_msg = err_msg

    @property
    def is_fail(self):
        return False if self._is_success else True

    @property
    def is_success(self):
        return True if self._is_success else False

    @property
    def data(self):
        return self._data if self._is_success else None

    @property
    def err_msg(self):
        return self._err_msg if not self._is_success else None


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        try:
            self.decrease_by_timeout = True
            return Result(data=func(self, *args, **kwargs), is_success=True)
        except Exception:
            trace = traceback.format_exc()
            func_name = inspect.currentframe().f_back.f_code.co_name
            err_msg = f"Something wrong happened in function {func_name} after running {time.perf_counter() - start_time}:\n{trace}"
            self.logger.error(err_msg)
            return Result(is_success=False, err_msg=err_msg)

    return wrapper


def handle_exceptions_with_retries(func):
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.perf_counter()
        last_error = None
        for try_index in range(3):
            try:
                return Result(data=func(self, *args, **kwargs), is_success=True)
            except Exception:
                trace = traceback.format_exc()
                func_name = inspect.currentframe().f_back.f_code.co_name
                err_msg = f"Something wrong happened in function {func_name} after running {time.perf_counter() - start_time}:\n{trace}"
                last_error = err_msg

        self.logger.error(err_msg)
        return Result(is_success=False, err_msg=last_error)

    return wrapper
