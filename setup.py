from setuptools import setup

setup(
    name='web500',
    version='0.1',
    long_description=__doc__,
    packages=['web500'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
        'tornado',
        'datadiff',
        'schema',
        'libsass >= 0.6.0'
    ],
    sass_manifests={
        'web500': ('scss', 'static/css', '/static/css')
    }
)
