import enum

class PacketLabel(str, enum.Enum):
    PENDING = "PENDING"
    BENIGN = "BENIGN"
    ATTACK = "ATTACK"