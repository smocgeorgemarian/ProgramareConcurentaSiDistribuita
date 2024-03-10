import json
import logging
import os
import subprocess
import time
from threading import Thread

BASE = os.path.join(os.path.dirname(__file__), "..")

VENV_PATH = os.path.join(BASE, ".venv", "bin", "python3")
CL_PATH = os.path.join(BASE, "client", "main_client.py")
SV_PATH = os.path.join(BASE, "server", "main_server.py")


class StatsGatherer:
    def __init__(self, runs_no=10):
        self.runs_no = runs_no
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(StatsGatherer.__name__)
        self.server = None
        self.client = None

    def run_command(self, commands, is_server):
        print(commands, is_server)
        process = subprocess.run(commands, capture_output=True, text=True)
        if is_server:
            self.server = process.stdout
        else:
            self.client = process.stdout

    def run(self):
        port = 10_000

        stats = {}
        for protocol in ["--tcp", "--udp"]:
            # either exists or not
            for wait_and_stop in ["", "--stop-and-wait"]:
                for run_index in range(self.runs_no):

                    if wait_and_stop:
                        command_list_sv = [VENV_PATH, SV_PATH, protocol, wait_and_stop, "--port", str(port)]
                        command_sv = " ".join(command_list_sv)

                        command_list_cl = [VENV_PATH, CL_PATH, protocol, wait_and_stop, "--port", str(port)]
                        command_cl = " ".join(command_list_cl)

                    else:
                        command_list_sv = [VENV_PATH, SV_PATH, protocol, "--port", str(port)]
                        command_sv = " ".join(command_list_sv)

                        command_list_cl = [VENV_PATH, CL_PATH, protocol, "--port", str(port)]
                        command_cl = " ".join(command_list_cl)

                    sv = Thread(target=self.run_command, args=(command_list_sv, True))
                    sv.start()
                    self.logger.info("Hehe")
                    cl = Thread(target=self.run_command, args=(command_list_cl, False))
                    cl.start()

                    sv.join()
                    cl.join()

                    self.logger.info(f"Commands:\nServer: {command_sv}\nClient: {command_cl}")
                    process1 = subprocess.run(command_list_sv, capture_output=True, text=True)
                    print("Pass")
                    time.sleep(0.5)
                    process2 = subprocess.run(command_list_cl, capture_output=True, text=True)

                    config = f"protocol={protocol}|wait_and_stop={wait_and_stop}|run_index={run_index}"
                    stats[config] = {
                        "sv": process1,
                        "cl": process2
                    }

                    time.sleep(0.5)
                    print(process1, process2)
                    port += 1

        with open("stats.json", "w") as fd:
            json.dump(stats, fd, indent=4)


if __name__ == '__main__':
    # print(os.path.exists("/home/georges/work/pcd/ProgramareConcurentaSiDistribuita/tema_1/utils/../server/main_server.py"))
    gatherer = StatsGatherer().run()
