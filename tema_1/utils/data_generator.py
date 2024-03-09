import logging
import os
import random

from faker import Faker

from utils.general import SAMPLES_DIR


class DataGenerator:
    def __init__(self, files_no=50):
        self.files_no = files_no
        self.faker = Faker()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(DataGenerator.__name__)
        os.makedirs(SAMPLES_DIR, exist_ok=True)

    def generate(self):
        for file_index in range(self.files_no):
            size = random.randint(10_000, 20_000)
            text = "".join([self.faker.word() for _ in range(size)]).encode()
            with open(os.path.join(SAMPLES_DIR, f"file_{file_index}"), "wb") as fd:
                fd.write(text)


if __name__ == '__main__':
    DataGenerator().generate()
