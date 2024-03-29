
# Flask E-shop Application
This repository focuses on a Flask application designed to analyze user data from an E-shop.

## Extensions
- SQL ORM: [Flask-SQLalchemy](https://flask-sqlalchemy.palletsprojects.com/en/3.1.x/)
- NoSQL ORM: [PyMongo](https://pymongo.readthedocs.io/en/stable/)
- Testing: [Unittest library](https://docs.python.org/3/library/unittest.html)
  
## Flask Application Structure
```markdown
flaskProject/
│
├── templates/
│   └── index.html
│
├── tests/
│   └── test_project.py
│
├── users_vouchers.db
├── requirements.txt
└── app.py
```


## Installation
### Requirements
- Python 3.x
### Installation steps:
1. Clone the repository
   ```
   $ git clone https://github.com/KastratiTalia/flaskProject.git
   ```
2. Create a virtual environment (make sure you have Python 3.x installed):
   - On Windows:
   ```
   $ python3 -m venv .venv
   ```
   - On macOS:
   ```
   $ python -m venv venv
   ```
3. Activate the virtual environment:
  - On Windows:
    ```
    $ .\venv\Scripts\activate
    ```
  - On macOS/Linux:
     ```
     $ source venv/bin/activate
     ```
4. Upgrade `pip` to the latest version:
    - On Windows:
    ```
    $ python -m pip install --upgrade pip
    ```
    - On macOS/Linux:
    ```
    $ python3 -m pip install --upgrade pip
    ```
  
5. Install Dependencies
   
   ```
   $ pip install -r requirements.txt
   ```
   
## Run Flask Application
   Run the application
   ```
   $ python app.py
   ```

## Tests
  1. Run all the unit tests:
     ```
     $ python -m unittest tests.test_project
     ```
  2. Run an individual test case:
     ```
     $ python -m unittest tests.test_project.TestProject.test_total_spent_successful
     ```
## API Video Demo
![demo1](https://github.com/KastratiTalia/flaskProject/assets/93604292/5bf009db-cd9d-40bb-8c20-a782fcd41e65)

## Tests Video Demo
![demo2](https://github.com/KastratiTalia/flaskProject/assets/93604292/87c29584-36e7-4001-95b5-ec9d6d56b30d)

## Documentation
- Github Wiki Documentation: [Documentation](https://github.com/KastratiTalia/flaskProject/wiki)
