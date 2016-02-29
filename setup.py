from setuptools import setup
            
setup(name         = 'os-installer',
      version      = '5.4',
      author       = "Ikey Doherty",
      author_email = "ikey@solus-project.com.com",
      license      = "GPL-2.0",
      packages     = ['os_installer', 'os_installer.pages', 'os_installer.widgets'],
      scripts      = ['os-installer-gtk'],
)
