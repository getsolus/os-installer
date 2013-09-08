from setuptools import setup
            
setup(name         = 'os-installer',
      version      = '1.0',
      author       = "Ikey Doherty",
      author_email = "ikey@solusos.com",
      license      = "GPLv2+",
      packages     = ['os_installer', 'os_installer.pages', 'os_installer.widgets'],
      scripts      = ['os-installer-gtk'],
)
