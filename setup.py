"""
ebsave packaging
"""

# system imports
import platform
from setuptools import setup

if tuple(int(x) for x in platform.python_version().split('.')) <= (2, 7, 6):
    urllib3_spec = 'urllib3<=1.23'
else:
    urllib3_spec = 'urllib3'


# packaging
setup(name='ebsave',
      version='0.2.2',
      author='Conrad Mukai',
      author_email='conrad@mukai-home.net',
      url='https://github.com/conrad-mukai/python-ebsave',
      packages=['ebsave'],
      install_requires=[
          'boto3',
          'requests',
          urllib3_spec
      ],
      entry_points={'console_scripts': ['ebsave=ebsave:main']},
      zip_safe=False
)
