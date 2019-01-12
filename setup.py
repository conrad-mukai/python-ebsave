"""
ebsave packaging
"""

# system imports
from setuptools import setup


# packaging
setup(name='ebsave',
      version='0.2.2',
      author='Conrad Mukai',
      author_email='conrad@mukai-home.net',
      url='https://github.com/conrad-mukai/python-ebsave',
      packages=['ebsave'],
      install_requires=[
          'boto3',
          'requests'
      ],
      entry_points={'console_scripts': ['ebsave=ebsave:main']},
      zip_safe=False
)
