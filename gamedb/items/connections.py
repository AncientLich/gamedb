from gamedb.items.itms import Group as RlGroup
from gamedb.items.itms import Store as RlStore
from gamedb.items.itms import Platform as RlPlatform
from gamedb.items.itms import Subscription as RlSubscription
from gamedb.items.itms import Franchise as RlFranchise
from gamedb.items.itms import Game as RlGame
from gamedb.items.itms import Tag as RlTag
from gamedb.items.rels import GameTag as RlGameTag
from gamedb.items.rels import GameSplat as RlGameSplat
from collections import OrderedDict



def rules_ordered():
    rules = OrderedDict()
    rules[RlGroup] = {}
    rules[RlStore] = {'group': RlGroup}
    rules[RlPlatform] = {'group': RlGroup}
    rules[RlSubscription] = {}
    rules[RlFranchise] = {}
    rules[RlGame] = {'franchise': RlFranchise}
    rules[RlTag] = {}
    rules[RlGameTag] = ((RlGame, RlTag), {})
    rules[RlGameSplat] = (
        (RlGame, RlStore, RlPlatform), 
        {'subscriptionid': RlSubscription}
    )
    return rules



def rules():
    return dict(rules_ordered())



def connections():
    return {
        RlGame: {
            RlTag: RlGameTag,
            RlStore: RlGameSplat,
            RlPlatform: RlGameSplat
        },
        RlTag: {
            RlGame: RlGameTag
        },
        RlStore: {
            RlGame: RlGameSplat,
            RlPlatform: RlGameSplat
        },
        RlPlatform: {
            RlGame: RlGameSplat,
            RlStore: RlGameSplat
        },
        RlSubscription: {
            RlGame: RlGameSplat,
            RlStore: RlGameSplat,
            RlPlatform: RlGameSplat,
        },
        RlFranchise: {
            RlGame: RlGame
        },
        RlGroup: {
            RlStore: RlStore,
            RlPlatform: RlPlatform
        }
    }

