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
