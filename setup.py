from setuptools import find_packages
from setuptools import setup

version = '3.0.1'

setup(name='helios-sdk',
      version=version,
      description='Use the Helios APIs in Python',
      author='Michael Bayer',
      author_email='jonathan.cochrane@nv5.com',
      url='https://github.com/helios-earth/helios-sdk-python',
      download_url='https://github.com/helios-earth/'
                   'helios-sdk-python/archive/{}.tar.gz'.format(version),
      license='MIT',
      install_requires=['requests>=2.0.0',
                        'numpy>=1.13.0',
                        'Pillow>=5.0.0',
                        'python-dateutil>=2.7.0'],
      extras_require={
          'tests': ['pytest>=3.5.0'],
      },
      python_requires='>=3.6',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.6',
          'Topic :: Software Development :: Libraries',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages())
