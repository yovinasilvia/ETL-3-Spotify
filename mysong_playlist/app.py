from flask import Flask, request

app = Flask(__name__)

@app.route('/callback')
def callback():
    # Ambil authorization code dari URL
    auth_code = request.args.get('code')
    if auth_code:
        return f"Authorization code received: {auth_code}"
    else:
        return "No authorization code received"

if __name__ == '__main__':
    app.run(port=8888)
