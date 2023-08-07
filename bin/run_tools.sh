python3 -m black .
python3 -m isort .
python3 -m mypy .
python3 -m pylint $(git ls-files '*.py')
