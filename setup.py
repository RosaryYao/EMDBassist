from setuptools import setup, find_packages

setup(
    name='EMDBassist',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='Apache',
    author='Rosary Yao, Paul K Korir',
    author_email='rosary@ebi.ac.uk, pkorir@ebi.ac.uk',
    description='Transform subtomogram average data to generic format',
    install_requires=['numpy', 'mrcfile'],
    entry_points={
        'console_scripts': [
            # todo: more concise names required
            'tra=new_main.core_modules:main',
        ],
    }
)
