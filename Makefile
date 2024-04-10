.PHONY: precommit
precommit:
	pip install -r requirements-dev.txt && \
    pre-commit install -t pre-commit -t pre-push
