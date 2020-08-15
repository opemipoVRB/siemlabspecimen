#!/usr/bin/env python
# -*- coding: utf-8 -*-


from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class ApplicationServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):

        """
          Callback fired when the initial WebSocket opening handshake was completed.
          You now can send and receive WebSocket messages.

          :return:

        """
        print("WebSocket connection open.")
        self.factory.register(self)
        print("Client connected: {0}".format(self.peer))
        print("Client connected: {0}".format(self))
        self.factory.communicate(self, "Connected to Application Network", True)

    def onMessage(self, payload, isBinary):
        """

       Callback fired when a complete a message was received.

       :param payload:
       :param isBinary:
       :return:

        """
        # client is also self
        client = self

        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))


        # Send Response to every one
        self.send_broadcast_message(client, payload)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def send_private_message(self, client, message):
        """
        Response to a single client

        :param client:
        :param message:
        :return:
        """
        self.factory.communicate(client=client, payload=message, isBinary=True)

    def send_broadcast_message(self, client, message):
        """
        Broad cast a message

        :param client:
        :param message:
        :return:
        """
        self.factory.broadcast_communicate(client=client, payload=message, isBinary=True)


class ApplicationRouletteFactory(WebSocketServerFactory):

    def __init__(self, *args, **kwargs):
        super(ApplicationRouletteFactory, self).__init__(*args, **kwargs)
        self.clients = []

    def register(self, client):
        self.clients.append({'client-peer': client.peer, 'client': client})

    def unregister(self, client):
        for c in self.clients:
            if c['client-peer'] == client.peer:
                self.clients.remove(c)

    def broadcast_communicate(self, client, payload, isBinary):
        for i, c in enumerate(self.clients):
            if c['client'] == client:
                id = i
                break
        for c in self.clients:
            try:
                msg = '{0}'.format(payload.decode('utf-8'))
            except AttributeError:
                msg = '{0}'.format(payload)
            c['client'].sendMessage(str.encode(msg))

    def communicate(self, client, payload, isBinary):
        for i, c in enumerate(self.clients):
            if c['client'] == client:
                id = i
                break
        for c in self.clients:
            # print("This are the present clients   -->", c)
            if c['client'] == client:
                # print("Sending message to ", client)
                try:
                    msg = '{0}'.format(payload.decode('utf-8'))
                except AttributeError:
                    msg = '{0}'.format(payload)
                c['client'].sendMessage(str.encode(msg))


if __name__ == '__main__':
    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)

    factory = ApplicationRouletteFactory(u"ws://127.0.0.1:9000")
    factory.protocol = ApplicationServerProtocol
    # factory.setProtocolOptions(maxConnections=2)

    # note to self: if using putChild, the child must be bytes...

    reactor.listenTCP(9000, factory)
reactor.run()


