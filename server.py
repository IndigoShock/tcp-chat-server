from client import ChatClient
import threading
import socket
import sys


PORT = 9996 or 7364 or 1344 or 1842 or 4302 or 3857


class ChatServer(threading.Thread):
    def __init__(self, port, host='localhost'):
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
        if message.decode().startswith('@'):
            data = message.decode().split(maxsplit=2)
            if data[0] == '@quit':
                client.conn.sendall(b'You have left the chat.')
                reply = client.nick.encode() + b'has left the channel.\n'
                [c.conn.sendall(reply) for c in self.client_pool if
                    len(self.client_pool)]
                self.client_pool = [c for c in self.client_pool if c.id != id]
                client.conn.close()

            elif data[0] == '@list':
                reply = b'This is a list of everyone in the channel.\n'
                for client in self.client_pool:
                    reply += '{}\n'.format(client.nick).encode()
                client.conn.sendall(reply)

            elif data[0] == '@nickname':
                new_name = data[1]
                client.nick = new_name
                reply = 'Your name is now: {}\n'.format(client.nick).encode()
                client.conn.sendall(reply)

            elif data[0] == '@dm':
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
        print('{} connected with {}:{}'.format(client.nick, client.addr[0], str(client.addr[1])))
        try:
            while True:
                data = client.conn.recv(4096)
                self.parser(client, data)
        except (ConnectionResetError, BrokenPipeError, OSError):
            client.conn.close()

    def run(self):
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
        self.server.close()


if __name__ == '__main__':
    server = ChatServer(PORT)
    try:
        server.run()
    except KeyboardInterrupt:
        [c.conn.close() for c in server.client_pool if len(server.client_pool)]
        server.exit()
