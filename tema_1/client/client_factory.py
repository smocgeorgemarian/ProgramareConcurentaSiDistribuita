from client.impl.tcp_client import TcpClient
from client.impl.udp_client import UdpClient


class ClientFactory:
    @staticmethod
    def get_client(args):
        if args.tcp:
            return TcpClient(args.host, args.port, args.package_size, args.stop_and_wait)
        if args.udp:
            return UdpClient(args.host, args.port, args.package_size, args.stop_and_wait)
        raise Exception("Unknown type")