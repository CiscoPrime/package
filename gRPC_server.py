import grpc
from concurrent import futures
import telemetry_pb2
import telemetry_pb2_grpc
import time
import logging
from grpc._cython import cygrpc

# Configure logging to file
logging.basicConfig(
    filename="telemetry_server.log",  # Log file name
    filemode='a',  # Append to file
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Log INFO level and above
)

# Implement the service
class TelemetryServiceServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def SendTelemetry(self, request, context):
        try:
            log_message = (
                f"Received telemetry from Controller ID: {request.controller_id}\n"
                f"Telemetry Data: {request.telemetry_data}\n"
                f"Timestamp: {request.timestamp}"
            )
            logging.info(log_message)
            print(f"Telemetry received from {request.controller_id}. Check logs for details.")

            # Respond back to the WLC
            return telemetry_pb2.TelemetryResponse(
                status="SUCCESS",
                message="Telemetry received successfully!"
            )

        except Exception as e:
            logging.error(f"Error processing request: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Internal server error')
            return telemetry_pb2.TelemetryResponse(
                status="FAILURE",
                message=f"Error: {str(e)}"
            )

def serve():
    # Keep-alive settings to prevent connection issues
    options = [
        ('grpc.keepalive_time_ms', 10000),  # Send keepalive pings every 10 seconds
        ('grpc.keepalive_timeout_ms', 5000),  # Timeout for keepalive
        ('grpc.keepalive_permit_without_calls', 1),  # Allow pings even without active calls
        ('grpc.http2.min_time_between_pings_ms', 10000),
        ('grpc.http2.max_pings_without_data', 0),
        ('grpc.http2.max_ping_strikes', 0),
    ]

    # Create a gRPC server with the configured options
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    
    # Add the service to the server
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryServiceServicer(), server)
    
    # Bind the server to port 9090
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
