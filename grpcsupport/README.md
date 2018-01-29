Read this to understand what's going on with grpc / protobuf: https://grpc.io/docs/quickstart/python.html


To run a bot that uses grpc, you need to have the python module installed:
```
pip install grpcio
```

If you need to make changes to the API and regenerate the game_data_pb2* files inside the protobuf folder, run this:
```
pip install grpcio-tools

cd <one directory above this>
python -m grpc_tools.protoc -I./ --python_out=./ --grpc_python_out=./ grpcsupport/protobuf/game_data.proto
```
