@echo appstrings: deploying to test.pypi.org
@echo ---------------------------------
twine check dist/*
twine upload -r testpypi dist/*
