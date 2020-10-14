from setuptools import setup


setup(
    name='fuo_ytmusic',
    version='0.1.0',
    packages=['fuo_ytmusic'],
    url='https://github.com/BruceZhang1993/feeluown-ytmusic',
    license='GPL',
    author='BruceZhang1993',
    author_email='zttt183525594@gmail.com',
    description='Youtube music provider for FeelUOwn music player',
    keywords=['feeluown', 'plugin', 'youtube'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3 :: Only',
    ],
    install_requires=[
        'feeluown>=3.4',
        'requests',
        'pydantic',
        'ytmusicapi'
    ],
    entry_points={
        'fuo.plugins_v1': [
            'ytmusic = fuo_ytmusic',
        ]
    },
)
