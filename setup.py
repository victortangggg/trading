from setuptools import find_packages, setup

setup(
    name='libs',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'marketdata=libs.marketdata:main',
            'pnl=libs.pnl:main'
        ],
    },
)