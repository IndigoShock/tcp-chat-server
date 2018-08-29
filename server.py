from client import ChatClient
import random
import threading
import socket
import sys


PORT = random.randrange(5000,9999)


class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
        """Upon initiation, this will look for the port, server. The server
        looks for a socket with AF_INET, sock stream and proto tcp. The try
        will create the server and host. If the socket has an error,
        a statement will show up and tell the host a bind failed. And exit
        out of the system. After the try-except, the server will listen.
        """
        super().__init__(daemon=True)
        self.port = port
        self.host = host
        self.server = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM,
            socket.IPPROTO_TCP
        )
        self.client_pool = []

        try:
            self.server.bind((self.host, self.port))
        except socket.error:
            print('Bind failed {}'.format(socket.error))
            sys.exit()

        self.server.listen(10)

    def parser(self, client, message):
        """ This method will take the input from the client. Several are
        included: the quit, list, nickname and dm. The quit will have the
        client leave the chatroom and close their connection. The list will
        let the client know who every user is in the chatroom.
        The nickname will allow the client to update their current
        name to whatever they would like. The dm will allow
        the client to message another user directly.
        """
        if message.decode().startswith('/'):
            data = message.decode().split(maxsplit=2)
            if data[0] == '/quit':
                client.conn.sendall(b'You have left the chat.')
                reply = client.nick.encode() + b'has left the channel.\n'
                [c.conn.sendall(reply) for c in self.client_pool if
                    len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                client.conn.close()

            elif data[0] == '/list':
                reply = b'This is a list of everyone in the channel.\n'
                for client in self.client_pool:
                    reply += '{}\n'.format(client.nick).encode()
                [c.conn.sendall(reply) for c in self.client_pool if
                    len(self.client_pool)]
            elif data[0] == '/nickname':

                new_name = data[1]
                client.nick = new_name
                reply = 'Your name is now: {}\n'.format(client.nick).encode()
                client.conn.sendall(reply)

            elif data[0] == '/dm':
                for client in self.client_pool:
                    if data[1] == client.nick:
                        client.conn.sendall(data[2].encode())

            else:
                client.conn.sendall(b'Invalid command. Please try again.\n')

        else:
            reply = client.nick.encode() + b': ' + message
            [c.conn.sendall(reply) for c in self.client_pool if
                len(self.client_pool)]

    def run_thread(self, client):
        """This will let the client know the port and address they are
        connecting to. If not connected, they will have an exception with
        three possibilities: Connection, brokenpipe or OS error. If exception,
        thrown, they will have their connection closed.
        """
        print('{} connected with {}:{}'.format(
            client.nick, client.addr[0], str(client.addr[1])))
        try:
            while True:
                data = client.conn.recv(4096)
                self.parser(client, data)
        except (ConnectionResetError, BrokenPipeError, OSError):
            client.conn.close()

    def run(self):
        """Once this method is run, the server will start and find the
        connection. While true, the address and client will stay connected.
        Once all these arguments are taken into account, the server will start.
        """
        print('Server running on {}'.format(PORT))
        while True:
            conn, addr = self.server.accept()
            client = ChatClient(conn, addr)
            self.client_pool.append(client)
            threading.Thread(
                target=self.run_thread,
                args=(client,),
                daemon=True
            ).start()

    def exit(self):
        """This will exit out of the server.
        """
        print('Thanks for stopping by!')
        self.server.close()


if __name__ == '__main__':
    """This is the main method and will run the server. If the server
    doesn't run, a KeyboardInterrupt exception will throw
    and close the connection.
    """
    server = ChatServer(PORT)
    try:
        server.run()
    except KeyboardInterrupt:
        [c.conn.close() for c in server.client_pool if len(server.client_pool)]
        server.exit()

