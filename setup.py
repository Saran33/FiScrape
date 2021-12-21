from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
	
setup(
    name='FiScrape',
    packages=find_packages(include=['tutorial']),
    version='0.1.61803398',
	author='Saran Connolly',
    description='Financial news scraping and processing.',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/Saran33/FiScrape",
    project_urls={
        "Bug Tracker": "https://github.com/Saran33/FiScrape/issues",
    },
	classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
	install_requires = [
        'pandas','numpy', 'pytz', 'Scrapy>=2.5', 'SQLAlchemy>=1.4.25',
        'scrapy_splash @ git+https://github.com/Saran33/scrapy-splash.git',
        'grequests', 'beautifulsoup4', 'python-dateutil', 'pytz', 'tzlocal',
        'scrapyrt', 'cookiecutter', 'autopep8', 'pylint','tkmacosx',
],
	#package_dir={"": "src"},
    #packages=find_packages(where="FiScrape"),
    python_requires=">=3.8",
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
