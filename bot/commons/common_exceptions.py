class NotFoundException(Exception):
    """
    Generic resource not found.
    """
    pass


class CommandUnauthorizedException(Exception):
    """
    Thrown when user is not authorized to perform a command.
    """
    pass


class HomeWorldNotSetException(Exception):
    """
    Thrown when a command requires the guild home world set, but it was not.
    """
    pass


class InvalidWorldException(Exception):
    """
    Thrown when the GW2 world name specified by the user was not valid.
    """

    def __init__(self, world_name: str):
        self.world_name = world_name


class OptionNotFoundException(Exception):
    """
    Thrown when the selected option was not present in the Discord interaction.
    """
    pass
