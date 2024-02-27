import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from pymongo import MongoClient

app = Flask(__name__)

# Database path
current_file_path = os.path.abspath(__file__)
current_directory = os.path.dirname(current_file_path)
db_file_path = os.path.join(current_directory, 'users_vouchers.db')

# SQLALCHEMY settings
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_file_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# MongoDB settings
client = MongoClient('mongodb://localhost:27017/')
m_db = client.userDB
collection = m_db.userCollection


# Models
class UserInfo(db.Model):
    """
    SQLAlchemy Model for user information.

    Attributes:
    - user_id (int): Primary key for the user.
    - name (str): User's name.
    - email (str): User's email (unique).
    - age (int): User's age.
    """

    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)

    def to_dict(self):
        """
        Convert UserInfo instance to a dictionary.

        Returns:
        dict: Dictionary containing user information.
        """

        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }


class UserSpending(db.Model):
    """
    SQLAlchemy Model for user spending.

    Attributes:
    - user_id (int): Primary key for the user.
    - money_spent (float): Amount of money spent by the user (default is 0).
    - year (int): Year associated with the spending.
    """

    __tablename__ = 'user_spending'

    user_id = db.Column(db.Integer, primary_key=True)
    money_spent = db.Column(db.Float, default=0)
    year = db.Column(db.Integer)

    def to_dict(self):
        """
        Convert UserSpending instance to a dictionary.

        Returns:
        dict: Dictionary containing spending information.
        """
        return {
            'user_id': self.user_id,
            'money_spent': self.money_spent,
            'year': self.year
        }


@app.route('/')
def index():
    """
    Route handler for the home page.

    Returns:
    str: Rendered HTML template.
    """
    return render_template('index.html')


@app.route('/total_spent', methods=['GET'])
def total_spent():
    """
    API endpoint to get the total spending of a user.

    Usage Example:
    http://127.0.0.1:5000/total_spent?user_id=35

    Returns:
    jsonify: JSON response containing user data and total spending.
    """
    try:
        user_id = request.args.get('user_id')

        if user_id is None:
            return jsonify({'error': 'Missing user_id parameter'}), 400

        user_info = UserInfo.query.filter_by(user_id=user_id).first()

        if user_info is None:
            return jsonify({'error': 'User not found'}), 404

        total_spending = db.session.query(db.func.sum(UserSpending.money_spent)).filter_by(user_id=user_id).scalar()

        if total_spending is None:
            total_spending = 0

        user_data = {
            'user_id': user_info.user_id,
            'name': user_info.name,
            'age': user_info.age,
            'total_spending': round(total_spending, 2)
        }

        print(user_data)
        return jsonify(user_data)

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/average_spending_by_age/<int:user_id>', methods=['GET'])
def calculate_average_spending(user_id):
    """
    API endpoint to calculate the average spending for a user's age group.

    Args:
        user_id (int): The user ID extracted from the URL.

    Usage Example:
    http://127.0.0.1:5000/average_spending_by_age/35

    Returns:
    jsonify: JSON response containing user data, age, average spending, and age group.
    """
    try:
        user_info = UserInfo.query.filter_by(user_id=user_id).first()

        if user_info is None:
            return "User not found", 404

        age_query = db.session.query(UserInfo.age, db.func.avg(UserSpending.money_spent).label('average_spending')) \
            .join(UserSpending, UserInfo.user_id == UserSpending.user_id) \
            .filter(UserInfo.user_id == user_id) \
            .group_by(UserInfo.age) \
            .all()

        if not age_query:
            return "User has no spending data", 404

        user_age = age_query[0][0]
        average_spending = round(age_query[0][1], 2)

        age_group = get_age_group(user_age)

        response_data = {
            'user_id': user_id,
            'age': user_age,
            'average_spending': average_spending,
            'age_group': age_group
        }

        return jsonify(response_data)

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


def get_age_group(user_age):
    """
    Helper function to determine the age group based on user's age.

    Args:
    - user_age (int): The age of the user.

    Returns:
    str: Age group string.
    """
    if 18 <= user_age <= 24:
        return "18-24"
    elif 25 <= user_age <= 30:
        return "25-30"
    elif 31 <= user_age <= 36:
        return "31-36"
    elif 37 <= user_age <= 47:
        return "37-47"
    else:
        return ">47"



@app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    """
    API endpoint to write user data to MongoDB that have earned a bonus.

    Example Usage Command:
    curl -X POST -H "Content-Type: application/json" -d "
    {\"user_id\": 123, \"total_spending\": 2500}" "http://127.0.0.1:5000/write_to_mongodb"

    Returns:
    jsonify: JSON response indicating success or failure.
    """
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        total_spending = data.get('total_spending')

        bonus_amount = 2000

        if not user_id or not total_spending:
            return jsonify({'error': 'Missing user_id or total_spending parameter'}), 400

        existing_user = collection.find_one({'user_id': user_id})

        if existing_user:
            return jsonify({'error': f'User with user_id {user_id} already exists!'}), 400

        if total_spending < bonus_amount:
            return jsonify({'error': 'Total spending must be greater than 2000!'}), 400

        result = collection.insert_one(data)

        if result.inserted_id:
            return jsonify({'success': 'Data was successfully inserted'}), 201
        else:
            return jsonify({'error': 'Failed to insert data'}), 500

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/users', methods=['GET'])
def get_all_users():
    """
    API endpoint to retrieve information for all users.

    Returns:
    jsonify: JSON response containing a list of users and their count if available,
    or an error message if no users are found.
    """
    try:
        all_users = UserInfo.query.all()
        user_list = [user.to_dict() for user in all_users]

        if user_list:
            return jsonify({'users': user_list, 'count': len(user_list)}), 200
        else:
            return jsonify({'error': 'No users'}), 404

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """
    API endpoint to retrieve information for a specific user by user_id.

    Args:
    - user_id (int): User ID to look up.

    Returns:
    jsonify: JSON response containing user information if the user is found,
    or an error message if the user is not found.
    """
    try:
        user = UserInfo.query.get(user_id)

        if user is not None:
            user_dict = user.to_dict()
            return jsonify(user_dict), 200
        else:
            return jsonify({"error": "User not found"}), 404

    except Exception as e:

        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
