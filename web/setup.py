from setuptools import setup

setup(
    name='Ferret Web',
    version='0.1',
    long_description=__doc__,
    packages=['web'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask>=0.10',
        'Flask-Bootstrap>=3.1.1.2',
        'Flask-OAuth>=0.12',
        'Flask-SQLAlchemy>=1.0',
        'rauth>=0.7.0']
)
