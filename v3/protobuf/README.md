Read this to understand what's going on with protobuf: https://grpc.io/docs/quickstart/python.html

To generate the game_data_pb2* files I run this:
`python -m grpc_tools.protoc -I./v3/protobuf --python_out=./v3/protobuf --grpc_python_out=./v3/protobuf v3/protobuf/game_data.proto`