import attr
from datetime import date


def _date_to_bin(date):
    a = xdate.day
    b = xdate.month
    c = int(xdate.year / 100)
    d = int(xdate.year % 100)
    return bytes([a,b,c,d])


def _bin_to_date(xbin):
    day, month, y1, y2 = list(xbin)
    year = (y1 * 100) + y2
    return date(day=day, month=month, year=year)




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
    
    # dictionary of BLOB fields (fields directly written in binary)
    # every field contains an 'enc' and a 'dec' dictionary key that points to
    # a function wich requires a parameter ('enc' = encode => create binary)
    # ('dec' = decode => read binary and decode it as attribute object)
    blobs = { 'expire': 
                 {'enc': _date_to_bin, 'dec': _bin_to_date} }


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

