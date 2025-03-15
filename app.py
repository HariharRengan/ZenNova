from flask import Flask, render_template, request, redirect, url_for, session, send_file
from meditater import main
from therapy import generate_therapy
from fitness import generate_fitness
from sleep import create_profile

import os, base64
import time, sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)

conn = sqlite3.connect('meditater.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tracks (name TEXT, time INTEGER)''')
c.execute('''CREATE TABLE IF NOT EXISTS workouts (name TEXT, time INTEGER)''')
conn.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/mood')
def mood():
    return render_template('mood.html')

@app.route('/mood/<feeling>')
def mood_f(feeling):
    session['feeling'] = feeling
    session['redo'] = True
    return redirect('/journal')

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    if request.method == 'POST':
        session['jsave'] = (request.form['selfdata'], request.form['journal'])
        session['journal'] = request.form['selfdata'] + '\n' + request.form['journal']
        session['lang'] = 'zh-CN' if request.form['lang'] == 'zh-CN' else request.form['lang'][:2]
        session['redo'] = True
        return redirect('/soundtrack')
    p1, p2 = session.get('jsave', ('', ''))
    return render_template('journal.html', p1=p1, p2=p2)

@app.route('/soundtrack')
def soundtrack():
    return render_template('soundtrack.html')

@app.route('/soundtrack/<track>')
def soundtrack_t(track):
    session['track'] = track
    session['redo'] = True
    return redirect('/meditate')

@app.route('/meditate')
def meditate():
    c.execute('DELETE FROM tracks WHERE time < ?', (int(time.time()) - 86400,))
    conn.commit()
    if 'redo' not in session:
        return redirect('/mood')
    if 'journal' not in session:
        return redirect('/journal')
    if 'track' not in session:
        return redirect('/soundtrack')
    if 'feeling' not in session:
        return redirect('/mood')
    if session['redo']:
        user_day = session['journal']
        feeling = session['feeling']
        lang = session['lang']
        track = session['track']
        mixed_audio, cover_image = main(user_day, feeling, track, lang)
        session['mixed_audio'] = mixed_audio
        session['cover_image'] = cover_image
        session['redo'] = False
        print('Meditation complete')
        conn.execute('INSERT INTO tracks VALUES (?, ?)', (track, int(time.time())))
        conn.commit()
    else:
        mixed_audio = session['mixed_audio']
        cover_image = session['cover_image']
    return render_template('meditate.html', audio=mixed_audio, image=cover_image)

@app.route('/wellbeing-companion', methods=['GET', 'POST'])
def therapy():
    if request.method == 'POST':
        user_prompt = request.form['prompt']
        history = session.get('history', [])
        response = generate_therapy(user_prompt, history)
        session['history'] = history + [user_prompt] + [response]
        return render_template('therapy.html', history=session['history'])
    return render_template('therapy.html')

@app.route('/fitness', methods=['GET', 'POST'])
def fitness():
    c.execute('DELETE FROM workouts WHERE time < ?', (int(time.time()) - 86400,))
    conn.commit()
    if request.method == 'POST':
        img = request.files['fridgeImage']
        img_data = img.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        fridge = request.form['fridgeDescription']
        odata = request.form['extraComments']
        language = request.form['lang'] if request.form['lang'] == 'zh-CN' else request.form['lang'][:2]
        a, b, c1 = generate_fitness(img_base64, fridge, odata, language)
        session['audio'] = a
        session['diet'] = b.replace('#', '\n')
        session['exercise'] = c1
        conn.execute('INSERT INTO workouts VALUES (?, ?)', (a, int(time.time())))
        conn.commit()
        return render_template('fitness.html', audio = session['audio'], exercise = session['exercise'], diet = session['diet'])
    return render_template('fitness.html', audio = session.get('audio', None), exercise = session.get('exercise', None), diet = session.get('diet', None))

@app.route('/sleep', methods=['GET', 'POST'])
def sleep():
    if request.method == 'POST':
        sleep_data = create_profile(request.form['sleepData'] + '\nSleep Data:' + request.form['hsleepData'])
        return render_template('sleep.html', info=sleep_data)
    return render_template('sleep.html')

if __name__ == '__main__':
    app.run(debug=True)