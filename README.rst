###############
SchengenTripper
###############
A utility to add trips and check the length of stay in the Schengen area for any new
trips.

.. warning::
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
    PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
    HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
    CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
    OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

=======
Testing
=======
.. warning::
    Running the unit tests will remove the local database. If you have recorded trips
    that you want to keep you must rename the database file (``schengen.db``) before
    you run any tests.

From a clone of the repository::

    pip install --upgrade pip
    pip install -r build-requirements.txt
    pip install -r requirements.txt
        
    black .
    mypy --install-types --non-interactive .
    coverage run -m pytest -v -m unit --strict-markers
    coverage report -m

=======
Running
=======
The app uses a SQLite database persisted in the file ``schengen.db``, which is
excluded from the repository (i.e. it's a private, local file).

You can run the app to add some trips for a user::

    ./schengen.py alan.christie --arrival 4-nov-22 --departure 21-nov-22
    ./schengen.py alan.christie --arrival 1-dec-22 --departure 7-dec-22

.. note:: 
    Dates are strings that can be interpreted by the Python `dateutil`_ package.

Now we can use the app to get the earliest arrival date for a new trip::

    ./schengen.py alan.christie --trip-duration 30

And, see a record of the days you've visited the area during the last 180 with::
    
    ./schengen.py alan.christie --spent
    
To reset the database simply delete the database file::

    rm schengen.db

.. _dateutil: https://pypi.org/project/python-dateutil/
