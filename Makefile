PYTHON ?= python3

.PHONY: test-structure

test-structure:
	$(PYTHON) scripts/check_control_plane.py
	$(PYTHON) -m pytest tests/structure -q
