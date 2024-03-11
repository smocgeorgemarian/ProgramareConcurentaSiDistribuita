import json
import os
import time
import zlib
from socket import socket, AF_INET

from utils.general import SAMPLES_DIR
from utils.stats_helpers import stats_after_run


class Client:
    def __init__(self, host, port, package_size, mode, stop_and_wait, samples_dir=SAMPLES_DIR):
        self.host = host
        self.port = port
        self.socket = socket(AF_INET, mode)

        self.package_size = package_size
        self.samples_dir = samples_dir
        self.stop_and_wait = stop_and_wait
        self.bytes_no = 0
        self.msgs_no = 0

    def _connect_wrapper(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def _get_packages_no(self, file_fullpath):
        return int((os.stat(file_fullpath).st_size + self.package_size - 1) // self.package_size)

    def _get_samples(self):
        for index, filename in enumerate(os.listdir(self.samples_dir)):
            yield filename, os.path.join(self.samples_dir, filename)

    def _send_file(self, fd, headers, packages_no, **kwargs):
        raise NotImplementedError("Subclass must implement abstract method")

    def _send_finished_transmission(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def send(self):
        result = self._connect_wrapper()
        if result.is_fail:
            return result

        start = time.time()
        for file_index, (filename, file_fullpath) in enumerate(self._get_samples()):
            file_size = os.path.getsize(file_fullpath)
            packages_no = int((file_size + self.package_size - 1) // self.package_size)

            with open(file_fullpath, "rb") as fd:
                self._send_file(fd, packages_no, **{"filename": filename, "file_index": file_index, "file_size": file_size})

        # Ended work
        self._send_finished_transmission()

        json_data = {
            "delta_time": time.time() - start,
            "protocol": self.protocol,
            "bytes": self.bytes_no,
            "msgs": self.msgs_no
        }

        json_data_str = json.dumps(json_data)
        self.logger.info(f"Data: {json_data_str}")
        self.socket.close()

