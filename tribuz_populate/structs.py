import datetime
from typing import TypedDict
import uuid

class Multiverse(TypedDict):
    id: uuid.UUID
    code: str
    name: str
    description: str

class Profile(TypedDict):
    id: uuid.UUID
    username: str
    fullname: str
    nickname: str
    sex: str
    birthdate: datetime.datetime
    multiverse: str
    multiverse_id: uuid.UUID
    produced_by: uuid.UUID
