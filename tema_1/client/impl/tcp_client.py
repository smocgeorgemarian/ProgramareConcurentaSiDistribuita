import logging
from socket import SOCK_STREAM

from client.abstract_client import Client
from utils.exc_helpers import handle_exceptions
from utils.general import FINISHED_TRANSMISSION_MSG, HEADERS_SIZE
from utils.stats_helpers import stats_gatherer
from utils.udp_helpers import AckType


class TcpClient(Client):
    def __init__(self, host, port, package_size, stop_and_wait):
        super().__init__(host, port, package_size, SOCK_STREAM, stop_and_wait)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(TcpClient.__name__)

    @handle_exceptions
    def _connect_wrapper(self):
        self.socket.connect((self.host, self.port))

    @stats_gatherer
    def _send_finished_transmission(self):
        bytes_no = 0
        msgs_no = 0

        while True:
            finished_transmission_encoded = FINISHED_TRANSMISSION_MSG.encode()
            self.socket.send(finished_transmission_encoded)

            bytes_no += len(finished_transmission_encoded)
            msgs_no += 1

            if self.stop_and_wait:
                ack = self.socket.recv(4)
                ack = int.from_bytes(ack, byteorder="little", signed=False)

                if self.stop_and_wait:
                    if ack == AckType.ERROR:
                        continue
            break

        return bytes_no, msgs_no, False

    @stats_gatherer
    def _send_file(self, fd, packages_no, **kwargs):
        bytes_no = 0
        msgs_no = 0

        headers = f'{kwargs["filename"]}\n{kwargs["file_size"]}\n{packages_no}'
        headers = headers.ljust(HEADERS_SIZE)
        headers = headers.encode()
        while True:
            self.socket.send(headers)
            bytes_no += len(headers)
            msgs_no += 1
            if self.stop_and_wait:
                ack = self.socket.recv(4)
                ack = int.from_bytes(ack, byteorder="little", signed=False)

                if self.stop_and_wait:
                    if ack == AckType.ERROR:
                        continue
            break

        for package_index in range(packages_no):
            data = fd.read(self.package_size)
            while True:
                self.socket.send(data)

                bytes_no += len(data)
                msgs_no += 1

                if self.stop_and_wait:
                    ack = self.socket.recv(4)
                    ack = int.from_bytes(ack, byteorder="little", signed=False)

                    if self.stop_and_wait:
                        if ack == AckType.ERROR:
                            continue
                break

        self.logger.info(f"Sent file: {kwargs['filename']}")
        return bytes_no, msgs_no, True
