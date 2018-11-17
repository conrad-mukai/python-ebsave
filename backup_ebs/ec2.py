"""
backup_ebs.ec2
AWS EC2 API calls.
"""

# system imports
from datetime import datetime, timezone, timedelta
import collections
import copy
import socket

# project imports
from .metadata import get_region
from .log import LOGGER
from .constants import PROGRAM_NAME

# 3rd party imports
import boto3
import botocore
import pytz

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


def get_volume_ids(ec2, instance_id, skip):
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
            if a['Device'] not in skip}


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
        if not dryrun:
            ec2.delete_snapshot(SnapshotId=snapshot_id)


def _filter_snapshots_to_delete(response, retention, min_count):
    snapshot_ids = collections.defaultdict(list)
    for snapshot in response['Snapshots']:
        snapshot_ids[snapshot['VolumeId']].append((snapshot['SnapshotId'],
                                                   snapshot['StartTime']))
    old_snapshots = []
    initial_newest_snapshots \
        = [(None, pytz.utc.localize(datetime.min))] * min_count
    indices = list(range(min_count))
    t = datetime.now(timezone.utc)
    max_age = timedelta(days=retention)
    old_snapshot_count = 0
    for volume_id, snapshots in snapshot_ids.items():
        if len(snapshots) <= min_count:
            LOGGER.debug("retaining all snapshots for {}: number of snapshots "
                         "is less than {}".format(volume_id, min_count))
            continue
        newest_snapshots = copy.copy(initial_newest_snapshots)
        for snapshot in snapshots:
            append_to_old = True
            for i in indices:
                if snapshot[1] > newest_snapshots[i][1]:
                    append_to_old = False
                    kth_snapshot = newest_snapshots[-1]
                    for j in range(min_count-1, i, -1):
                        newest_snapshots[j] = newest_snapshots[j-1]
                    newest_snapshots[i] = snapshot
                    if kth_snapshot[0] is not None \
                       and t - kth_snapshot[1] > max_age:
                        old_snapshots.append(kth_snapshot[0])
                    break
            if append_to_old and t - snapshot[1] > max_age:
                old_snapshots.append(snapshot[0])
        next_old_snapshot_count = len(old_snapshots)
        if next_old_snapshot_count > old_snapshot_count:
            LOGGER.debug("deleting {} snapshots for {}"
                         .format(next_old_snapshot_count-old_snapshot_count,
                                 volume_id))
            old_snapshot_count = next_old_snapshot_count
        else:
            LOGGER.debug("retaining all snapshots for {}: no snapshot older "
                         "than {} days".format(volume_id, retention))
    return old_snapshots


def create_snapshots(ec2, hostname, volume_ids, dryrun):
    hostname = _get_hostname(hostname)
    for volume_id, device in volume_ids.items():
        tag = "{}:{}:{}".format(hostname, device,
                                datetime.utcnow().strftime(_TIMESTAMP_FORMAT))
        LOGGER.info("creating snapshot {} for {}".format(tag, volume_id))
        if not dryrun:
            ec2.create_snapshot(
                Description="snapshot created by {}".format(PROGRAM_NAME),
                VolumeId=volume_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'snapshot',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': tag
                            }
                        ]
                    }
                ]
            )


def _get_hostname(hostname):
    if hostname is None:
        return socket.gethostname().split('.')[0]
    else:
        return hostname
