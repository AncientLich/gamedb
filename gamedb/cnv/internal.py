import attr
    

def checkargtype(arg):
    if hasattr(type(arg), 'validator'):
        if arg.validator is not None:
            return checkargtype(arg.validator)
        elif arg.type is not None:
            return arg.type
        elif arg.converter is not None:
            return arg.converter
        else:
            return str
    else:
        return arg.type
