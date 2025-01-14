import grpc
from concurrent import futures
import logging
from cisco_gnmi import proto
from cisco_gnmi.proto import telemetry_pb2
import time

# Configure logging to file
logging.basicConfig(
    filename="telemetry_server.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Implement the telemetry service
class GNMITelemetryService(proto.gNMIProtoServicer):
    def Subscribe(self, request_iterator, context):
        """
        Handles streaming telemetry data from WLC.
        """
        for request in request_iterator:
            subscription_path = request.subscription_list.path
            log_message = f"Telemetry stream received from {subscription_path}:\n"

            for update in request.update:
                for kv in update.kv:
                    log_message += f"  {kv.key}: {kv.value}\n"

            logging.info(log_message)
            print(f"Telemetry received and logged from {subscription_path}")

        return proto.SubscribeResponse(
            response=proto.SubscribeResponse.Update(
                update="Telemetry stream processed successfully!"
            )
        )

def serve():
    options = [
        ('grpc.keepalive_time_ms', 10000),
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', 1),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.max_ping_strikes', 0),
    ]

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    
    # Add telemetry service
    proto.add_gNMIProtoServicer_to_server(GNMITelemetryService(), server)
    server.add_insecure_port('[::]:9090')
    logging.info("gRPC Server started, listening on port 9090...")
    print("gRPC Server started, listening on port 9090...")
    
    # Start the server
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep the server alive for 24 hours
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
