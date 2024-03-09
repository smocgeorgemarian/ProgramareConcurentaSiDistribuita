import logging
from socket import SOCK_STREAM

from server.abstract_server import Server
from utils.stats_helpers import stats_gatherer


class TcpServer(Server):
    def __init__(self, host, port, package_size, store=True):
        super().__init__(host, port, package_size, SOCK_STREAM, store=store)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(TcpServer.__name__)

    @stats_gatherer
    def _receive_file(self, connection, filename, file_size, packages_no):
        packages = []
        bytes_no = 0
        msgs_no = 0
        for package_index in range(packages_no):
            data = connection.recv(self.package_size)
            bytes_no += len(data)
            msgs_no += 1
            self.logger.info(f"Data size received: {len(data)}")
        return bytes_no, msgs_no
