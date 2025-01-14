import grpc
from concurrent import futures
import logging
import time
import telemetry_pb2  # Cisco telemetry .proto bindings
import telemetry_pb2_grpc  # gRPC service from Cisco proto
from google.protobuf.json_format import MessageToDict

# Configure logging to file
logging.basicConfig(
    filename="telemetry_server.log",
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Implement the service
class TelemetryServiceServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def SendTelemetry(self, request_iterator, context):
        try:
            for request in request_iterator:
                # Convert Protobuf message to dictionary for easier debugging/logging
                telemetry_data = MessageToDict(request)

                # Extract relevant fields
                controller_id = telemetry_data.get("controllerId", "Unknown")
                timestamp = telemetry_data.get("timestamp", 0)
                subscription_id = telemetry_data.get("subscriptionId", "Unknown")
                encoding = telemetry_data.get("encoding", "Unknown")

                log_message = (
                    f"Received telemetry from Controller ID: {controller_id}\n"
                    f"Subscription ID: {subscription_id}\n"
                    f"Encoding: {encoding}\n"
                    f"Timestamp: {timestamp}\n"
                    f"Telemetry Data: {telemetry_data.get('kvPairs', [])}"
                )

                # Log telemetry data to file
                logging.info(log_message)
                print(f"Telemetry received from {controller_id}. Check logs for details.")

            # Respond back to the WLC after stream ends
            return telemetry_pb2.TelemetryResponse(
                status="SUCCESS",
                message="Telemetry stream processed successfully!"
            )

        except Exception as e:
            logging.error(f"Error processing telemetry: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Internal server error: {e}")
            return telemetry_pb2.TelemetryResponse(
                status="FAILURE",
                message=f"Error: {str(e)}"
            )

def serve():
    # Server configuration and keepalive settings
    options = [
        ('grpc.keepalive_time_ms', 10000),  # Keepalive pings every 10 seconds
        ('grpc.keepalive_timeout_ms', 5000),  # Timeout for keepalive
        ('grpc.keepalive_permit_without_calls', 1),
    ]

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
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
