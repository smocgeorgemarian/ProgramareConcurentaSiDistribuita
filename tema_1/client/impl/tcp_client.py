import logging
import os
from socket import SOCK_STREAM

from client.abstract_client import Client


class TcpClient(Client):
    def __init__(self, host, port, package_size):
        super().__init__(host, port, package_size, SOCK_STREAM)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(TcpClient.__name__)

    def _send_file(self, filename, file_fullpath):
        file_size = os.stat(file_fullpath).st_size
        packages_no = int((file_size + self.package_size - 1) // self.package_size)
        headers = f"{filename}{file_size}{packages_no}".encode()
        self.logger.info(f"Headers: {headers}")

        for try_index in range(100):
            self.socket.send(headers)

        with open(file_fullpath, "rb") as fd:
            for package_index in range(packages_no):
                data = fd.read(self.package_size)
                self.socket.send(data)

    def send(self):
        result = self._connect_wrapper()
        if result.is_fail:
            return result

        for filename, file_fullpath in self._get_samples():
            self._send_file(filename, file_fullpath)
