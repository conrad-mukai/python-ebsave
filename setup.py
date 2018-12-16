"""
ebsave packaging
"""

# system imports
from setuptools import setup


# packaging
setup(name='ebsave',
      version='0.1.0',
      author='Conrad Mukai',
      author_email='cmukai@cisco.com',
      url='https://github.com/conrad-mukai/python-ebsave',
      packages=['ebsave'],
      install_requires=[
          'boto3',
          'requests'
      ],
      entry_points={'console_scripts': ['ebsave=ebsave:main']}
)
