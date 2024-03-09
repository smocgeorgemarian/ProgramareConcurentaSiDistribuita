class ClientFactory:
    @staticmethod
    def get_client(args):
        if args.tcp:
            return TcpServer(args.host, args.port, args.package_size)

        raise Exception("Unknown type")