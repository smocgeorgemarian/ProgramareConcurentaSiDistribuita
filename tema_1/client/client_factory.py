from client.impl.tcp_client import TcpClient
from client.impl.udp_client import UdpClient


class ClientFactory:
    @staticmethod
    def get_client(args):
        if args.tcp:
            return TcpClient(args.host, args.port, args.package_size)
        if args.udp:
            return UdpClient(args.host, args.port, args.package_size)
        raise Exception("Unknown type")