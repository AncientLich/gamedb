import attr
import gamedb.items
import gamedb.cnv.internal


def _get_attr_columname(cls, attr_name, attr_type):
    if hasattr(cls, 'blobs') and attr_name in cls.blobs:
        return (attr_name,)
    elif hasattr(attr_type, 'tablename'):
        return '{}id'.format(attr_name)
    else:
        return attr_name



def get_item_struct(cls):
    attributes = [(at.name, gamedb.cnv.internal.checkargtype(at))
                  for at in attr.fields(cls)]
    struct = []
    for attr_name, attr_type in attributes:
        column_name = _get_attr_columname(cls, attr_name, attr_type)
        # when column name value is NOT a string, but a tuple containing
        # a string (tuple with only one value inside), then the attribute
        # was stored as BLOB in sqlite DB (type=None)
        if isinstance(column_name, tuple):
            name = column_name[0]
            struct.append(
                {'attr': name, 'column': name,
                 'aliased': '{}_{}'.format(cls.tablename, name),
                 'type': None})
        # usual case: _get_attr_columname returns a string
        else:
            struct.append(
                {'attr': attr_name, 'column': column_name,
                 'aliased': '{}_{}'.format(cls.tablename, column_name),
                 'type': attr_type})
    return struct

