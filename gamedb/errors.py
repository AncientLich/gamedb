import gamedb.itms


class ItemNotFoundError(Exception):
    def __init__(self, table, value):
        self.table = table
        self.value = value
    
    def __str__(self):
        return 'Cannot find {} "{}"'.format(self.table, self.value)



class ItemExistsError(Exception):
    def __init__(self, item):
        self.item = item
        val = getattr(item, 'name', None)
        if val is None:
            val = getattr(item, 'title', None)
        self.emsg = '{} "{}" already exists.'.format(item.tablename, val)
    
    def __str__(self):
        return self.emsg

