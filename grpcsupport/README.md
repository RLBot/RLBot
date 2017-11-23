Read this to understand what's going on with grpc / protobuf: https://grpc.io/docs/quickstart/python.html

To generate the game_data_pb2* files inside the protobuf folder I run this:
```
cd <one directory above this>
python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ grpcsupport/protobuf/game_data.proto
```
