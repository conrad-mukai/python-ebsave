"""
backup_ebs
Entry point for module.
"""

# system imports
import sys

# project imports
from .driver import run


def main(argv=sys.argv):
    try:
        return run(argv)
    except SystemExit as e:
        return e
    except Exception as e:
        print("[error]: {}".format(e))
        return 1
