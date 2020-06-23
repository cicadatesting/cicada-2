from concurrent import futures
import logging

import grpc

import app_pb2
import app_pb2_grpc


class Greeter(app_pb2_grpc.GreeterServicer):

    def SayHello(self, request, context):
        for key, value in context.invocation_metadata():
            print('Received initial metadata: key=%s value=%s' % (key, value))

        return app_pb2.HelloReply(message='Hello, %s!' % request.name)

    def SayHelloCS(self, requests, context):
        names = []

        for request in requests:
            names.append(request.name)

        return app_pb2.HelloReply(message=f"Hello {', '.join(names)}")

    def SayHelloSS(self, request, context):
        yield app_pb2.HelloReply(message='Hello, %s!' % request.name)

    def SayHelloBI(self, requests, context):
        context.set_trailing_metadata((
            ('checksum-bin', b'I agree'),
            ('retry', 'false'),
        ))

        for request in requests:
            yield app_pb2.HelloReply(message='Hello, %s!' % request.name)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    app_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
