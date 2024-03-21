@rem Requires:
@rem pip install twine
@echo observable_properties: deploying to test.pypi.org
@echo ---------------------------------
twine check dist/*
twine upload -r testpypi dist/*
