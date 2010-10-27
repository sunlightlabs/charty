
from distutils.core import setup

setup(
    name='Charty',
    version='0.1.0',
    author='Kaitlin Lee',
    author_email='klee@sunlightfoundation.com',
    packages=['charty', 'charty.utils'],
    url='http://github.com:sunlightlabs/Charty/',
    license='LICENSE.txt',
    description='Another Python SVG Chart Generator that uses CSS smartly',
    long_description=open('README').read(),
)

