import os
from socket import socket, AF_INET

from utils.exc_helpers import handle_exceptions_with_retries
from utils.general import DOWNLOADS_DIR


class Server:
    def __init__(self, host, port, package_size, mode, samples_dir=DOWNLOADS_DIR):
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

    def _send_file(self, filename, file_fullpath):
        raise NotImplementedError("Subclass must implement abstract method")

    def send(self):
        raise NotImplementedError("Subclass must implement abstract method")