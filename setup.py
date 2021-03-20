import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ascheck", # Replace with your own username
    version="0.0.3.1",
    author="Stijn Debackere",
    author_email="debackere@strw.leidenuniv.nl",
    description="A package to perform image analysis on archaeological tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/StijnDebackere/AScheck",
    install_requires=["opencv-python>=4.2.0",
                      "numpy",
                      "matplotlib>=2.0.0",
                      "scipy"],
    scripts=["ascheck"],
    package_dir={'': 'src'},
    packages=setuptools.find_packages(),
    python_requires='>=3.6',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)


