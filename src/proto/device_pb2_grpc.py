# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import proto.device_pb2 as device__pb2


class MessageBrokerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.SendDeviceMessage = channel.unary_unary(
            "/MessageBroker/SendDeviceMessage",
            request_serializer=device__pb2.DeviceMessage.SerializeToString,
            response_deserializer=device__pb2.DeviceMessage.FromString,
        )


class MessageBrokerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def SendDeviceMessage(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details("Method not implemented!")
        raise NotImplementedError("Method not implemented!")


def add_MessageBrokerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        "SendDeviceMessage": grpc.unary_unary_rpc_method_handler(
            servicer.SendDeviceMessage,
            request_deserializer=device__pb2.DeviceMessage.FromString,
            response_serializer=device__pb2.DeviceMessage.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler("MessageBroker", rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class MessageBroker(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def SendDeviceMessage(
        request,
        target,
        options=(),
        channel_credentials=None,
        call_credentials=None,
        insecure=False,
        compression=None,
        wait_for_ready=None,
        timeout=None,
        metadata=None,
    ):
        return grpc.experimental.unary_unary(
            request,
            target,
            "/MessageBroker/SendDeviceMessage",
            device__pb2.DeviceMessage.SerializeToString,
            device__pb2.DeviceMessage.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
        )
