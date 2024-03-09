from socket import socket, AF_INET

from utils.exc_helpers import handle_exceptions
from utils.general import DOWNLOADS_DIR
from utils.stats_helpers import stats_after_run


class Server:
    def __init__(self, host, port, package_size, mode, store=True, samples_dir=DOWNLOADS_DIR):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, mode)

        self.package_size = package_size
        self.store = store
        self.samples_dir = samples_dir

    @handle_exceptions
    def _bind_wrapper(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen()

    def _receive_file(self, connection):
        raise NotImplementedError("Subclass must implement abstract method")

    @stats_after_run
    def receive(self):
        result = self._bind_wrapper()
        if result.is_fail:
            return result

        self.logger.info(f"Listening at: {self.host}, port: {self.port}")
        connection, client_address = self.socket.accept()

        with connection:
            while True:
                bytes_no, msgs_no, should_continue = self._receive_file(connection)
                if not should_continue:
                    break

