from setuptools import setup

setup(
    name            = "os-installer",
    version         = "12.5",
    author          = "Ikey Doherty",
    author_email    = "ikey@solus-project.com",
    description     = ("Operating System Installer"),
    license         = "GPL-2.0",
    url             = "https://github.com/solus-project/os-installer",
    packages        = ['os_installer2', 'os_installer2.pages'],
    scripts         = ['os-installer-gtk'],
    classifiers     = [ "License :: OSI Approved :: GPL-2.0 License"],
    package_data    = {'os_installer2': ['data/*.png', 'data/*.svg']},
)
