"""
backup_ebs packaging
"""

# system imports
from setuptools import setup


# packaging
setup(name='backup-ebs',
      version='0.1.1',
      author='Conrad Mukai',
      author_email='cmukai@cisco.com',
      url='https://gitlab.cmxcisco.com/cmx-devops-tools/python-backup-ebs',
      packages=['backup_ebs'],
      package_dirs={'backup_ebs': 'backup_ebs'},
      install_requires=[
          'boto3',
          'requests',
          'pytz'
      ],
      entry_points={'console_scripts': ['backup-ebs=backup_ebs:main']}
)
