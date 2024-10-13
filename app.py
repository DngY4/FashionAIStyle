from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_babel import Babel, gettext
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import numpy as np
import cv2
from tensorflow.keras.models import load_model
from ai_training import FashionAITrainer
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['LANGUAGES'] = ['en', 'fr', 'es']
CORS(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
babel = Babel(app)

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')

# Load fashion knowledge base
with open('fashion_knowledge.json', 'r') as f:
    fashion_knowledge = json.load(f)

# Initialize TF-IDF vectorizer
tfidf = TfidfVectorizer()
occasion_tfidf = tfidf.fit_transform(fashion_knowledge['occasions'])

# Load AI model
ai_trainer = FashionAITrainer()
ai_trainer.load_model('fashion_ai_model.h5')

# User model for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Mock user database
users = {'admin': {'password': 'admin_password'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@babel.localeselector
def get_locale():
    return request.accept_languages.best_match(app.config['LANGUAGES'])

def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    return ' '.join([word for word in tokens if word.isalnum() and word not in stop_words])

def get_closest_occasion(user_input):
    preprocessed_input = preprocess_text(user_input)
    input_tfidf = tfidf.transform([preprocessed_input])
    similarities = cosine_similarity(input_tfidf, occasion_tfidf)
    closest_match = fashion_knowledge['occasions'][similarities.argmax()]
    return closest_match

def analyze_image(image_path):
    img = cv2.imread(image_path)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = img / 255.0
    img = np.expand_dims(img, axis=0)
    
    # Assuming we have a trained model for image classification
    # prediction = image_model.predict(img)
    # predicted_class = np.argmax(prediction)
    # return fashion_knowledge['style_personalities'][predicted_class]
    
    # For now, we'll return a mock result
    return "classic"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/style_recommendation', methods=['POST'])
def style_recommendation():
    data = request.json
    occasion = data.get('occasion', '')
    preferred_color = data.get('preferred_color', '').lower()
    body_type = data.get('body_type', '').lower()

    closest_occasion = get_closest_occasion(occasion)
    
    # Use AI model for style prediction
    occasion_index = fashion_knowledge['occasions'].index(closest_occasion)
    style_prediction = ai_trainer.model.predict(np.array([occasion_index]))
    predicted_style = list(fashion_knowledge['style_personalities'].keys())[style_prediction.argmax()]

    if closest_occasion in fashion_knowledge['style_rules']:
        outfit = fashion_knowledge['style_rules'][closest_occasion]
    else:
        outfit = fashion_knowledge['style_rules']['casual']

    if preferred_color in fashion_knowledge['color_combinations']:
        colors = [preferred_color] + fashion_knowledge['color_combinations'][preferred_color]
    else:
        colors = ["black", "white"]

    if body_type in fashion_knowledge['body_type_recommendations']:
        body_type_rec = fashion_knowledge['body_type_recommendations'][body_type]
    else:
        body_type_rec = gettext("Wear clothes that make you feel comfortable and confident.")

    response = {
        "outfit": outfit,
        "color_scheme": colors,
        "body_type_recommendation": body_type_rec,
        "predicted_style": predicted_style,
        "message": gettext("For a {occasion} occasion, we recommend a {style} style: {outfit}. "
                   "Color scheme: {colors}. {body_type_rec}").format(
                       occasion=closest_occasion,
                       style=predicted_style,
                       outfit=', '.join(outfit),
                       colors=', '.join(colors),
                       body_type_rec=body_type_rec
                   )
    }

    return jsonify(response)

@app.route('/api/trend_analysis', methods=['GET'])
def trend_analysis():
    return jsonify({"current_trends": fashion_knowledge['current_trends']})

@app.route('/api/style_quiz', methods=['POST'])
def style_quiz():
    data = request.json
    answers = data.get('answers', [])
    
    # Simple scoring system
    style_scores = {style: sum(1 for answer in answers if answer == style) for style in fashion_knowledge['style_personalities']}
    dominant_style = max(style_scores, key=style_scores.get)
    
    return jsonify({
        "dominant_style": dominant_style,
        "description": gettext(fashion_knowledge['style_personalities'][dominant_style])
    })

@app.route('/api/train_ai', methods=['POST'])
@login_required
def train_ai():
    data = request.json
    new_data = data.get('new_data', {})
    
    # Validate new data
    if not validate_new_data(new_data):
        return jsonify({"error": gettext("Invalid data format")}), 400
    
    # Update fashion knowledge base
    for key, value in new_data.items():
        if key in fashion_knowledge:
            if isinstance(fashion_knowledge[key], list):
                fashion_knowledge[key].extend(value)
            elif isinstance(fashion_knowledge[key], dict):
                fashion_knowledge[key].update(value)

    # Save updated fashion knowledge
    with open('fashion_knowledge.json', 'w') as f:
        json.dump(fashion_knowledge, f, indent=2)

    # Retrain AI model
    trainer = FashionAITrainer()
    trainer.train_occasion_style_model()
    trainer.save_model('fashion_ai_model.h5')

    return jsonify({"message": gettext("AI model updated and retrained successfully")})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({"error": gettext("No file part")}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": gettext("No selected file")}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        style = analyze_image(file_path)
        return jsonify({"style": style})
    return jsonify({"error": gettext("File type not allowed")}), 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('admin'))
        flash(gettext('Invalid username or password'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin():
    return render_template('admin.html', fashion_knowledge=fashion_knowledge)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def validate_new_data(new_data):
    required_keys = set(fashion_knowledge.keys())
    if not set(new_data.keys()).issubset(required_keys):
        return False
    # Add more specific validation rules here
    return True

if __name__ == '__main__':
    app.run(debug=True)