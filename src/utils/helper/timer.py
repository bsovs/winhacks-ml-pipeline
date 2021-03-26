import logging
import time
from typing import Optional

from src.utils.helper.print_colors import pcolors

'''
    Used to time and log total run time of a function
'''


def time_execute(func, case: Optional[str] = None):
    tic = time.perf_counter()
    output = func()
    toc = time.perf_counter()
    if case is not None:
        _str = str(f" {pcolors.OKGREEN}({case}){pcolors.ENDC}")
    else:
        _str = ""
    logging.info(f"Delta Time{_str}: {pcolors.OKBLUE}{toc - tic:0.4f}{pcolors.ENDC} sec")
    return output
