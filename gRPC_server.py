import grpc
from concurrent import futures
import telemetry_pb2
import telemetry_pb2_grpc
import time

# Implement the service
class TelemetryServiceServicer(telemetry_pb2_grpc.TelemetryServiceServicer):
    def SendTelemetry(self, request, context):
        print(f"Received telemetry from Controller ID: {request.controller_id}")
        print(f"Telemetry Data: {request.telemetry_data}")
        print(f"Timestamp: {request.timestamp}")

        # Respond back to the WLC
        return telemetry_pb2.TelemetryResponse(
            status="SUCCESS",
            message="Telemetry received successfully!"
        )

def serve():
    # Create a gRPC server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    telemetry_pb2_grpc.add_TelemetryServiceServicer_to_server(TelemetryServiceServicer(), server)
    
    # Bind the server to the port
    server.add_insecure_port('[::]:9090')
    print("gRPC Server listening on port 9090...")
    
    # Start the server
    server.start()
    try:
        while True:
            time.sleep(86400)  # Keep the server running
    except KeyboardInterrupt:
        print("Shutting down server...")
        server.stop(0)

if __name__ == '__main__':
    serve()
