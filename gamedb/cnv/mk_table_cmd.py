import attr
import gamedb.items
import gamedb.cnv.internal


'''
This file contains the definition for mk_table_cmd(cls, params)
all other functions are private routines used by mk_table_cmd itself
'''



# convert a type (int, str, boolean or class) to a string wich represent db
# type
def _type_to_string(xtype):
    if xtype is int or xtype is bool:
        return 'INTEGER'
    else:
        return 'TEXT'



# get FOREIGN KEY references for relation items (GameTag, GameSplat)
# 1) get references that will make the primary key (keyclasses)
def _rel_get_reference1(keyclasses):
    value = ''
    for k in keyclasses:
        value += ', FOREIGN KEY({}id) REFERENCES {}(ID)'.format(
            k.tablename, k.tablename)
    return value



# get FOREIGN KEY references for relation items (GameTag, GameSplat)
# 2) get other references (check if attr_name appears in a relation rule)
def _rel_get_reference2(attr_name, rule):
    value = ''
    if attr_name in rule and hasattr(rule[attr_name], 'tablename'):
        value = ', FOREIGN KEY({}id) REFERENCES {}(ID)'.format(
            rule[attr_name].tablename, rule[attr_name].tablename)
    return value



# get the final PRIMARY KEY command for relation items (GameTag, GameSplat)
def _rel_primarykey(keyclasses):
    value = ', PRIMARY KEY('
    value += ', '.join(['{}id'.format(k.tablename) for k in keyclasses])
    value += ')'
    return value



# when a class has one or more composite attributes, than this routine is
# invoked by mk_table_cmd instead of default listcomp (see mk_table_cmd)
#
# when attribute is a composite attribute (cls.composite[att_name] exists)
# then the table definition is kept from 'def' key
# 
# example: cls.composite['expire'] for attribute expire will be a dictionary
# wich will contain the 'def' key.
# composite = cls.composite['expire']
# composite['def'] = 'd INTEGER, m INTEGER, y INTEGER'
def _cls_params(cls, attributes, params_org):
    if isinstance(params_org, tuple):
        keyclasses, params = params_org
    else:
        params = params_org
    value = []
    references = {}
    for at_name, at_type in attributes:
        if not hasattr(cls, 'composite') or at_name not in cls.composite:
            if at_type in gamedb.items.rules():
                value.append('{}id INTEGER'.format(at_name))
                references[at_name] = (
                    'FOREIGN KEY({}id) REFERENCES {}(ID)'.format(
                        at_name, at_type.tablename
                    )
                )
            else:
                value.append('{} {}{}'.format(
                    at_name, _type_to_string(at_type),
                    ' PRIMARY KEY AUTOINCREMENT' if at_name == 'ID' else '')
                )
        else:
            composite = cls.composite[at_name]
            value.append(composite['def'])
    value = ', '.join(value)
    return (value, references)



def mk_table_cmd(cls, params):
    '''
    mk_table_cmd(cls, params)
    
    mk_table_cmd is a function that returns a string: the SQL command to make a 
    table.
    
    @cls: item (or relation) class type
    @params: set of rule (kept from gamedb.items.rules()) of that item class
    '''
    
    is_relation = True if isinstance(params, (tuple, list)) else False
    attributes = [(at.name, gamedb.cnv.internal.checkargtype(at))
                  for at in attr.fields(cls)]
    value = 'CREATE TABLE IF NOT EXISTS {}\n('.format(cls.tablename)
    tmp_val, references = _cls_params(cls, attributes, params)
    value += tmp_val
    if is_relation:
        value += _rel_get_reference1(params[0])
    for attr_name, attr_type in attributes:
        if attr_name in references:
            value += ', ' + references[attr_name]
        elif attr_type is int and attr_name.endswith('id') and is_relation:
            value += _rel_get_reference2(attr_name, params[1])
    if is_relation:
        value += _rel_primarykey(params[0])
    value += ')'
    return value