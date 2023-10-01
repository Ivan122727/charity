from typing import Union

from charity.helpers import SetForClass


class MailCodeTypes(SetForClass):
    reg = "reg"
    auth = "auth"


class UserRoles(SetForClass):
    user = "user"
    employee = "employee"
    dev = "dev"

class ActionType(SetForClass):
    run = "run"
    bike = "bycicle"
    walk = "walk"

RolesType = Union[set[str], list[str], str]


class Modes(SetForClass):
    prod = "prod"
    dev = "dev"
