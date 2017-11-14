from setuptools import setup

APP = ['twitter_to_cms.py']
DATA_FILES = []
PACKAGES = ['certifi']
OPTIONS = {'argv_emulation': True,
           'site_packages': True,
           'packages': PACKAGES,
           'arch': 'universal',
           'plist': {'CFBundleName': 'TwitterToCms',
                     'CFBundleShortVersionString': '1.0.0',
                     'CFBundleVersion': '1.0.0',
                     'CFBundleIdentifier': 'com.github.nahratzah.twitter_to_cms',
                     'NSHumanReadableCopyright': 'BSD 2-clause',
                     'CFBundleDevelopmentRegion': 'English'
                    }
          }

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
