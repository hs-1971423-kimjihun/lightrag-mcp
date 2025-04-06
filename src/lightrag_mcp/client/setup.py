import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="light-rag-server-api-client",
    version="1.2.8",
    description="A client library for accessing LightRAG Server API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.9, <4",
    install_requires=["httpx >= 0.20.0, < 0.29.0", "attrs >= 22.2.0", "python-dateutil >= 2.8.0, < 3"],
    package_data={"light_rag_server_api_client": ["py.typed"]},
)
