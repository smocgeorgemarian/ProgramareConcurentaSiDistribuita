import os
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

    def _connect_wrapper(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def _get_packages_no(self, file_fullpath):
        return int((os.stat(file_fullpath).st_size + self.package_size - 1) // self.package_size)

    def _get_samples(self):
        for index, filename in enumerate(os.listdir(self.samples_dir)):
            if index == 100:
                break
            yield filename, os.path.join(self.samples_dir, filename)

    def _send_file(self, fd, headers, packages_no, **kwargs):
        raise NotImplementedError("Subclass must implement abstract method")

    def _send_finished_transmission(self):
        raise NotImplementedError("Subclass must implement abstract method")

    @stats_after_run
    def send(self):
        result = self._connect_wrapper()
        if result.is_fail:
            return result

        for file_index, (filename, file_fullpath) in enumerate(self._get_samples()):
            file_size = os.stat(file_fullpath).st_size
            packages_no = int((file_size + self.package_size - 1) // self.package_size)

            with open(file_fullpath, "rb") as fd:
                self._send_file(fd, packages_no, **{"filename": filename, "file_index": file_index, "file_size": file_size})

        # Ended work
        self._send_finished_transmission()
        self.socket.close()

