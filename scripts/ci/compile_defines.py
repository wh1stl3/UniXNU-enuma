"""Validate both joined and Clang -MJ split preprocessor options strictly."""
def require_define(arguments, name, expected):
    definitions=[];undefinitions=[];i=0
    while i<len(arguments):
        arg=arguments[i];op=None;value=None
        if arg in ('-D','-U'):
            if i+1>=len(arguments):raise ValueError('Truncated preprocessor option')
            op=arg;value=arguments[i+1];i+=1
        elif arg.startswith(('-D','-U')):
            op=arg[:2];value=arg[2:]
        if op:
            key,sep,definition=value.partition('=')
            if key==name:
                if op=='-U':undefinitions.append(value)
                else:definitions.append(definition if sep else '1')
        i+=1
    if not definitions or undefinitions or any(v!=str(expected) for v in definitions):
        raise ValueError(f'Wrong compilation macro {name}: definitions={definitions}, undefinitions={undefinitions}')
    return definitions
