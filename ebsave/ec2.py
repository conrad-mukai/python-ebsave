"""
ebsave.ec2
AWS EC2 API calls
"""

# system imports
from datetime import datetime, timezone, timedelta
import collections
import heapq
import socket

# project imports
from .metadata import get_region
from .log import LOGGER
from .constants import PROGRAM_NAME

# 3rd party imports
import boto3
import botocore

# constants
_TIMESTAMP_FORMAT = '%Y%m%dT%H%M%S'


def get_client(region):
    if region is None:
        try:    # first try with the local configuration
            return boto3.client('ec2')
        except botocore.exceptions.NoRegionError: # now try with metadata
            LOGGER.debug("no region configured, trying instance metadata")
            return boto3.client('ec2', region_name=get_region())
    else:
        return boto3.client('ec2', region_name=region)


def get_volume_ids(ec2, instance_id, devices):
    LOGGER.debug("getting volume IDs for %s", instance_id)
    response = ec2.describe_volumes(
        Filters=[
            {
                'Name': 'attachment.instance-id',
                'Values': [
                    instance_id
                ]
            }
        ]
    )
    return {a['VolumeId']: a['Device']
            for v in response['Volumes']
            for a in v['Attachments']
            if len(devices) == 0 or a['Device'] in devices}


def create_snapshots(ec2, hostname, volume_ids, dryrun):
    hostname = _get_hostname(hostname)
    description = "snapshot created by {}".format(PROGRAM_NAME)
    for volume_id, device in volume_ids.items():
        tag = "{}:{}:{}".format(hostname, device,
                                datetime.utcnow().strftime(_TIMESTAMP_FORMAT))
        LOGGER.info("creating snapshot %s for %s", tag, volume_id)
        _create_snapshot(ec2, dryrun, tag, Description=description,
                         VolumeId=volume_id)


def delete_snapshots(ec2, volume_ids, retention, min_count, dryrun):
    LOGGER.debug("searching for old snapshots from volume(s) %s to delete",
                 ",".join(volume_ids))
    response = ec2.describe_snapshots(
        Filters=[
            {
                'Name': 'volume-id',
                'Values': list(volume_ids.keys())
            }
        ]
    )
    old_snapshots = _filter_snapshots_to_delete(response, retention, min_count)
    for snapshot_id in old_snapshots:
        LOGGER.info("deleting snapshot %s", snapshot_id)
        _delete_snapshot(ec2, dryrun, snapshot_id, SnapshotId=snapshot_id)


def _filter_snapshots_to_delete(response, retention, min_count):
    snapshot_ids = collections.defaultdict(list)
    for snapshot in response['Snapshots']:
        snapshot_ids[snapshot['VolumeId']].append((snapshot['SnapshotId'],
                                                   snapshot['StartTime']))
    old_snapshots = []
    t = datetime.now(timezone.utc)
    max_age = timedelta(days=retention)
    old_snapshot_count = 0
    for volume_id, snapshots in snapshot_ids.items():
        if len(snapshots) <= min_count:
            LOGGER.debug("retaining all snapshots for %s: number of snapshots "
                         "is less than or equal to %d", volume_id, min_count)
            continue
        newest_snapshots = set(heapq.nlargest(min_count, snapshots,
                                              key=lambda x: x[1]))
        old_snapshots += [s[0] for s in snapshots
                          if s not in newest_snapshots and t - s[1] > max_age]
        next_old_snapshot_count = len(old_snapshots)
        if next_old_snapshot_count > old_snapshot_count:
            LOGGER.debug("found %d snapshot(s) for %s to delete",
                         next_old_snapshot_count-old_snapshot_count,
                         volume_id)
            old_snapshot_count = next_old_snapshot_count
        else:
            LOGGER.debug("retaining all snapshots for %s: no snapshot older "
                         "than %d days", volume_id, retention)
    return old_snapshots


def _dryrun(action):
    def wrapper(f):
        def inner(ec2, dryrun, snapshot, **kwargs):
            try:
                return f(ec2, dryrun, snapshot, **kwargs)
            except botocore.exceptions.ClientError as e:
                if dryrun:
                    if 'DryRunOperation' in str(e):
                        LOGGER.info("you have permission to %s snapshot %s",
                                    action, snapshot)
                    else:
                        LOGGER.error("you don't have permission to %s "
                                     "snapshot %s", action, snapshot)
                else:
                    raise e
        return inner
    return wrapper


def _get_hostname(hostname):
    if hostname is None:
        return socket.gethostname().split('.')[0]
    else:
        return hostname


@_dryrun('create')
def _create_snapshot(ec2, dryrun, snapshot, **kwargs):
    response = ec2.create_snapshot(DryRun=dryrun, **kwargs)
    ec2.create_tags(DryRun=dryrun,
                    Resources=[response['SnapshotId']],
                    Tags=[
                        {
                            'Key': 'Name',
                            'Value': snapshot
                        }
                    ])
    return response


@_dryrun('delete')
def _delete_snapshot(ec2, dryrun, snapshot, **kwargs):
    return ec2.delete_snapshot(DryRun=dryrun, **kwargs)
