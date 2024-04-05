from curses import flash
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests

app = Flask(__name__)

DATABASE = 'ping_pong.db'
TENOR_API_KEY = 'AIzaSyB_VYfk9Mn2odoFpbSIIjrOYSCMtZNO3yE'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


TENOR_API_KEY = 'AIzaSyAXnRcCb4d8m062Z38cj1aNVovjdgntGzY'

def get_random_gif(keyword="pingpong"):
    url = f"https://g.tenor.com/v1/search?q={keyword}&key={TENOR_API_KEY}&limit=1"
    print(url)
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        gif_url = data['results'][0]['media'][0]['gif']['url']
        return gif_url
    else:
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM players ORDER BY rating DESC').fetchall()
    conn.close()
    print(get_random_gif())
    return render_template('index.html', gif_url="https://media1.tenor.com/m/zhY9_LLI0xYAAAAd/forrest-gump-ping-pong.gif", players=players)

def calculate_new_ratings(winner_rating, loser_rating):
    K = 32
    expected_winner = 1 / (1 + 10 ** ((loser_rating - winner_rating) / 400))
    expected_loser = 1 - expected_winner
    
    new_winner_rating = winner_rating + K * (1 - expected_winner)
    new_loser_rating = loser_rating + K * (0 - expected_loser)
    
    return new_winner_rating, new_loser_rating

@app.route('/match', methods=('GET', 'POST'))
def match():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM players').fetchall()
    
    if request.method == 'POST':
        winner_id = request.form['winner']
        loser_id = request.form['loser']
        
        # Получаем текущие рейтинги
        winner_rating = conn.execute('SELECT rating FROM players WHERE id = ?', (winner_id,)).fetchone()['rating']
        loser_rating = conn.execute('SELECT rating FROM players WHERE id = ?', (loser_id,)).fetchone()['rating']
        
        # Рассчитываем новые рейтинги
        new_winner_rating, new_loser_rating = calculate_new_ratings(winner_rating, loser_rating)
        
        # Обновляем рейтинги в базе данных
        conn.execute('UPDATE players SET rating = ? WHERE id = ?', (new_winner_rating, winner_id))
        conn.execute('UPDATE players SET rating = ? WHERE id = ?', (new_loser_rating, loser_id))
        
        # Добавляем запись о матче
        conn.execute('INSERT INTO matches (winner_id, loser_id) VALUES (?, ?)', (winner_id, loser_id))
        
        conn.commit()
        
        return redirect(url_for('index'))
    
    return render_template('match.html', players=players)

@app.route('/add_player', methods=('GET', 'POST'))
def add_player():
    if request.method == 'POST':
        name = request.form['name']
        rating = request.form.get('rating', 1000)  # Используем 1000 как значение рейтинга по умолчанию
        if not name:
            flash('Имя игрока обязательно!')
        else:
            conn = get_db_connection()
            conn.execute('INSERT INTO players (name, rating) VALUES (?, ?)', (name, rating))
            conn.commit()
            conn.close()
            return redirect(url_for('index'))
    return render_template('add_player.html')


if __name__ == '__main__':
    app.run(debug=True)
