from typing import Any
from grpc import Channel, aio
from tribuz_populate.bigbang.assault import Ammo
from tribuz_populate.protobuf import multiverses_pb2, multiverses_pb2_grpc
from tribuz_populate.structs import Multiverse


class MultiverseAmmo(Ammo):
    def get_caliber(self) -> str:
        return 'code'
    
    def load(self, channel: Channel) -> multiverses_pb2_grpc.MultiverseServiceStub:
        return multiverses_pb2_grpc.MultiverseServiceStub(channel)
    
    async def fire(self, gun: multiverses_pb2_grpc.MultiverseServiceStub, bullet: Multiverse) -> Multiverse:
        multiverse_created = {}
        try: 
            multiverse_created = await gun.CreateMultiverse(multiverses_pb2.MultiverseCreateRequest(
                code=bullet['code'],
                name=bullet['name'],
                description=bullet['description']
            ))
        except aio.AioRpcError as ex:
            multiverse_created = await gun.GetMultiverseByCode(multiverses_pb2.MultiverseGetByCodeRequest(
                code=bullet['code']
            ))
        except Exception as ex:
            raise ex
        return {
            'id': multiverse_created.id,
            'code': multiverse_created.code,
            'name': multiverse_created.name,
            'description': multiverse_created.description
        }
