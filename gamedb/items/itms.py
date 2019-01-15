import attr
from datetime import date



@attr.s
class Group:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    
    tablename = 'splatgroup'



@attr.s
class Store:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    icon = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    group = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Group)))
    tablename = 'store'


@attr.s
class Platform:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    icon = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    group = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(Group)))
    tablename = 'platform'



@attr.s
class Subscription:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    icon = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    expire = attr.ib(validator=attr.validators.instance_of(date))
    
    tablename = 'subscription'
    
    # this parameter is used when an attribute is 'composite' and need some
    # kind of conversion from-to DB
    composite = {
        # name of composite parameter
        'expire': {
            # 1) 'from' = 'from database'
            'from': {
            },
            # 2) 'to' = 'to database'
            'to': {
            # 3) 'def' = 'definition to use in CREATE_TABLE'
            },
            'def': 'd INTEGER, m INTEGER, y INTEGER'
        }
    }



@attr.s
class Franchise:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    image = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    
    tablename = 'franchise'



@attr.s
class Game:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    year = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    franchise = attr.ib(
        validator=attr.validators.optional(
            attr.validators.instance_of(Franchise)))
    vote = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    priority = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    image = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    note = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    
    tablename = 'game'


@attr.s
class Tag:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    
    tablename = 'tag'
    externs = ()

