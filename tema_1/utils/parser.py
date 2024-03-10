import argparse


class Parser:
    def __init__(self):
        pass

    def get_args(self):
        parser = argparse.ArgumentParser(description="Server IP and Port Argument Parser")
        parser.add_argument("--host", type=str, default="127.0.0.1", help="Server IP address")
        parser.add_argument("--port", type=int, default=8081, help="Server port number")
        parser.add_argument("--package-size", type=int, default=8192, help="Size of a packet sent via network")
        parser.add_argument("--tcp", action='store_true', default=False, help="Use tcp for data transfer")
        parser.add_argument("--udp", action='store_true', default=False, help="Use tcp for data transfer")
        parser.add_argument("--stop-and-wait", action='store_true', default=False, help="Ack for every message")
        return parser.parse_args()
