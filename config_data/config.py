from dataclasses import dataclass
from environs import Env


@dataclass
class TCSClient:
    token: str
    id: str


@dataclass
class Config:
    tcs_client: TCSClient


def load_config(path: str = None) -> Config:
    env: Env = Env()
    env.read_env(path)

    return Config(tcs_client=TCSClient(token=env('TINKOFF_TOKEN'), id=env('TINKOFF_ACCOUNT')))
                                    