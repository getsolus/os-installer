from setuptools import setup

setup(
    name="os-installer",
    version="16.0",
    author="Solus",
    author_email="copyright@getsol.us",
    description="Operating System Installer",
    license="GPL-2.0",
    url="https://github.com/getsolus/os-installer",
    packages=['os_installer2', 'os_installer2.pages'],
    scripts=['os-installer-gtk'],
    classifiers=["License :: OSI Approved :: GPL-2.0 License"],
    package_data={'os_installer2': ['data/*.png', 'data/*.svg', 'data/*.css']},
)
