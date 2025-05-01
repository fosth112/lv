from flask import Flask
from app.api.routes import routes

app = Flask(__name__)
app.register_blueprint(routes)

# ✅ เพิ่ม route สำหรับเช็ค root URL
@app.route('/')
def health_check():
    return "Free Fire LV API is live!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
