from flask import Flask, request, jsonify
from sqlalchemy import create_engine


app = Flask(__name__)
engine = create_engine('postgresql://postgres:admin@db:5432/postgres')


@app.route('/members', methods=['POST'])
def members():
    body = request.json

    with engine.connect() as connection:
        row = list(
            connection.execute(
                "INSERT INTO members (name) VALUES (%s) RETURNING *",
                body['name']
            )
        )[0]

    return jsonify({
        "id": row.id,
        "name": row.name
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
