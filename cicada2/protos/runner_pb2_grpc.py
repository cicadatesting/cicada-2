# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from cicada2.protos import runner_pb2 as cicada2_dot_protos_dot_runner__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2


class RunnerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Action = channel.unary_unary(
                '/cicada_2.Runner/Action',
                request_serializer=cicada2_dot_protos_dot_runner__pb2.ActionRequest.SerializeToString,
                response_deserializer=cicada2_dot_protos_dot_runner__pb2.ActionReply.FromString,
                )
        self.Assert = channel.unary_unary(
                '/cicada_2.Runner/Assert',
                request_serializer=cicada2_dot_protos_dot_runner__pb2.AssertRequest.SerializeToString,
                response_deserializer=cicada2_dot_protos_dot_runner__pb2.AssertReply.FromString,
                )
        self.Healthcheck = channel.unary_unary(
                '/cicada_2.Runner/Healthcheck',
                request_serializer=google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
                response_deserializer=cicada2_dot_protos_dot_runner__pb2.HealthcheckReply.FromString,
                )


class RunnerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Action(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Assert(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Healthcheck(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_RunnerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Action': grpc.unary_unary_rpc_method_handler(
                    servicer.Action,
                    request_deserializer=cicada2_dot_protos_dot_runner__pb2.ActionRequest.FromString,
                    response_serializer=cicada2_dot_protos_dot_runner__pb2.ActionReply.SerializeToString,
            ),
            'Assert': grpc.unary_unary_rpc_method_handler(
                    servicer.Assert,
                    request_deserializer=cicada2_dot_protos_dot_runner__pb2.AssertRequest.FromString,
                    response_serializer=cicada2_dot_protos_dot_runner__pb2.AssertReply.SerializeToString,
            ),
            'Healthcheck': grpc.unary_unary_rpc_method_handler(
                    servicer.Healthcheck,
                    request_deserializer=google_dot_protobuf_dot_empty__pb2.Empty.FromString,
                    response_serializer=cicada2_dot_protos_dot_runner__pb2.HealthcheckReply.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'cicada_2.Runner', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Runner(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Action(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/cicada_2.Runner/Action',
            cicada2_dot_protos_dot_runner__pb2.ActionRequest.SerializeToString,
            cicada2_dot_protos_dot_runner__pb2.ActionReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Assert(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/cicada_2.Runner/Assert',
            cicada2_dot_protos_dot_runner__pb2.AssertRequest.SerializeToString,
            cicada2_dot_protos_dot_runner__pb2.AssertReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Healthcheck(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/cicada_2.Runner/Healthcheck',
            google_dot_protobuf_dot_empty__pb2.Empty.SerializeToString,
            cicada2_dot_protos_dot_runner__pb2.HealthcheckReply.FromString,
            options, channel_credentials,
            call_credentials, compression, wait_for_ready, timeout, metadata)