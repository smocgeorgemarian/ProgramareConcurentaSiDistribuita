from client.client_factory import ClientFactory
from utils.parser import Parser


def main():
    parser = Parser()
    args = parser.get_args()
    client = ClientFactory.get_client(args)
    client.send()


if __name__ == '__main__':
    main()
