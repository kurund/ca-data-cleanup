# Data Cleanup Application for Career Aware Data

## Features include
* Ability to manage batches
* Allows admin to upload the OMR data files for the batch
* Files are transformed into respective CSV files that can be directly mapped to data in SF


## Setup
1. Clone the project
   > git clone https://github.com/kurund/ca-data-cleanup.git
2. Install virtulenv (https://pypi.python.org/pypi/virtualenv)
3. Create and activate virtualenv
   > virtualenv -p python3 env <br/>
   > source env/bin/activate.fish
4. Install required packages
   > pip install -r careeraware/requirements.txt
5. Setup database
   > cd careeraware <br/>
   > python manage.py migrate
6. Run the server
   > python manage.py runserver
7. Check if application is running correctly
   > http://127.0.0.1:8000/
8. Create superuser for the admin backend
   > python manage.py createsuperuser
   