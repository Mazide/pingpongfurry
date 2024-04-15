from curses import flash
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os
import requests
from datetime import datetime

app = Flask(__name__)

DATABASE = 'ping_pong.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()
    players = conn.execute('SELECT * FROM players ORDER BY rating DESC').fetchall()

    players_dict = {player['id']: player['name'] for player in players}

    # Получение списка всех матчей
    matches = conn.execute('SELECT * FROM matches').fetchall()
    print(matches)

    # Формирование и вывод строк с описанием каждого матча
    match_descriptions = []
    for match in matches:
        winner_name = players_dict.get(match['winner_id'])
        loser_name = players_dict.get(match['loser_id'])
    
        
        date = match['match_date']
        if date is not None:
            # Преобразование строки с датой в объект datetime
            match_date_obj = datetime.strptime(match['match_date'], '%Y-%m-%d %H:%M:%S')
        
            # Форматирование даты в формат "2 апреля"
            match_date_formatted = match_date_obj.strftime('%-d %B').replace('January', 'января').replace('February', 'февраля').replace('March', 'марта').replace('April', 'апреля').replace('May', 'мая').replace('June', 'июня').replace('July', 'июля').replace('August', 'августа').replace('September', 'сентября').replace('October', 'октября').replace('November', 'ноября').replace('December', 'декабря')
            match_descriptions.append(winner_name + " " + "赢得" + " " + loser_name + " " + match_date_formatted)

        else:
            print("nodate")

    conn.close()
    return render_template('index.html', gif_url="https://media1.tenor.com/m/zhY9_LLI0xYAAAAd/forrest-gump-ping-pong.gif", players=players, matches=match_descriptions)

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
        
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        conn.execute('INSERT INTO matches (winner_id, loser_id, match_date) VALUES (?, ?, ?)', 
                    (winner_id, loser_id, current_timestamp))
        
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
