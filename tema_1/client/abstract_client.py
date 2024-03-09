import os
from socket import socket, AF_INET

from utils.exc_helpers import handle_exceptions_with_retries
from utils.general import SAMPLES_DIR
from utils.stats_helpers import stats_after_run


class Client:
    def __init__(self, host, port, package_size, mode, samples_dir=SAMPLES_DIR):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, mode)

        self.package_size = package_size
        self.samples_dir = samples_dir

    @handle_exceptions_with_retries
    def _connect_wrapper(self):
        self.socket.connect((self.host, self.port))

    def _get_packages_no(self, file_fullpath):
        return int((os.stat(file_fullpath).st_size + self.package_size - 1) // self.package_size)

    def _get_samples(self):
        for filename in os.listdir(self.samples_dir):
            yield filename, os.path.join(self.samples_dir, filename)

    def _send_file(self, fd, headers, packages_no):
        raise NotImplementedError("Subclass must implement abstract method")

    def _send_finished_transmission(self):
        raise NotImplementedError("Subclass must implement abstract method")

    @stats_after_run
    def send(self):
        result = self._connect_wrapper()
        if result.is_fail:
            return result

        for filename, file_fullpath in self._get_samples():
            file_size = os.stat(file_fullpath).st_size
            packages_no = int((file_size + self.package_size - 1) // self.package_size)
            headers = f"{filename}\n{file_size}\n{packages_no}".encode()
            self.logger.info(f"Headers: {headers}")

            with open(file_fullpath, "rb") as fd:
                self._send_file(fd, headers, packages_no)

        # Ended work
        self._send_finished_transmission()
