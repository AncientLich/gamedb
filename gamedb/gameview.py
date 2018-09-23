import attr
import gamedb.itms
import gamedb.rels



def _validator_list_of_type(xtype):
    def validator(instance, attribute, value):
        if (not isinstance(value, (list, tuple)) 
               or not all([isinstance(v, xtype) for v in value])):
            raise ValueError(
                'attribute {} must be a list/tuple of '
                '{}'.format(attribute, xtype.__name__)) 
    return validator



@attr.s 
class Place:
    store = attr.ib(validator=attr.validators.instance_of(
        gamedb.itms.Store))
    platform = attr.ib(validator=attr.validators.instance_of(
        gamedb.itms.Platform))
    lang = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    link = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    subscription = attr.ib(validator=attr.validators.optional(
        attr.validators.instance_of(gamedb.itms.Subscription)))
    isdemo = attr.ib(converter=bool, default=False)
    
    tablename = None

    def toGameSplat(self, *, gameid):
        subscr = self.subscription.ID if self.subscription else None
        return gamedb.rels.GameSplat(gameid, self.store.ID, self.platform.ID,
                                     self.lang, self.link,
                                     subscr, self.isdemo)



@attr.s
class GameView:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    title = attr.ib(validator=attr.validators.instance_of(str))
    year = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    franchise = attr.ib(
        validator=attr.validators.optional(
            attr.validators.instance_of(gamedb.itms.Franchise)))
    vote = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    priority = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    image = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    note = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    tags = attr.ib(attr.validators.optional(
        _validator_list_of_type(gamedb.itms.Tag)))
    places = attr.ib(attr.validators.optional(
        _validator_list_of_type(Place)))
    
    tablename = None

