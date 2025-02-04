import re
from typing import Optional, Tuple

def split_pos(pat:re.Pattern, src:str) -> Optional[Tuple[str,str,str]]:
    m = pat.search(src)
    if m is None:
        return None

    head_span = m.span()
    return (src[0:head_span[0]], #the string before pat
            m.group(1),          #the string that matches pat
            src[head_span[1]:])  #the string after pat