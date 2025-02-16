# Tribuz Populate
Generate fake data for tribuz
## Features used
 - multiprocessing
 - asyncio
 - grpc
 - faker


## How to use
Install:
```
poetry install
```
Generate grpc protobuf client python files
```
poetry run python -m grpc_tools.protoc --python_out=. --grpc_python_out=. -I ../tribuz_populate $(find ./protobuf -name "*.proto")
```
Run the script:
```
poetry run python tribuz_populate/
```