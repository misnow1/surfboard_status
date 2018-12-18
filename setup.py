
from setuptools import setup, find_packages


setup(
    name='surfboard_status',
    version='0.1.0',
    python_requires='>3.6',
    package_dir={'': 'src'},
    packages=find_packages('src'),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'surfboard-status = surfboard_status.main:main'
        ]
    },
    install_requires=['requests', 'beautifulsoup4', 'click', 'lxml'],
    author='Michael Snow',
    author_email='sno.sno@gmail.com'
)
