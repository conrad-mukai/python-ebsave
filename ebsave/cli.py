"""
ebsave.cli
command line interface
"""

# system imports
import argparse

# project imports
from .log import LOG_LEVELS, DEFAULT_LOG_LEVEL
from .constants import DEFAULT_RETENTION_PERIOD, DEFAULT_MIN_COUNT


def parse_cmdline(argv):
    parser = argparse.ArgumentParser(description="backup EBS volumes")
    parser.add_argument('-l', '--logfile', default=None,
                        help="path to logfile (default is stdout)")
    parser.add_argument('-L', '--loglevel', choices=LOG_LEVELS,
                        default=DEFAULT_LOG_LEVEL, metavar='LOGLEVEL',
                        help="log level [{}] (default is {})"
                             .format(','.join(LOG_LEVELS),
                                     DEFAULT_LOG_LEVEL))
    parser.add_argument('-R', '--region',
                        help="region to search for instance (default is to "
                             "use the region in the local configuration: "
                             "~/.aws/config or the AWS_DEFAULT_REGION "
                             "environment variable; otherwise, if the script "
                             "is running on an AWS instance use the region in "
                             "which it is located)")
    parser.add_argument('-r', '--retention', type=int,
                        default=DEFAULT_RETENTION_PERIOD,
                        help="retention period in days (default is {})"
                             .format(DEFAULT_RETENTION_PERIOD))
    parser.add_argument('-m', '--min-count', type=int,
                        default=DEFAULT_MIN_COUNT,
                        help="minimum number of most recent snapshots per "
                             "volume to retain (default is {})"
                             .format(DEFAULT_MIN_COUNT))
    parser.add_argument('-i', '--instance-id',
                        help="ID for instance to which volumes are attached "
                             "(default is instance on which script is being "
                             "run)")
    parser.add_argument('-H', '--hostname',
                        help="name to tag snapshots with (default is the "
                             "system hostname)")
    parser.add_argument('-d', '--devices', nargs='*', default=[],
                        metavar='DEVICE',
                        help="devices to include (e.g., /dev/xvdf - default is "
                             "to include all devices)")
    parser.add_argument('-D', '--dryrun', action='store_true',
                        help="flag to enable dry run mode")
    return parser.parse_args(argv[1:])
