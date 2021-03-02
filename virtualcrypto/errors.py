class VirtualCryptoException(Exception):
    pass


class MissingScope(VirtualCryptoException):
    pass


class HTTPException(VirtualCryptoException):
    pass


class BadRequest(HTTPException):
    pass


class NotFound(HTTPException):
    pass
