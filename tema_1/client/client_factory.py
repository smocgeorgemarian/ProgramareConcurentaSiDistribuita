from client.impl.tcp_client import TcpClient


class ClientFactory:
    @staticmethod
    def get_client(args):
        if args.tcp:
            return TcpClient(args.host, args.port, args.package_size)

        raise Exception("Unknown type")