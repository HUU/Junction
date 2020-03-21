# Contributing to Junction

The following is a set of basic guidelines to help you be productive working in the Junction codebase.  This is a hobby project, I am not particular about who is contributing, and will accept any pull request that doesn't take the project in a totally random direction.

## Working on Issues

All of the work done on this project is tracked in GitHub issues (with bigger release efforts tracked in GitHub projects).  Start by looking there for things you can work on (or open an issue with your suggestions).

Once you have something you want to take on:

1. Comment in the issue that you are working on the problem (or have stopped, so others can take a look).
2. Submit a pull request, detailing the changes you made.
3. GitHub Actions will automatically verify your changes meet the [styleguides](#styleguides).
4. I will review and accept your PR as soon as possible.

Depending on the issue and the benefit it offers, I have no problem cutting an early release/hotfix so it can be picked up on PyPI.

## Ramping Up

I am happy to answer your questions and chat 1:1 if you are working on Junction.  [Contact details are on my GitHub profile](https://github.com/HUU).

An attempt is made to keep an overview of Junctions [architecture and design in the wiki](https://github.com/HUU/Junction/wiki).

## Development Environment

This project is attempting to use the latest (stable-ish) standards and practices emerging in the Python community.  This includes `pyproject.toml` (a single unified configuration file for the project and its various tools).  As of this writing, `pyproject.toml` is sparse, and so some exceptions are made (e.g. `mypy.ini`).

* [Poetry](https://python-poetry.org/) for dependency management, virtualenv creation, and packaging.
* [Black](https://black.readthedocs.io/en/stable/) for code formatting.
* [Flake8](https://flake8.pycqa.org/en/latest/) for PEP8 enforcement.
* [mypy](http://mypy-lang.org/) for static type checking.
* [tox](https://tox.readthedocs.io/en/latest/) for test execution.
* [pytest](https://docs.pytest.org/en/latest/) for unit testing.
* [pre-commit](https://pre-commit.com/) for automatically checking compliance with the above.
* [GitHub Actions](https://github.com/HUU/Junction/actions) for CI/CD.

#### Setup

1. [Install Poetry](https://python-poetry.org/docs/#installation).
2. Clone the repistory:
    ```sh
    git clone git@github.com:HUU/Junction.git
    ```
3. Setup the virtual environment:
    ```sh
    cd Junction
    poetry install
    ```
4. Activate the virtual environment:
    ```sh
    poetry shell
    ```
5. Setup pre-commit hooks:
    ```sh
    pre-commit install
    ```

With the above completed, you are now prepared to develop against Junction using your preferred tools.  Thanks to Poetry, you will also have access to the Junction CLI from within the virtual environment, and it will use the code in your cloned repository directly.

### Test Confluence Instance

You will need an instance of Confluence to test against.  Atlassian offers free instances of Confluence Cloud (liimited to 10 users).  [Sign-up here](https://www.atlassian.com/software/confluence/free).

## Styleguides

#### Git Commit Messages
* Use the present tense ("Fixes problem" not "Fixed problem")
* Try to limit the first line to 72 characters or less
* Reference issues and pull requests on the first line
* Use the second line and beyond to elaborate on your change in more detail:
  * For bugs, describe the root cause of the issue and how your change addresses it if not obious.
  * For enhancements, explain the consequences of your changes if not obvious.
* Don't worry too much about it, I'll accept almost anything...

#### Python
* Black will automatically reformat your code to meet project standards.  The style is not always pretty, but the benefit of having a rigid standard and a tool to autoformat your code outweighs the downside.
* Flake8, mypy will take care of the rest... so in effect: if the pre-commit hooks pass then you're good to go.
* All code must be type hinted.  mypy should enforce this for you.
  * Avoid gratuitous usage of `Any` as it defeats the point of type hinting.
  * When added an untyped dependency, you can register a mypy exemption in `mypy.ini`
* Avoid dependencies between the subpackages i.e. `markdown` should not depend on `confluence` and vice-versa.

#### Dependencies
* External dependencies must work with the latest version of Python.  As such, I will refuse new dependencies that are not clearly maintained towards that end.
* Dependencies do not have to be typed, but it is nice when they are.
* Junction is a pure-python project; no native or cross-runtime dependencies will be accepted (except for development tools).

