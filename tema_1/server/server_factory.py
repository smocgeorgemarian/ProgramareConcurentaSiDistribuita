from server.impl.tcp_server import TcpServer
from server.impl.udp_server import UdpServer


class ServerFactory:
    @staticmethod
    def get_server(args):
        if args.tcp:
            return TcpServer(args.host, args.port, args.package_size, args.stop_and_wait, store=args.store_answers)
        if args.udp:
            return UdpServer(args.host, args.port, args.package_size, args.stop_and_wait, store=args.store_answers)

        raise Exception("Unknown type")