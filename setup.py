from setuptools import find_packages
from setuptools import setup

version = '2.4.0'

setup(name='helios-sdk',
      version=version,
      description='Use the Helios APIs in Python',
      author='Michael Bayer',
      author_email='mbayer@harris.com',
      url='https://github.com/harris-helios/helios-sdk-python',
      download_url='https://github.com/harris-helios/'
                   'helios-sdk-python/archive/{}.tar.gz'.format(version),
      license='MIT',
      install_requires=['requests>=2.0.0',
                        'numpy>=1.13.0',
                        'pandas>=0.21.0',
                        'Pillow>=5.0.0',
                        'python-dateutil>=2.7.0'],
      extras_require={
          'tests': ['pytest>=3.5.0'],
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
