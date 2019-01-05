"""
ebsave packaging
"""

# system imports
from setuptools import setup


# packaging
setup(name='ebsave',
      version='0.2.0',
      author='Conrad Mukai',
      author_email='conrad@mukai-home.net',
      url='https://github.com/conrad-mukai/python-ebsave',
      packages=['ebsave'],
      install_requires=[
          'boto3',
          'requests',
          'urllib3<=1.23;python_version<="2.7.6"'
      ],
      entry_points={'console_scripts': ['ebsave=ebsave:main']},
      zip_safe=False
)
