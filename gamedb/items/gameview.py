import attr
from gamedb.items.itms import Store as PlaceStore
from gamedb.items.itms import Platform as PlacePlatform
from gamedb.items.itms import Subscription as PlaceSubscription
from gamedb.items.itms import Franchise as GVFranchise
from gamedb.items.itms import Tag as GVTag
from gamedb.items.rels import GameSplat as PlaceGameSplat



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
        PlaceStore))
    platform = attr.ib(validator=attr.validators.instance_of(
        PlacePlatform))
    lang = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    link = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    subscription = attr.ib(validator=attr.validators.optional(
        attr.validators.instance_of(PlaceSubscription)))
    isdemo = attr.ib(converter=bool, default=False)
    
    tablename = None

    def toGameSplat(self, *, gameid):
        subscr = self.subscription.ID if self.subscription else None
        return PlaceGameSplat(gameid, self.store.ID, self.platform.ID,
                                     self.lang, self.link,
                                     subscr, self.isdemo)



@attr.s
class GameView:
    ID = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    name = attr.ib(validator=attr.validators.instance_of(str))
    year = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    franchise = attr.ib(
        validator=attr.validators.optional(
            attr.validators.instance_of(GVFranchise)))
    vote = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    priority = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(int)))
    image = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    note = attr.ib(
        validator=attr.validators.optional(attr.validators.instance_of(str)))
    tags = attr.ib(attr.validators.optional(
        _validator_list_of_type(GVTag)))
    places = attr.ib(attr.validators.optional(
        _validator_list_of_type(Place)))
    
    tablename = None

