import json
import logging
import os.path
import time

from _socket import SOCK_DGRAM

from server.abstract_server import Server
from utils.exc_helpers import handle_exceptions
from utils.general import DOWNLOADS_DIR
from utils.udp_helpers import UdpResponse, DatagramType, AckType


class UdpServer(Server):
    def __init__(self, host, port, package_size, stop_and_wait, store=True):
        super().__init__(host, port, package_size, SOCK_DGRAM, stop_and_wait, store=store)

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(UdpServer.__name__)
        self.udp_packet_size = package_size + 8 * 4
        self.file_index_to_chunks = {}
        self.file_index_to_filename = {}
        self.file_index_to_no_chunks = {}
        self.file_index_to_actual_count = {}
        self.client_address = None
        self.store_time = 0

    @handle_exceptions
    def _bind_wrapper(self):
        self.socket.bind((self.host, self.port))
        self.socket.settimeout(10)

    @handle_exceptions
    def _receive_data(self):
        should_continue = True
        while True:
            data, self.client_address = self.socket.recvfrom(self.udp_packet_size)
            self.bytes_no += len(data)
            self.msgs_no += 1

            response = UdpResponse(data)
            if response.crc_problem:
                if self.stop_and_wait:
                    self.socket.sendto(AckType.ERROR.value.to_bytes(4, "little"), self.client_address)
                    continue
                break

            if response.type == DatagramType.INITIAL_HEADER:
                if self.store:
                    self.file_index_to_filename[response.file_index] = response.filename

            elif response.type == DatagramType.CHUNK:
                self.file_index_to_no_chunks[response.file_index] = response.packages_no
                self.file_index_to_actual_count[response.file_index] = self.file_index_to_actual_count.get(response.file_index, 0) + 1

                if self.store:
                    if response.file_index not in self.file_index_to_chunks:
                        self.file_index_to_chunks[response.file_index] = []
                    self.file_index_to_chunks[response.file_index].append((response.package_index, response.data))

            else:
                should_continue = False

            if self.stop_and_wait:
                self.socket.sendto(AckType.OK.value.to_bytes(4, "little"), self.client_address)
            break

        return should_continue

    def split_data_per_file(self):
        self.logger.info(f"Received name for: {len(self.file_index_to_filename)} files")
        self.logger.info(f"Received data for: {len(self.file_index_to_chunks)} files")
        start = time.time()
        tmp_files_to_chunks = {}
        for file_index, chunks in self.file_index_to_chunks.items():
            chunks = sorted(chunks, key=lambda x: x[0])
            tmp_files_to_chunks[file_index] = chunks

        for file_index in tmp_files_to_chunks:
            if file_index not in self.file_index_to_no_chunks:
                continue

            if file_index not in self.file_index_to_filename:
                default_name = f"default_name_{file_index}"
                filename = default_name
            else:
                filename = self.file_index_to_filename[file_index]
            os.makedirs(DOWNLOADS_DIR, exist_ok=True)
            with open(os.path.join(DOWNLOADS_DIR, filename), "wb+") as fd:
                for chunk in tmp_files_to_chunks[file_index]:
                    fd.write(chunk[1].encode())
        self.store_time = time.time() - start

    def compute_packages_percent(self):
        total = 0
        actual = 0
        for file_index, expected in self.file_index_to_no_chunks.items():
            total += expected
            if file_index not in self.file_index_to_actual_count:
                continue
            actual += self.file_index_to_actual_count[file_index]
        if total:
            self.percent = actual * 100 / total
        else:
            self.percent = 0

    # @stats_after_run
    def receive(self):
        result = self._bind_wrapper()
        if result.is_fail:
            return result

        self.logger.info(f"Listening at: {self.host}, port: {self.port}")

        start = None
        while True:
            # no ack case
            result = self._receive_data()
            if not start:
                start = time.time()
            if result.is_fail:
                break
            if result.data is not None:
                should_continue = result.data
                if not should_continue:
                    break
        if self.store:
            self.split_data_per_file()

        self.compute_packages_percent()

        decrease_value = 10 if self.decrease_by_timeout else 0
        json_data = {
            "delta_time": time.time() - start - decrease_value,
            "protocol": "udp",
            "bytes_no": self.bytes_no,
            "msgs_no": self.msgs_no,
            "receive_rate": self.percent,
            "store_time": self.store_time
        }
        json_data_str = json.dumps(json_data)
        self.logger.info(f"Data: {json_data_str}")
