from config import (
    SERVER_HOST,
    SERVER_PORT,
)


class Server:
    def __init__(self, host=SERVER_HOST, port=SERVER_PORT,):
        self.host = host
        self.port = port

    async def listen(self):
        try:
            server = await asyncio.start_server(
                self.process_client, self.host, self.port,
            )
            logger.info("Server is initialized at %s", server.sockets[0].getsockname())
            async with server:
                await server.serve_forever()
        except Exception as e:
            logger.error("Error detected: %s", e)
        except KeyboardInterrupt:
            logger.info("Shutting down the server")


    def process_client(self, reader: StreamReader, writer: StreamWriter):
        # add client
        # handle messages
        # remove client
        pass
