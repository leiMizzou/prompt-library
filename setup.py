from setuptools import setup
setup(name="prompt-library",version="0.1.0",
    description="Reusable prompt templates for AI agents",
    long_description=open("README.md").read(),long_description_content_type="text/markdown",
    author="Lei Hua",url="https://github.com/leiMizzou/prompt-library",
    py_modules=["prompt_library"],python_requires=">=3.8",
    entry_points={"console_scripts":["prompt-library=prompt_library:main"]})
