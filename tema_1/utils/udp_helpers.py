from enum import Enum


class DatagramType(Enum):
    INITIAL_HEADER = 1
    CHUNK = 2
    END_MESSAGE = 3


class UdpResponse:
    def __init__(self, raw_response):
        decoded: str = raw_response.decode()
        splitted_data = decoded.split("\n")
        type = int(splitted_data[0])
        self.type = DatagramType(type)
        if self.type == DatagramType.INITIAL_HEADER:
            self.filename = splitted_data[1]
            self.file_index = splitted_data[2]
            self.file_size = splitted_data[3]
        elif self.type == DatagramType.CHUNK:
            self.file_index = splitted_data[1]
            self.file_size = splitted_data[2]
            self.packages_no = splitted_data[3]
            self.package_index = splitted_data[4]
            self.data = splitted_data[5]
        else:
            self.data = splitted_data[1]

