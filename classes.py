from dataclasses import dataclass

@dataclass
class VM:
    ID: str
    profile: str
    vCPU: int
    RAM: int
    disk: int
    group: str

@dataclass
class Server:
    ID: str
    s_type: str
    vCPU: int
    RAM: int
    disk: int
    qty: int
