# Encodes Jewel Sockets as a 16-bit field.
#
# Socket fields:
#
# The field is divided in 4x4-bit subfields,
# each representing one socket on the item.
#
# Bit   0: Whether this socket is locked by default
# Bit 1:3: The shape of this socket
#
# Shapes:
#
# 0 - Socket unused
# 1 - Tear
# 2 - Circle
# 3 - Square
# 4 - Triangle
# 5 - Power Pin
# 6 - Shield Pin
# 7 - Sword Pin
class JewelSockets:
    def __init__(self):
        self.value = 0

    def add_socket(self, idx: int, obj: dict):
        # Whether the socket is locked by default.
        socket = (obj["m_bLockable"] << 0)

        # Encode the socket shape.
        stype = obj["m_socketType"]
        if stype.endswith("TEAR"):
            socket |= (0b001 << 1)
        elif stype.endswith("CIRCLE"):
            socket |= (0b010 << 1)
        elif stype.endswith("SQUARE"):
            socket |= (0b011 << 1)
        elif stype.endswith("TRIANGLE"):
            socket |= (0b100 << 1)
        elif stype.endswith("PINSQUAREPIP"):
            socket |= (0b101 << 1)
        elif stype.endswith("PINSQUARESHIELD"):
            socket |= (0b110 << 1)
        elif stype.endswith("PINSQUARESWORD"):
            socket |= (0b111 << 1)

        self.value |= (socket << (idx * 4))
