# Backup EBS

Script to backup EBS volumes attached to an EC2 instance.

## Description

This script manages snapshots of one or more EBS volumes attached to a specific
EC2 instance. It not only creates snapshots, but deletes those that are older
than a prescribed retention policy. The primary use case for this script is to
run as a cronjob on an AWS instance. Used this way it will back up volumes that
are attached to the instance on which the script is running on a regular basis.
The script can also be run off-instance, such as from another AWS instance or a
remote workstation with access privileges to the AWS account.

## Command Line Syntax

The command line syntax for the script is as follows:
    
    usage: backup-ebs [-h] [-l LOGFILE] [-L LOGLEVEL] [-R REGION] [-r RETENTION]
                      [-m MIN_COUNT] [-i INSTANCE_ID] [-H HOSTNAME]
                      [-s [SKIP [SKIP ...]]] [-d]
    
    backup EBS volumes
    
    optional arguments:
      -h, --help            show this help message and exit
      -l LOGFILE, --logfile LOGFILE
                            path to logfile (default is stdout)
      -L LOGLEVEL, --loglevel LOGLEVEL
                            log level [DEBUG,INFO,WARNING,ERROR,CRITICAL] (default
                            is INFO)
      -R REGION, --region REGION
                            region to search for instance (default is to use the
                            region in the local configuration: ~/.aws/config or
                            the AWS_DEFAULT_REGION environment variable;
                            otherwise, if the script is running on an AWS instance
                            use the region in which it is located)
      -r RETENTION, --retention RETENTION
                            retention period in days (default is 7)
      -m MIN_COUNT, --min-count MIN_COUNT
                            minimum number of snapshots per volume to retain
                            regardless of age (default is 5)
      -i INSTANCE_ID, --instance-id INSTANCE_ID
                            ID for instance to which volumes are attached (default
                            is instance on which script is being run)
      -H HOSTNAME, --hostname HOSTNAME
                            name to tag snapshots with (default is the system
                            hostname)
      -s [SKIP [SKIP ...]], --skip [SKIP [SKIP ...]]
                            devices to skip (e.g., /dev/xvda - default is to not
                            skip any)
      -d, --dryrun          flag to enable dry run mode

## Use Cases

The following sections describe common use cases.

### Run on Instance Being Backed Up

If the script is run on an AWS instance with no options and with no local AWS
configuration (i.e., `~/.aws/config` or `AWS*` environment variables), then it will
determine the region and instance ID from
[instance metadata](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-instance-metadata.html)
and proceed to manage snapshots for all volumes attached to the device. The
hostname used to tag snapshots will be taken from the local OS. If you don't
want to create snapshots for specific volumes then use the `--skip` option. An
example this is:

    backup-ebs -s /dev/xvda

### Run on Remote Instance

If the script is used to backup volumes on remote AWS instances the
`--instance-id` and `--hostname` options should be used. If there is no local
AWS configuration then the instance upon which the script is running should be
in the same region as the instances being backed up to take advantage of the
instance metadata. Otherwise, use the `--region` option to specify the region
in which the backed up instance resides. An example of this is:

    backup-ebs -H jenkins-master -i i-0ce03cbe16e0a87e1 -r us-west-2 -s /dev/xvda

### Run on Workstation

If the script is run on a workstation, then it should be configured with access
to an AWS account. In that case you must specify the `--instance-id` and
`--hostname` options. The region is part of your local configuration so it does
not have to be specified. An example of this is:

    backup-ebs -H jenkins-master -i i-0ce03cbe16e0a87e1 -s /dev/xvda

## Retention Policy

The `--retention` and `--min-count` options control the retention policy. At
least `min-count` snapshots per volume will be retained regardless of age. Once
the number of snapshots per volume exceeds `min-count` then any snapshots older
than `retention` days will be deleted.

## IAM Permissions

The principal running the script needs to be granted something like the
following IAM policy:

    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "backup",
                "Effect": "Allow",
                "Action": [
                    "ec2:DescribeVolumes",
                    "ec2:DescribeSnapshots",
                    "ec2:DeleteSnapshot",
                    "ec2:CreateTags",
                    "ec2:CreateSnapshot"
                ],
                "Resource": "*"
            }
        ]
    }

Running with the `dryrun` option enabled will check if the script can perform
the desired operations.
