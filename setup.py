from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()
	
setup(
    name='FiScrape',
    packages=find_packages(include=['tutorial']),
    version='0.1.1',
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
  #'pwe @ git+https://github.com/Saran33/pwe_analysis.git',
        'pandas','numpy', 'pytz', 'Scrapy>=1.7.3', 'SQLAlchemy>=1.3.6'
],
	#package_dir={"": "src"},
    #packages=find_packages(where="pwe"),
    python_requires=">=3.8",
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
