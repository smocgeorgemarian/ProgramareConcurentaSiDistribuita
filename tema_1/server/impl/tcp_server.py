import logging
from socket import SOCK_STREAM

from server.abstract_server import Server
from utils.general import HEADERS_SIZE, FINISHED_TRANSMISSION_MSG
from utils.stats_helpers import stats_gatherer


class TcpServer(Server):
    def __init__(self, host, port, package_size, store=True):
        super().__init__(host, port, package_size, SOCK_STREAM, store=store)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(TcpServer.__name__)

    @stats_gatherer
    def _receive_file(self, connection):
        headers = connection.recv(HEADERS_SIZE)
        headers_decoded = headers.decode()

        if headers_decoded == FINISHED_TRANSMISSION_MSG:
            return len(headers_decoded), 1, False

        bytes_no = 0
        msgs_no = 0

        self.logger.info(f"Headers received:\n{headers_decoded}")
        filename, file_size, packages_no = headers_decoded.split("\n")
        file_size, packages_no = int(file_size), int(packages_no.rstrip())

        bytes_no += len(headers_decoded)
        msgs_no += 1

        packages = []
        for package_index in range(packages_no):
            if package_index != packages_no - 1:
                data = connection.recv(self.package_size)
            else:
                data = connection.recv(file_size - (packages_no - 1) * self.package_size)

            bytes_no += len(data)
            msgs_no += 1
            # self.logger.info(f"Data size received: {len(data)}")
        return bytes_no, msgs_no, True
