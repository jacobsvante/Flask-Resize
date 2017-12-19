#!/bin/bash
trap 'exit' ERR

lint () {
    flake8 flask_resize tests\
    && (isort --recursive --check-only flask_resize tests \
        || (isort --recursive --diff flask_resize tests && false)\
    )
}


pytest_prep () {
    echo -n 'Prepping pytest... '
    # Pytest complains about invalid import paths if we don't delete .pyc files
    find tests -name "*.pyc" -exec rm -f {} \; &&\
    echo 'Done!'
}


pytest_run_default () {
    coverage run --source=flask_resize -m py.test && coverage report
}


if [[ "$1" = 'lint' ]]; then
    lint
elif [[ "$1" = 'test' ]]; then
    pytest_prep
    pytest_run_default
elif [[ "$1" = 'pytest' ]]; then
    pytest_prep
    exec "$@"
else
    exec "$@"
fi
