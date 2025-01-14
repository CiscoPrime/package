import grpc
from concurrent import futures
import telemetry_pb2
import telemetry_pb2_grpc
import time
import logging

# Configure logging
logging.basicConfig(
    filename="telemetry_server.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Implement the service
class TelemetryServiceServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def SendTelemetry(self, request_iterator, context):
        for request in request_iterator:
            log_message = (
                f"Received telemetry from Controller ID: {request.controller_id}\n"
                f"Subscription ID: {request.subscription_id}\n"
                f"Encoding: {request.encoding}\n"
                f"Timestamp: {request.timestamp}\n"
                f"Telemetry Data:"
            )

            # Log each key-value pair
            for kv_pair in request.kv_pairs:
                log_message += f"\n  {kv_pair.key}: {kv_pair.value}"

            logging.info(log_message)
            print(f"Telemetry received from {request.controller_id}. Check logs for details.")
        
        return telemetry_pb2.TelemetryResponse(
            status="SUCCESS",
            message="Telemetry stream processed successfully!"
        )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryServiceServicer(), server)
    server.add_insecure_port('[::]:9090')
    logging.info("gRPC Server started, listening on port 9090...")
    print("gRPC Server started, listening on port 9090...")
    server.start()
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        logging.info("Shutting down server...")
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
