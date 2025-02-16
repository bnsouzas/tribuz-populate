from typing import Any
from grpc import Channel, aio
from tribuz_populate.bigbang.assault import Ammo
from tribuz_populate.protobuf import multiverses_pb2, multiverses_pb2_grpc, profiles_pb2, profiles_pb2_grpc
from tribuz_populate.structs import Multiverse, Profile
from datetime import datetime


class ProfileAmmo(Ammo):
    def get_caliber(self) -> str:
        return 'username'
    
    def load(self, channel: Channel) -> profiles_pb2_grpc.ProfileServiceStub:
        return profiles_pb2_grpc.ProfileServiceStub(channel)
    
    async def fire(self, gun: profiles_pb2_grpc.ProfileServiceStub, bullet: Profile) -> Profile:
        username_created = {}
        try: 
            username_created = await gun.CreateProfile(profiles_pb2.ProfileCreateRequest(
                multiverse_id=bullet['multiverse_id'],
                username=bullet['username'],
                fullname=bullet['fullname'],
                nickname=bullet['nickname'],
                sex=bullet['sex'],
                birthdate=datetime.combine(bullet['birthdate'], datetime.min.time())
            ))
        except aio.AioRpcError as ex:
            username_created = await gun.GetProfileByUsername(profiles_pb2.ProfileGetByUsernameRequest(
                username=bullet['username']
            ))
        except Exception as ex:
            raise ex
        return {
            'id': username_created.id,
            'multiverse_id': username_created.multiverse_id,
            'username': username_created.username,
            'fullname': username_created.fullname,
            'nickname': username_created.nickname,
            'sex': username_created.sex,
            'birthdate': username_created.birthdate
        }
