import logging
import os
import random
from concurrent.futures import ThreadPoolExecutor

from faker import Faker

from utils.general import SAMPLES_DIR


class DataGenerator:
    def __init__(self, files_no=5000):
        self.files_no = files_no
        self.faker = Faker()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(DataGenerator.__name__)
        os.makedirs(SAMPLES_DIR, exist_ok=True)

    def write_file(self, file_index):
        size = random.randint(100_000, 200_000)
        text = "".join([self.faker.word() for _ in range(size)]).encode()
        with open(os.path.join(SAMPLES_DIR, f"file_{file_index}"), "wb") as fd:
            fd.write(text)

        self.logger.info(f"Finished file with index: {file_index}")

    def generate(self):
        with ThreadPoolExecutor(max_workers=10) as tp:
            for file_index in range(self.files_no):
                tp.submit(self.write_file, file_index)

        self.logger.info("Done")


if __name__ == '__main__':
    DataGenerator().generate()
