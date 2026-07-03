import json
import random
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from janome.tokenizer import Tokenizer

app = Flask(__name__)
DB_FILE = 'app.db'
tokenizer = Tokenizer()

FONTS = ['Roboto', 'Bebas Neue', 'Cinzel', 'Dancing Script', 'Press Start 2P', 'Lobster', 'Oswald', 'Playfair Display']
WEIGHTS = ['400', '700', '900']
EFFECTS = ['art-shadow', 'art-glow', 'art-blur', 'art-hollow', '']

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS artworks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_content TEXT,
                styles_json TEXT,
                bg_color TEXT,
                intensity INTEGER
            )
        ''')

@app.route('/', methods=['GET'])
def index():
    with sqlite3.connect(DB_FILE) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute('SELECT * FROM artworks ORDER BY id DESC').fetchall()
        gallery = []
        for row in rows:
            # 古いデータにintensityがない場合のフォールバックを設定
            intensity = row['intensity'] if 'intensity' in row.keys() and row['intensity'] is not None else 20
            gallery.append({
                'id': row['id'],
                'text_content': row['text_content'],
                'styles': json.loads(row['styles_json']),
                'bg_color': row['bg_color'],
                'intensity': intensity
            })
    return render_template('index.html', gallery=gallery, preview=None)

@app.route('/preview', methods=['POST'])
def preview():
    text = request.form.get('text_content', '')
    words = [token.surface for token in tokenizer.tokenize(text) if token.surface.strip()]
    
    styled_words = []
    for word in words:
        # Python側で全てのランダム要素を確定して保存する
        styled_words.append({
            'text': word,
            'font': random.choice(FONTS),
            'weight': random.choice(WEIGHTS),
            'hue': random.randint(0, 360),
            'effect': random.choice(EFFECTS),
            'size_factor': round(0.3 + random.random() * 1.7, 3),
            'rot_factor': round(random.random() - 0.5, 3),
            'color_shift_factor': round(random.random(), 3)
        })
    
    bg_color = "#0f172a" 
    
    preview_data = {
        'text': text,
        'styled_words': styled_words,
        'styles_json': json.dumps(styled_words),
        'bg_color': bg_color
    }
    return render_template('index.html', gallery=[], preview=preview_data)

@app.route('/save', methods=['POST'])
def save():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            'INSERT INTO artworks (text_content, styles_json, bg_color, intensity) VALUES (?, ?, ?, ?)',
            (request.form['text_content'], request.form['styles_json'], request.form['bg_color'], request.form['intensity'])
        )
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)