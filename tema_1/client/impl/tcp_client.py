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
        self.protocol = "tcp"

    @handle_exceptions
    def _connect_wrapper(self):
        self.socket.connect((self.host, self.port))

    def _send_finished_transmission(self):
        while True:
            finished_transmission_encoded = FINISHED_TRANSMISSION_MSG.encode()
            self.socket.send(finished_transmission_encoded)

            self.bytes_no += len(finished_transmission_encoded)
            self.msgs_no += 1

            if self.stop_and_wait:
                ack = self.socket.recv(4)
                ack = int.from_bytes(ack, byteorder="little", signed=False)

                if self.stop_and_wait:
                    if ack == AckType.ERROR:
                        continue
            break

        return False

    def _send_file(self, fd, packages_no, **kwargs):
        headers = f'{kwargs["filename"]}\n{kwargs["file_size"]}\n{packages_no}'
        headers = headers.ljust(HEADERS_SIZE)
        headers = headers.encode()
        # self.logger.info(f"Headers size: {len(headers)}")
        while True:
            self.socket.send(headers)
            self.bytes_no += len(headers)
            self.msgs_no += 1
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
                # self.logger.info(f"Data len: {len(data)}")
                self.socket.send(data)

                self.bytes_no += len(data)
                self.msgs_no += 1

                if self.stop_and_wait:
                    ack = self.socket.recv(4)
                    ack = int.from_bytes(ack, byteorder="little", signed=False)

                    if self.stop_and_wait:
                        if ack == AckType.ERROR:
                            continue
                break

        # self.logger.info(f"Sent file: {kwargs['filename']}")
        return True
