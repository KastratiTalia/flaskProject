from flask import Flask, json, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from mongodb import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\admin\\Desktop\\flaskProject\\database\\users_vouchers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# many-to-one: user_spending to user_info
class UserInfo(db.Model):
    __tablename__ = 'user_info'

    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True)
    age = db.Column(db.Integer)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'email': self.email,
            'age': self.age
        }


class UserSpending(db.Model):
    __tablename__ = 'user_spending'

    user_id = db.Column(db.Integer, primary_key=True)
    money_spent = db.Column(db.Float, default=0)
    year = db.Column(db.Integer)

    def to_dict(self):
        return {
            'user_id': self.user_id,
            'money_spent': self.money_spent,
            'year': self.year
        }


# 1. Get all users API
@app.route('/users', methods=['GET'])
def get_all_users():
    all_users = UserInfo.query.all()
    user_list = [user.to_dict() for user in all_users]
    if user_list is not None:
        return jsonify(user_list), 200
    else:
        return jsonify({'error': 'No users'}), 400


# 2. Get user by id API
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    user = UserInfo.query.get(user_id)

    if user is not None:
        user_dict = user.to_dict()
        return jsonify(user_dict), 200
    else:
        return jsonify({"error": "User not found"}), 404


# API 1: TOTAL spending of user_id
# http://127.0.0.1:5000/total_spent?user_id=35
@app.route('/total_spent', methods=['GET'])
def total_spent():
    try:
        user_id = request.args.get('user_id')

        if user_id is None:
            return json.dumps({'error': 'Missing user_id parameter'}), 400

        user_info = UserInfo.query.filter_by(user_id=user_id).first()

        if user_info is None:
            return json.dumps({'error': 'User not found'}), 404

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
        return json.dumps({'error': 'Internal Server Error'}), 500


# API 2:  AVERAGE spending for an age group
# http://127.0.0.1:5000/average_spending_by_age/35
@app.route('/average_spending_by_age/<int:user_id>', methods=['GET'])
def calculate_average_spending(user_id):
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
        total_spending = round(age_query[0][1], 2)

        age_group = get_age_group(user_age)

        response_data = {
            'user_id': user_id,
            'age': user_age,
            'total_spending': total_spending,
            'age_group': age_group
        }

        return jsonify(response_data)

    except Exception as e:
        print("Unexpected error:", str(e))
        return json.dumps({'error': 'Internal Server Error'}), 500


def get_age_group(user_age):
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


# API 3: BONUS calculation
# curl -X POST -H "Content-Type: application/json" -d "
# {\"user_id\": 123, \"total_spending\": 2500}" "http://127.0.0.1:5000/write_to_mongodb"
@app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        total_spending = data.get('total_spending')

        bonus_amount = 2000

        if not user_id or not total_spending:
            return json.dumps({'error': 'Missing user_id or total_spending parameter'}), 400

        existing_user = collection.find_one({'user_id': user_id})

        if existing_user:
            return json.dumps({'error': f'User with user_id {user_id} already exists!'}), 400

        if total_spending < bonus_amount:
            return json.dumps({'error': 'Total spending must be greater than 2000!'}), 400

        result = collection.insert_one(data)

        if result.inserted_id:
            return json.dumps({'success': 'Data was successfully inserted'}), 201
        else:
            return json.dumps({'error': 'Failed to insert data'}), 500

    except Exception as e:
        print("Unexpected error:", str(e))
        return json.dumps({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run(debug=True)
