import os

requirements_file = os.path.join(os.path.dirname(__file__), 'REQUIREMENTS.txt')
with open(requirements_file) as f:
    required = f.read().splitlines()

from distutils.core import setup

setup(
    name = "Friday",
    description = "An open source, extensible virtual assistant",
    version = "0.3.1",
    url = "https://github.com/Zenohm/Friday",
    long_description = """An open-source virtual assistant who got her name from an old project of one Tony Stark.""",
    license = "MIT",
    keywords = ['assistant', 'ai', 'api.ai',
                'plugin', 'plugins', 'friday',
                'virtual assistant', 'open source'],
    maintainer = "Isaac Smith (Zenohm)",
    maintainer_email = "sentherus@gmail.com",
    author = "Isaac Smith (Zenohm)",
    author_email = "sentherus@gmail.com",
    classifiers = [
	'Development Status :: 3 - Alpha',
	'Environment :: Console',
	'Natural Language :: English',
	'Intended Audience :: Other Audience',
	'Intended Audience :: Education',
	'Intended Audience :: Developers',
	'Intended Audience :: Science/Research',
	'License :: OSI Approved :: MIT License',
	'Operating System :: Microsoft :: Windows',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3 :: Only',
	'Programming Language :: Python :: 3.3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
	'Programming Language :: Python :: 3.6',
	'Topic :: Office/Business',
	'Topic :: Home Automation',
	'Topic :: Internet',
	'Topic :: Scientific/Engineering',
	'Topic :: Scientific/Engineering :: Human Machine Interfaces',
	'Topic :: Multimedia :: Sound/Audio :: Speech',
    ],
    packages = ['friday'],
    install_requires=required,
)
