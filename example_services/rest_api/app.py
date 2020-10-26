from flask import Flask, request, jsonify
from sqlalchemy import create_engine


app = Flask(__name__)
engine = create_engine("mysql+pymysql://root:admin@db:3306/mydb")


@app.route("/members", methods=["POST"])
def members():
    body = request.json

    with engine.connect() as connection:
        connection.execute("INSERT INTO members (name) VALUES (%s)", body["name"])

        row = list(
            connection.execute("SELECT * FROM members WHERE id=LAST_INSERT_ID()")
        )[0]

    return jsonify({"id": row.id, "name": row.name})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8080)
