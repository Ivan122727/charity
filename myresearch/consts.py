from typing import Union

from myresearch.helpers import SetForClass


class MailCodeTypes(SetForClass):
    reg = "reg"
    auth = "auth"


class UserRoles(SetForClass):
    user = "user"
    employee = "employee"
    dev = "dev"

class FundCategories(SetForClass):
    family = "Семья"
    health = "Здоровье"
    animals = "Животные"

RolesType = Union[set[str], list[str], str]


class Modes(SetForClass):
    prod = "prod"
    dev = "dev"
