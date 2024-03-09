from server.server_factory import ServerFactory
from utils.parser import Parser


def main():
    parser = Parser()
    args = parser.get_args()
    server = ServerFactory.get_server(args)
    server.receive()


if __name__ == '__main__':
    main()
