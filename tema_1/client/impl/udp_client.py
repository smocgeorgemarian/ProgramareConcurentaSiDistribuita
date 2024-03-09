import logging
from socket import SOCK_DGRAM

from client.abstract_client import Client
from utils.exc_helpers import Result
from utils.general import FINISHED_TRANSMISSION_MSG
from utils.stats_helpers import stats_gatherer
from utils.udp_helpers import DatagramType


class UdpClient(Client):
    def __init__(self, host, port, package_size):
        super().__init__(host, port, package_size, SOCK_DGRAM)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(UdpClient.__name__)



    def _connect_wrapper(self):
        return Result(data=None, is_success=True)

    @stats_gatherer
    def _send_finished_transmission(self):
        bytes_no = 0
        msgs_no = 0

        merged_data = f'{DatagramType.END_MESSAGE.value}\n{FINISHED_TRANSMISSION_MSG}'
        merged_data_encoded = merged_data.encode()
        self.socket.sendto(merged_data_encoded, (self.host, self.port))

        bytes_no += len(merged_data_encoded)
        msgs_no += 1
        return bytes_no, msgs_no, False

    def _build_package(self, data, file_index, package_index, file_size):
        packages_no = int((file_size + self.package_size - 1) // self.package_size)
        headers = f'{DatagramType.CHUNK.value}\n{file_index}\n{file_size}\n{packages_no}\n{package_index}'
        merged_data = f'{headers}\n{data}'.encode()
        return merged_data

    @stats_gatherer
    def _send_file(self, fd, packages_no, **kwargs):
        bytes_no = 0
        msgs_no = 0

        headers = f'{DatagramType.INITIAL_HEADER.value}\n{kwargs["filename"]}\n{kwargs["file_index"]}\n{kwargs["file_size"]}'.encode()
        self.socket.sendto(headers, (self.host, self.port))
        bytes_no += len(headers)
        msgs_no += 1

        for package_index in range(packages_no):
            data = fd.read(self.package_size)
            package = self._build_package(data, kwargs["file_index"], package_index, kwargs["file_size"])
            self.socket.sendto(package, (self.host, self.port))
            bytes_no += len(data)
            msgs_no += 1
        return bytes_no, msgs_no, True
