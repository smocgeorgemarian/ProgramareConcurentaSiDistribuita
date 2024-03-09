from server.impl.tcp_server import TcpServer


class ServerFactory:
    @staticmethod
    def get_server(args):
        if args.tcp:
            return TcpServer(args.host, args.port, args.package_size)

        raise Exception("Unknown type")