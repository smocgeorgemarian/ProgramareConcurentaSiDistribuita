import logging
import os.path

from _socket import SOCK_DGRAM

from server.abstract_server import Server
from utils.exc_helpers import handle_exceptions
from utils.general import DOWNLOADS_DIR
from utils.stats_helpers import stats_gatherer, stats_after_run
from utils.udp_helpers import UdpResponse, DatagramType


class UdpServer(Server):
    def __init__(self, host, port, package_size, store=True):
        super().__init__(host, port, package_size, SOCK_DGRAM, store=store)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(UdpServer.__name__)
        self.udp_packet_size = package_size + 12 * 4
        self.file_index_to_chunks = {}
        self.file_index_to_filename = {}

    @stats_gatherer
    def _receive_file(self, connection):
        pass

    @handle_exceptions
    def _bind_wrapper(self):
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(10)

    @handle_exceptions
    @stats_gatherer
    def _receive_data(self):
        bytes_no = 0
        msgs_no = 0
        should_continue = True

        data, _ = self.socket.recvfrom(self.udp_packet_size)
        bytes_no += len(data)
        msgs_no += 1

        response = UdpResponse(data)
        if response.type == DatagramType.INITIAL_HEADER:
            self.file_index_to_filename[response.file_index] = response.filename

        elif response.type == DatagramType.CHUNK:
            if response.file_index not in self.file_index_to_chunks:
                self.file_index_to_chunks[response.file_index] = []
            self.file_index_to_chunks[response.file_index].append((response.package_index, response.data))

        elif response.type == DatagramType.END_MESSAGE:
            should_continue = False
        else:
            print("Sarutul tau e afrodisiac")

        return bytes_no, msgs_no, should_continue

    def split_data_per_file(self):
        self.logger.info(f"Received name for: {len(self.file_index_to_filename)} files")
        self.logger.info(f"Received data for: {len(self.file_index_to_chunks)} files")

        tmp_files_to_chunks = {}
        for file_index, chunks in self.file_index_to_chunks.items():
            chunks = sorted(chunks, key=lambda x: x[0])
            tmp_files_to_chunks[file_index] = chunks
        for file_index in tmp_files_to_chunks:
            if file_index not in self.file_index_to_filename:
                default_name = f"default_name_{file_index}"
                self.logger.info(f"Using custom name: {default_name}")
                filename = default_name
            else:
                filename = self.file_index_to_filename[file_index]
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            with open(os.path.join(DOWNLOADS_DIR, filename), "wb+") as fd:
                for chunk in tmp_files_to_chunks[file_index]:
                    fd.write(chunk[1].encode())

    @stats_after_run
    def receive(self):
        result = self._bind_wrapper()
        if result.is_fail:
            return result

        self.logger.info(f"Listening at: {self.host}, port: {self.port}")

        while True:
            # no ack case
            result = self._receive_data()
            if result.is_fail:
                break

        self.split_data_per_file()
