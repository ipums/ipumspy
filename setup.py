from pathlib import Path
from typing import List

from setuptools import setup, find_packages


here = Path(__file__).parent.absolute()


with open(here / "README.md", encoding="utf-8") as f:
    long_description = f.read()


def read_requirements(requirements_file: str) -> List[str]:
    requirements = []
    with open(requirements_file, "rt") as infile:
        for line in infile:
            line = line.strip()
            if line.startswith("#") or not line:
                continue
            requirements.append(line)
    return requirements


setup(
    name="ipumspy",
    version="0.0.1",
    description="A collection of tools for working with IPUMS data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/thepolicylab/ipumspy",
    author="Kevin Wilson",
    author_email="kevin_wilson@brown.edu",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: GPLv3",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    keywords="ipums",
    packages=find_packages(),
    python_requires=">=3.6, <4",
    install_requires=read_requirements("requirements.txt"),
    entry_points={"console_scripts": ["ipums=ipumspy.cli:cli"],},  # Optional
    project_urls={
        "Bug Reports": "https://github.com/thepolicylab/ipumspy/issues",
        "Source": "https://github.com/thepolicylab/ipumspy",
    },
)
