@rem Requires:
@rem pip install build
@echo observable_properties: build for distribution
@echo ---------------------------------
@echo Running build frontend:
del dist\*.gz
del dist\*.whl
python -m build
@echo Install in editable mode:
pip install -e .
