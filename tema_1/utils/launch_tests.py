import logging
import os
import subprocess
import time

BASE = os.path.join(os.path.dirname(__file__), "..")

VENV_PATH = os.path.join(BASE, ".venv", "bin", "python3")
CL_PATH = os.path.join(BASE, "client", "main_client.py")
SV_PATH = os.path.join(BASE, "server", "main_server.py")


class StatsGatherer:
    def __init__(self, runs_no=10):
        self.runs_no = runs_no
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(StatsGatherer.__name__)

    def run(self):
        for protocol in ["--tcp", "--udp"]:
            # either exists or not
            for wait_and_stop in ["", "--stop-and-wait"]:
                for run_index in range(self.runs_no):
                    if wait_and_stop:
                        command_list = [VENV_PATH, SV_PATH, protocol, wait_and_stop]
                        command = " ".join([VENV_PATH, SV_PATH, protocol, wait_and_stop])
                    else:
                        command_list = [VENV_PATH, SV_PATH, protocol]
                        command = " ".join([VENV_PATH, SV_PATH, protocol])

                    self.logger.info(f"Command: {command}")
                    process1 = subprocess.Popen(command_list, stdout=subprocess.PIPE)
                    process2 = subprocess.Popen(command_list, stdout=subprocess.PIPE)

                    process1.wait()
                    process2.wait()
                    data_1 = process1.communicate()
                    data_2 = process2.communicate()
                    time.sleep(3)
                    print(data_1, data_2)


if __name__ == '__main__':
    # print(os.path.exists("/home/georges/work/pcd/ProgramareConcurentaSiDistribuita/tema_1/utils/../server/main_server.py"))
    gatherer = StatsGatherer().run()

