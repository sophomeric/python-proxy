#!/usr/bin/env python
#import Queue
import binascii
import select, socket, ssl
from sys import exit

buffer_size = 4096
# Test bad server
#forward_to = ('192.168.50.19', 853)
# Cloudflare
forward_to = ('1.1.1.1', 853)
bind_to = ('0.0.0.0', 53)
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)

def format_hp(hp_tuple):
    return ':'.join(map(str,hp_tuple))

class Proxy:
    # Sockets from which we expect to read
    inputs  = []
    # Sockets to which we expect to write
    outputs = []
    # Outgoing message queues (socket:Queue)
    message_queues = {}

    def __init__(self):
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print('Starting up on {0}:{1}'.format(bind_to[0], bind_to[1]))
        self.proxy.bind(bind_to)
        self.proxy.listen(5)

    def start(self):
        self.inputs.append(self.proxy)
        while True:
            selector = select.select
            rlist, wlist, xlist = selector(self.inputs, self.outputs, self.inputs)
            for s in rlist:
                """
                If the socket is the main "server" socket, the one being used to listen for connections, then the "readable" condition means it is ready to accept another incoming connection.
                """
                if s is self.proxy:
                    forward = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM))
                    forward.settimeout(5)
                    print('Connecting to backend {0}'.format(format_hp(forward_to)))
                    forward.connect(forward_to)
                    connection, client_address = s.accept()
                    print('Connected; {0}'.format(format_hp(client_address)))
                    connection.setblocking(0)
                    self.inputs.append(connection)
                    self.inputs.append(forward)
                    self.message_queues[connection] = forward
                    #self.message_queues[connection] = Queue.Queue()
                    #self.message_queues[connection].put(forward)
                    self.message_queues[forward] = connection
                    #self.message_queues[forward] = Queue.Queue()
                    #self.message_queues[forward].put(connection)
                # Established connection with a client that has sent data.
                else:
                    data = s.recv(buffer_size)
                    if data:
                        # A readable client socket has data
                        print('Received; {1}; "{0}"'.format(data, format_hp(s.getpeername())))
                        print('Hex response: {0}'.format(binascii.hexlify(data).decode("utf-8")))
                        self.message_queues[s].send(data)
                        # Add output channel for response
                        if s not in self.outputs:
                            self.outputs.append(s)
                    # A readable socket without data available is from a client that has disconnected, and the stream is ready to be closed.
                    else:
                        print('Closing; {0}.'.format(format_hp(client_address)))
                        # Stop listening for input on the connection
                        if s in self.outputs:
                            self.outputs.remove(s)
                        self.inputs.remove(s)
                        s.close()

                        # Remove message queue
                        del self.message_queues[s]
            # Not needed since we're just crossing the (data) streams now
            #for s in wlist:
            #    try:
            #        next_msg = self.message_queues[s].get_nowait()
            #    except Queue.Empty:
            #        print('Output queue for {0} is empty, removing it.'.format(s.getpeername()))
            #        self.outputs.remove(s)
            #    else:
            #        print('Sending "{0}" to {1}.'.format(next_msg, s.getpeername()))
            #        s.send(next_msg)
            for s in xlist:
                print('Excpetion for {0}, closing connection.'.format(s.getpeername()))
                self.inputs.remove(s)
                if s in self.outputs:
                    self.outputs.remove(s)
                s.close()

                # Remove message queue
                del self.message_queues[s]

if __name__ == '__main__':
        proxy_server = Proxy()
        try:
            proxy_server.start()
        except KeyboardInterrupt:
            print('Received Ctrl+C, shutting down.')
            exit(1)
