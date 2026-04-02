from setuptools import setup, find_packages

setup(
    name="mystic-swarm-v2",
    version="2.0.0",
    packages=find_packages(),
    install_requires=["qdrant-client", "httpx", "pydantic"],
    python_requires=">=3.10",
)
