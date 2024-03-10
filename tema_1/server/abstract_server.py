from socket import socket, AF_INET

from utils.exc_helpers import handle_exceptions
from utils.general import DOWNLOADS_DIR
from utils.stats_helpers import stats_after_run


class Server:
    def __init__(self, host, port, package_size, mode, stop_and_wait, store=True, samples_dir=DOWNLOADS_DIR):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, mode)

        self.package_size = package_size
        self.store = store
        self.samples_dir = samples_dir
        self.stop_and_wait = stop_and_wait

    @handle_exceptions
    def _bind_wrapper(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def _receive_file(self, connection):
        raise NotImplementedError("Subclass must implement abstract method")

    @stats_after_run
    def receive(self):
        raise NotImplementedError("Subclass must implement abstract method")


