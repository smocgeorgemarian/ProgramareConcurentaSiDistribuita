import logging
from socket import SOCK_STREAM

from client.abstract_client import Client
from utils.general import FINISHED_TRANSMISSION_MSG
from utils.stats_helpers import stats_gatherer


class TcpClient(Client):
    def __init__(self, host, port, package_size):
        super().__init__(host, port, package_size, SOCK_STREAM)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(TcpClient.__name__)

    @stats_gatherer
    def _send_finished_transmission(self):
        self.socket.send(FINISHED_TRANSMISSION_MSG)

    @stats_gatherer
    def _send_file(self, fd, headers, packages_no):
        bytes_no = 0
        msgs_no = 0

        self.socket.send(headers)
        bytes_no += len(headers)
        msgs_no = 1
        for package_index in range(packages_no):
            data = fd.read(self.package_size)
            self.socket.send(data)

            bytes_no += len(headers)
            msgs_no += 1
        return bytes_no, msgs_no
