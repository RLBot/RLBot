import os
from grpcsupport.grpc_client import make_grpc_agent

port = None

try:
    # Look for a port.cfg file in the same directory as THIS python file.
    location = os.path.realpath(
        os.path.join(os.getcwd(), os.path.dirname(__file__)))

    with open(os.path.join(location, "port.cfg"), "r") as portFile:
        port = int(portFile.readline().rstrip())

except ValueError:
    print("Failed to parse port file!")
    raise

Agent = make_grpc_agent('localhost', port)
