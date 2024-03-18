###############
SchengenTripper
###############

.. image:: https://img.shields.io/github/actions/workflow/status/alanbchristie/SchengenTripper/test.yaml
   :alt: GitHub Workflow Status
.. image:: https://img.shields.io/github/v/release/alanbchristie/schengentripper
   :alt: GitHub release (latest SemVer)
.. image:: https://img.shields.io/github/license/alanbchristie/schengentripper
   :alt: GitHub

A Python 3 utility to record trips and check the length of new visits to the EU Schengen
Area to ensure you don't break the current legal requirement not to spend more than
90 days in any 180 day period (the *90 day rule*).

The app records trips in a SQLite database against a user and can therefore
record trips against specific users.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
    CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
    OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

============
Contributing
============

The project uses: -

*   `pre-commit`_ to enforce linting of files prior to committing them to the
    upstream repository
*   `Commitizen`_ to enforce a `Conventional Commit`_ commit message format
*   `Black`_ for code formatting
*   `mypy`_ and `pylint`_ for static analysis

You **MUST** comply with these choices in order to  contribute to the project.
To get started review the pre-commit utility and the conventional commit style
and then set-up your local clone by following the Installation and
Quick Start sections::

    pip install -r build-requirements.txt
    pre-commit install -t commit-msg -t pre-commit

Now the project's rules will run on every commit, and you can check the
current health of your clone with::

    pre-commit run --all-files

=======
Testing
=======

Warning
    Running the unit tests will remove the local database. If you have recorded trips
    that you want to keep you must rename the database file (``schengen.db``) before
    you run any tests.

From a clone of the repository::

    pip install --upgrade pip
    pip install -r build-requirements.txt
    pip install -r requirements.txt

    coverage run -m pytest -v -m unit --strict-markers
    coverage report -m

    pre-commit run --all-files

===============
Running the App
===============
The app uses a SQLite database persisted in the file ``schengen.db``, which is
excluded from the repository (i.e. it's a private, local file).

You can run the app to add some trips for a user. Here we add two trips
against the user ``alan.christie``::

    ./schengen.py alan.christie --arrival 2-sep-23 --departure 1-oct-23
    ./schengen.py alan.christie --arrival 4-nov-23 --departure 18-nov-23
    ./schengen.py alan.christie --arrival 14-feb-24 --departure 15-mar-24

.. note::
    Dates are strings that can be interpreted by the Python `dateutil`_ package.

Now we can use the app to get the earliest arrival date for a new trip, one
that will not result in a breach of the *90 day rule*::

    ./schengen.py alan.christie --trip-duration 30

And, see a record of the days you've visited the area during the last 180 with::

    ./schengen.py alan.christie --spent

Or, display the histogram of accumulated days between two dates with::

    ./schengen.py alan.christie --histogram-180 --arrival 1-jan-23 --departure 1-jan-24

To reset the database simply delete the database file::

    rm schengen.db

.. _black: https://black.readthedocs.io/en/stable
.. _commitizen: https://commitizen-tools.github.io/commitizen/
.. _conventional commit: https://www.conventionalcommits.org/en/v1.0.0/
.. _dateutil: https://pypi.org/project/python-dateutil/
.. _mypy: https://pypi.org/project/mypy/
.. _pre-commit: https://pre-commit.com
.. _pylint: https://pypi.org/project/pylint/
