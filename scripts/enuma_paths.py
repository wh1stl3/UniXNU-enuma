"""Resolve enuma evidence paths after migration without rewriting evidence."""
from pathlib import Path


def evidence_path(value, root):
    root=Path(root).resolve()
    text=str(value).replace('\\','/').rstrip('/')
    # Exact enuma roots only. Never resolve nuwa or fall back to an old tree.
    prefixes=(root.as_posix(), 'D:/Code/PortingiOS/enuma/UniXNU-enuma',
              '/mnt/d/Code/PortingiOS/enuma/UniXNU-enuma',
              'D:/Code/UniXNU-enuma','/mnt/d/Code/UniXNU-enuma')
    for prefix in prefixes:
        if text.lower().startswith(prefix.lower()+'/'):
            text=text[len(prefix)+1:];break
    parts=text.split('/')
    if not parts or parts[0]!='out' or any(p in ('','..','.') or ':' in p for p in parts):
        raise ValueError('evidence path must refer to this enuma out/ tree')
    result=root.joinpath(*parts).resolve()
    result.relative_to(root/'out')
    return result
