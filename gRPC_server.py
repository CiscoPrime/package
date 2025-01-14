import grpc
from concurrent import futures
import logging
import time
from grpc import ServicerContext

# Proto imports (manually generated telemetry_pb2 and telemetry_pb2_grpc)
import telemetry_pb2
import telemetry_pb2_grpc

# Configure logging to both console and file
logging.basicConfig(
    filename="telemetry_server.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
console_handler = logging.StreamHandler()  # Console handler for immediate output
console_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(console_handler)

# Implement the gRPC service
class TelemetryService(telemetry_pb2_grpc.TelemetryServiceServicer):
    def Subscribe(self, request_iterator, context: ServicerContext):
        """
        Handles streaming telemetry data from WLC.
        """
        for request in request_iterator:
            log_message = f"\nRAW TELEMETRY DATA RECEIVED:\n{request}\n"
            logging.info(log_message)
            print(log_message)  # Print immediately to console

        return telemetry_pb2.TelemetryResponse(
            status="SUCCESS",
            message="Telemetry stream processed successfully!"
        )

def serve():
    # Server keepalive options to maintain connection
    options = [
        ('grpc.keepalive_time_ms', 10000),  # Send keepalive pings every 10s
        ('grpc.keepalive_timeout_ms', 5000),
        ('grpc.keepalive_permit_without_calls', 1),
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.max_ping_strikes', 0),
    ]

    # Create gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryService(), server)
    server.add_insecure_port('[::]:9090')
    logging.info("gRPC Server started, listening on port 9090...")
    print("gRPC Server started, listening on port 9090...")
    
    # Start the server
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep the server running
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
 