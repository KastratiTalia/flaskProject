from flask import Flask, json, request, jsonify
from sqlDatabase import *
from mongodb import *

app = Flask(__name__)


# 1. Get all users API
@app.route('/users', methods=['GET'])
def get_all_users():
    conn = db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor = conn.execute("SELECT * FROM user_info")
        users = [
            dict(user_id=row[0], name=row[1], email=row[2], age=row[3])
            for row in cursor.fetchall()
        ]
        if users is not None:
            return jsonify(users)


# 2. Get user by id API
@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_by_id(user_id):
    conn = db_connection()
    cursor = conn.cursor()
    user = None
    if request.method == 'GET':
        cursor.execute("SELECT * FROM user_info WHERE user_id=?", (user_id,))
        rows = cursor.fetchall()
        for r in rows:
            user = r
        if user is not None:
            return jsonify(user), 200


# API 1: TOTAL spending of user_id
# http://127.0.0.1:5000/total_spent?user_id=35
@app.route('/total_spent', methods=['GET'])
def average_spending_by_age():
    try:
        user_id = request.args.get('user_id')

        if user_id is None:
            return json.dumps({'error': 'Missing user_id parameter'}), 400

        query = """SELECT ui.user_id, ui.name, ui.age, SUM(us.money_spent) as total_spending 
                FROM user_info ui
                INNER JOIN user_spending us ON ui.user_id = us.user_id
                WHERE ui.user_id = ?
                GROUP BY ui.user_id, ui.name, ui.age
                """

        result = query_db(query, (user_id,))

        if not result:
            return json.dumps({'error': 'User not found'}), 404
        else:
            user_data = {
                'user_id': result[0][0],
                'name': result[0][1],
                'age': result[0][2],
                'total_spending': round(result[0][3], 2)
            }

        print(user_data)
        return json.dumps(user_data)

    except Exception as e:
        print("Unexpected error:", str(e))
        return json.dumps({'error': 'Internal Server Error'}), 500


# API 2:  AVERAGE spending for an age group
# http://127.0.0.1:5000/average_spending_by_age/35
@app.route('/average_spending_by_age/<int:user_id>', methods=['GET'])
def calculate_average_spending(user_id):
    user_id = request.view_args['user_id']

    query = '''
            SELECT ui.age, AVG(us.money_spent) as average_spending
            FROM user_info ui
            INNER JOIN user_spending us
            ON ui.user_id = us.user_id
            WHERE ui.user_id=?
            GROUP BY ui.age
    '''

    user_data = query_db(query, (user_id,))

    if user_data:
        user_age = user_data[0][0]
        total_spending = round(user_data[0][1], 2)

        if 18 <= user_age <= 24:
            age_group = "18-24"
        elif 25 <= user_age <= 30:
            age_group = "25-30"
        elif 31 <= user_age <= 36:
            age_group = "31-36"
        elif 37 <= user_age <= 47:
            age_group = "37-47"
        else:
            age_group = ">47"

        response_data = {
            'user_id': user_id,
            'age': user_age,
            'total_spending': total_spending,
            "age_group": age_group
        }

        return json.dumps(response_data)
    return "User not found", 404


# API 3: BONUS calculation
@app.route('/write_to_mongodb', methods=['POST'])
def write_to_mongodb():
    data = request.get_json()

    if collection.find_one({'user_id': data['user_id']}):
        return json.dumps({'Error': f'User with user_id {data["user_id"]} already exists!'}), 400
    else:
        if data['total_spending'] >= 2000:
            result = collection.insert_one(data)
            if result.inserted_id:
                return json.dumps({'Success': 'Data was successfully inserted'}), 201
            else:
                return json.dumps({'Error': 'Failed to insert data'}), 500
        else:
            return json.dumps({'Bad Request': 'Total spending must be greater than 2000 !'}), 400


if __name__ == '__main__':
    app.run(debug=True)
