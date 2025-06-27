from flask_cors import CORS

   app = Flask(__name__)
   CORS(app, origins=["https://flipflow-7c658.firebaseapp.com"])

from pdf_to_video_api import app

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port) 
