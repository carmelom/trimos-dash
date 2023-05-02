from setuptools import setup, find_packages

setup(name='rf_trap_mode_solver',
      version="0.9.0",
      description='A mode solver for RF ion traps',
      url='',
      author='Carmelo Mordini',
      author_email='cmordini@phys.ethz.ch',
      python_requires='>=3.8',
      install_requires=[
          'numpy',
          'scipy',
          'nptyping',
          'tabulate',
          'colorama'
      ],
      extras_require={},
      packages=find_packages())
