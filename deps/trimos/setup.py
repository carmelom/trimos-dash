from setuptools import setup, find_packages

setup(name='trimos',
      version="0.9.0",
      description='ThRee dImensional MOde Solver for trapped ions',
      url='',
      author='Carmelo Mordini',
      author_email='cmordini@phys.ethz.ch',
      python_requires='>=3.9',
      install_requires=[
          'numpy',
          'scipy',
          'nptyping',
          'tabulate',
          'colorama'
      ],
      extras_require={},
      packages=find_packages())
