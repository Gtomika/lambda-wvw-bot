class NotFoundException(Exception):
    pass


# When user invoking the command has no permissions!
# This is not related to GW2 API unauthorized
class CommandUnauthorizedException(Exception):
    pass
