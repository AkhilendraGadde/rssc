import socket


class Socket:
    """ A sockets class for managing commands for both client and server. """

    def __init__(self):
        """ Initializes socket object. """
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock_ser = socket

    def serverCommands(self):
        """ Settings for server """
        self.sock.bind(('', int(input("Enter port number : "))))
        self.sock.listen(int(input("Enter no of connections to listen : ")))
        return (self.sock.accept())

    def clientCommands(self):
        """ Settings for client """
        self.host = str(input("Enter Ip to connect : "))
        self.port = int(input("Enter port number : "))
        self.sock.connect((self.host, self.port))
        return (self.host, self.port)

    def shutdown(self):
        """ Closes the Tunnel completely (disables send and recv). """
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()

# end of class


if __name__ == "__main__":
    Socket()
