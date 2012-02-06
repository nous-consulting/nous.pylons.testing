from setuptools import setup, find_packages

setup(
    name='nous.pylons.testing',
    version='0.4.7',
    description='Nous testing utils.',
    author='Ignas Mikalajunas',
    author_email='ignas@nous.lt',
    url='http://github.com/Ignas/nous.pylons.testing/',
    classifiers=["Development Status :: 3 - Alpha",
                 "Environment :: Web Environment",
                 "Topic :: Communications :: Email",
                 "Intended Audience :: Developers",
                 "License :: OSI Approved :: GNU General Public License (GPL)",
                 "Programming Language :: Python"],
    install_requires=[
        'setuptools'],
    package_dir={'': 'src'},
    packages=find_packages('src'),
    namespace_packages=['nous', 'nous.pylons'],
    include_package_data=True,
    zip_safe=False,
    license="GPL"
)
