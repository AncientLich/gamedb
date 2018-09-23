import attr



@attr.s
class GameTag:
    gameid = attr.ib(validator=attr.validators.instance_of(int))
    tagid = attr.ib(validator=attr.validators.instance_of(int))
    
    tablename = 'gametag'



@attr.s
class GameSplat:
    gameid = attr.ib(validator=attr.validators.instance_of(int))
    storeid = attr.ib(validator=attr.validators.instance_of(int))
    platformid = attr.ib(validator=attr.validators.instance_of(int))
    lang = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    link = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    subscriptionid = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    isdemo = attr.ib(converter=bool, default=False)
    
    tablename = 'gamesplat'

