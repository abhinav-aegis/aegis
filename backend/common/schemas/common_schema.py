from enum import Enum

class IOrderEnum(str, Enum):
    ascendent = "ascendent"
    descendent = "descendent"


class TokenType(str, Enum):
    ACCESS = "access_token"
    REFRESH = "refresh_token"

class TokenSubjectType(str, Enum):
    USER = "user"
    CLIENT = "client"
