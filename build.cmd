@echo observable_properties: build for distribution
@echo ---------------------------------
@echo Running build frontend:
python -m build
@echo Install in editable mode:
pip install -e .
