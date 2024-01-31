from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DATABASE = 'C:\\Users\\admin\\Desktop\\flaskProject\\database\\users_vouchers.db'


def query_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    data = cur.fetchall()
    conn.close()
    return data


@app.route('/average_spending_by_age', methods=['GET'])
def average_spending_by_age():
    try:
        user_id = request.args.get('user_id')

        if user_id is None:
            return jsonify({'error': 'Missing user_id parameter'}), 400

        query = 'SELECT ui.user_id, ui.name, ui.age, SUM(us.money_spent) as total_spending ' \
                'FROM user_info ui ' \
                'INNER JOIN user_spending us ON ui.user_id = us.user_id ' \
                'WHERE ui.user_id = ? ' \
                'GROUP BY ui.user_id, ui.name, ui.age'

        result = query_db(query, (user_id,))

        if not result:
            return jsonify({'error': 'User not found'}), 404

        user_data = {
            'user_id': result[0][0],
            'name': result[0][1],
            'age': result[0][2],
            'total_spending': result[0][3]
        }

        return jsonify(user_data)

    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    app.run()
