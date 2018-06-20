"""Some utils functions for lock file handling"""

import os


def isLocked(lockfile):
    """Check if the ´lockfile´ exists"""

    return os.path.isdir(lockfile)


def tryLock(lockfile):
    """
    Create the given ´lockfile´

    Return false if it already exists
    """

    if isLocked(lockfile):
        return False

    os.mkdir(lockfile)
    return True


def tryUnlock(lockfile):
    """
    Remove the given ´lockfile´

    Return false if it doesn't exist
    """

    if not isLocked(lockfile):
        return False

    os.rmdir(lockfile)
    return True
