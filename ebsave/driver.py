"""
ebsave.driver
driver
"""

# project imports
from .cli import parse_cmdline
from .log import setup_logging, LOGGER
from .constants import PROGRAM_NAME
from .metadata import get_instance_id
from .ec2 import get_client, get_volume_ids, delete_snapshots, create_snapshots


def run(argv):
    args = parse_cmdline(argv)
    setup_logging(args.logfile, args.loglevel)
    try:
        LOGGER.debug("starting %s", PROGRAM_NAME)
        _start(args)
    except Exception as e:
        LOGGER.exception(e)
        return 1
    finally:
        LOGGER.debug("finished %s", PROGRAM_NAME)
    return 0


def _start(args):
    if args.instance_id is None:
        instance_id = get_instance_id()
    else:
        instance_id = args.instance_id
    ec2 = get_client(args.region)
    volume_ids = get_volume_ids(ec2, instance_id, args.devices)
    if len(volume_ids) == 0:
        LOGGER.info("no volumes to backup")
        return
    create_snapshots(ec2, args.hostname, volume_ids, args.dryrun)
    delete_snapshots(ec2, volume_ids, args.retention, args.min_count,
                     args.dryrun)
