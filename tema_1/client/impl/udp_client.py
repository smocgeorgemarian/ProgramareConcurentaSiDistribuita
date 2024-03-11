import logging
from socket import SOCK_DGRAM

from client.abstract_client import Client
from utils.exc_helpers import Result
from utils.general import FINISHED_TRANSMISSION_MSG
from utils.stats_helpers import stats_gatherer
from utils.udp_helpers import DatagramType, checksum, AckType


class UdpClient(Client):
    def __init__(self, host, port, package_size, stop_and_wait):
        super().__init__(host, port, package_size, SOCK_DGRAM, stop_and_wait)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(UdpClient.__name__)
        self.protocol = "udp"

    def _connect_wrapper(self):
        return Result(data=None, is_success=True)

    def _send_finished_transmission(self):
        merged_data = f'{DatagramType.END_MESSAGE.value}\n{FINISHED_TRANSMISSION_MSG}'
        merged_data_encoded = merged_data.encode()

        crc = checksum(merged_data_encoded) % (2 ** 32)
        merged_data_encoded += crc.to_bytes(length=4, byteorder="little", signed=False)
        self.logger.info(f"Size finished: {len(merged_data_encoded)}")
        while True:
            self.socket.sendto(merged_data_encoded, (self.host, self.port))

            self.bytes_no += len(merged_data_encoded)
            self.msgs_no += 1
            if self.stop_and_wait:
                ack = int.from_bytes(self.socket.recv(4), byteorder="little", signed=False)
                if ack == AckType.ERROR:
                    continue
            break

        return False

    def _build_package(self, data, file_index, package_index, file_size):
        packages_no = int((file_size + self.package_size - 1) // self.package_size)
        headers = f'{DatagramType.CHUNK.value}\n{file_index}\n{file_size}\n{packages_no}\n{package_index}'
        merged_data = f'{headers}\n'.encode() + data

        crc = checksum(merged_data) % (2 ** 32)
        merged_data = merged_data + crc.to_bytes(length=4, byteorder="little", signed=False)
        return merged_data

    def _send_file(self, fd, packages_no, **kwargs):
        headers = f'{DatagramType.INITIAL_HEADER.value}\n{kwargs["filename"]}\n{kwargs["file_index"]}\n{kwargs["file_size"]}'.encode()
        crc = checksum(headers)
        headers += crc.to_bytes(length=4, byteorder="little", signed=False)
        while True:
            self.socket.sendto(headers, (self.host, self.port))
            self.bytes_no += len(headers)
            self.msgs_no += 1

            if self.stop_and_wait:
                ack = int.from_bytes(self.socket.recv(4), byteorder="little", signed=False)
                if ack == AckType.ERROR:
                    continue
            break

        for package_index in range(packages_no):
            data = fd.read(self.package_size)
            package = self._build_package(data, kwargs["file_index"], package_index, kwargs["file_size"])
            while True:
                self.socket.sendto(package, (self.host, self.port))
                self.bytes_no += len(package)
                self.msgs_no += 1

                if self.stop_and_wait:
                    ack = int.from_bytes(self.socket.recv(4), byteorder="little", signed=False)
                    if ack == AckType.ERROR:
                        continue
                break

        return True
