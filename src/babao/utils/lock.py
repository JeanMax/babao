"""Some utils functions for lock file handling"""

import os


def isLocked(lockfile):
    """TODO"""

    return os.path.isfile(lockfile)


def tryLock(lockfile):
    """TODO"""

    if isLocked(lockfile):
        return False

    open(lockfile, "w")
    return True


def tryUnlock(lockfile):
    """TODO"""

    if not isLocked(lockfile):
        return False

    os.remove(lockfile)
    return True
