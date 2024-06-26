"""
Custom exceptions we need
"""


class CannotEdit(Exception):
    """
    Use when we cannot edit config on the device
    """


class InvalidCredential(Exception):
    """
    Use when we cannot get credentials from the environment
    """


class InvalidData(Exception):
    """
    Use when the data is invalid
    """


class InvalidDeviceType(Exception):
    """
    Use when we cant determine the device type
    """
