import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ArticutAPI_Taigi",
    version="0.9",
    author="Droidtown Linguistic Tech. Co. Ltd.",
    author_email="info@droidtown.co",
    description="Articut NLP system provides not only finest results on Chinese word segmentaion (CWS), Part-of-Speech tagging (POS) and Named Entity Recogintion tagging (NER), but also the fastest online API service in the NLP industry.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Droidtown/ArticutAPI_Taigi",
    project_urls={
        "Documentation": "https://api.droidtown.co/ArticutAPI/document/",
        "Source": "https://github.com/Droidtown/ArticutAPI",
    },
    license="MIT License",
    keywords=[
        "NLP", "NLU", "CWS", "POS", "NER", "AI",
        "artificial intelligence",
        "Chinese word segmentation",
        "computational linguistics",
        "language",
        "linguistics",
        "graphQL",
        "natural language",
        "natural language processing",
        "natural language understanding",
        "parsing",
        "part-of-speech-embdding",
        "part-of-speech-tagger",
        "pos-tagger",
        "pos-tagging",
        "syntax",
        "tagging",
        "text analytics"
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["requests >= 2.25.1", "ArticutAPI"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        #"Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: Customer Service",
        "Intended Audience :: Information Technology",
        "Natural Language :: Chinese (Traditional)",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Text Processing :: Markup :: XML",
        "Topic :: Text Processing :: Filters",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6.1",
)
