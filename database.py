# ============================================================
# database.py — Complete Database with all tables
# ============================================================

import sqlite3
from datetime import datetime

DATABASE = 'autism.db'


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # USERS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            name             TEXT    NOT NULL,
            email            TEXT    NOT NULL UNIQUE,
            password         TEXT    NOT NULL,
            created_at       TEXT    NOT NULL,
            is_verified      INTEGER DEFAULT 0,
            verify_token     TEXT,
            is_admin         INTEGER DEFAULT 0
        )
    ''')

    # PREDICTIONS table (AQ-10 results)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id         INTEGER NOT NULL,
            date            TEXT    NOT NULL,
            result          TEXT    NOT NULL,
            confidence      REAL    NOT NULL,
            autism_prob     REAL    NOT NULL,
            no_autism_prob  REAL    NOT NULL,
            age             INTEGER NOT NULL,
            gender          TEXT    NOT NULL,
            a1  INTEGER, a2  INTEGER, a3  INTEGER,
            a4  INTEGER, a5  INTEGER, a6  INTEGER,
            a7  INTEGER, a8  INTEGER, a9  INTEGER, a10 INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # FACIAL RESULTS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facial_results (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id           INTEGER NOT NULL,
            date              TEXT    NOT NULL,
            behavioral_score  REAL    NOT NULL,
            behavioral_risk   TEXT    NOT NULL,
            eye_contact       REAL,
            blink_rate        REAL,
            blink_score       REAL,
            head_movement     REAL,
            face_presence     REAL,
            expression_score  REAL,
            duration_seconds  REAL,
            mode              TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')

    # COMBINED RESULTS table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS combined_results (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id             INTEGER NOT NULL,
            date                TEXT    NOT NULL,
            prediction_id       INTEGER,
            facial_id           INTEGER,
            aq10_result         TEXT,
            aq10_confidence     REAL,
            behavioral_score    REAL,
            combined_score      REAL,
            combined_risk       TEXT,
            risk_level          TEXT,
            FOREIGN KEY (user_id)        REFERENCES users (id),
            FOREIGN KEY (prediction_id)  REFERENCES predictions (id),
            FOREIGN KEY (facial_id)      REFERENCES facial_results (id)
        )
    ''')

    conn.commit()

    # Add new columns to existing tables if upgrading
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0')
        conn.commit()
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN verify_token TEXT')
        conn.commit()
    except Exception:
        pass
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        conn.commit()
    except Exception:
        pass

    conn.close()
    print("Database initialized successfully!")


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(name, email, password, verify_token=None):
    conn   = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users
            (name, email, password, created_at, is_verified, verify_token)
            VALUES (?, ?, ?, ?, 0, ?)
        ''', (name, email, password,
              datetime.now().strftime("%d %b %Y"), verify_token))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return get_user_by_id(user_id)
    except sqlite3.IntegrityError:
        conn.close()
        return None


def get_user_by_email(email):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_id(user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return user


def get_user_by_token(token):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE verify_token = ?', (token,))
    user = cursor.fetchone()
    conn.close()
    return user


def verify_user_email(user_id):
    conn = get_db()
    conn.execute('''
        UPDATE users SET is_verified = 1, verify_token = NULL
        WHERE id = ?
    ''', (user_id,))
    conn.commit()
    conn.close()


def update_user_profile(user_id, name, password=None):
    conn = get_db()
    if password:
        conn.execute(
            'UPDATE users SET name = ?, password = ? WHERE id = ?',
            (name, password, user_id)
        )
    else:
        conn.execute(
            'UPDATE users SET name = ? WHERE id = ?',
            (name, user_id)
        )
    conn.commit()
    conn.close()


def get_all_users():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users ORDER BY id DESC')
    users  = cursor.fetchall()
    conn.close()
    return users


# ============================================================
# PREDICTION FUNCTIONS
# ============================================================

def save_prediction(user_id, result, confidence, autism_prob,
                    no_autism_prob, age, gender, answers):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (
            user_id, date, result, confidence,
            autism_prob, no_autism_prob, age, gender,
            a1, a2, a3, a4, a5, a6, a7, a8, a9, a10
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        datetime.now().strftime("%d %b %Y, %I:%M %p"),
        result, confidence, autism_prob, no_autism_prob,
        age, gender,
        answers[0], answers[1], answers[2], answers[3], answers[4],
        answers[5], answers[6], answers[7], answers[8], answers[9]
    ))
    conn.commit()
    prediction_id = cursor.lastrowid
    conn.close()
    return prediction_id


def get_user_predictions(user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions WHERE user_id = ?
        ORDER BY id DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results


def get_prediction_by_id(prediction_id, user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions WHERE id = ? AND user_id = ?
    ''', (prediction_id, user_id))
    result = cursor.fetchone()
    conn.close()
    return result


def get_latest_prediction(user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM predictions WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def delete_prediction(prediction_id, user_id):
    conn = get_db()
    conn.execute('''
        DELETE FROM predictions WHERE id = ? AND user_id = ?
    ''', (prediction_id, user_id))
    conn.commit()
    conn.close()


def get_all_predictions():
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT p.*, u.name, u.email
        FROM predictions p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    ''')
    results = cursor.fetchall()
    conn.close()
    return results


# ============================================================
# FACIAL RESULT FUNCTIONS
# ============================================================

def save_facial_result(user_id, data):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO facial_results (
            user_id, date, behavioral_score, behavioral_risk,
            eye_contact, blink_rate, blink_score,
            head_movement, face_presence, expression_score,
            duration_seconds, mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        datetime.now().strftime("%d %b %Y, %I:%M %p"),
        data.get('behavioral_score', 0),
        data.get('behavioral_risk', ''),
        data.get('eye_contact', 0),
        data.get('blink_rate', 0),
        data.get('blink_score', 0),
        data.get('head_movement', 0),
        data.get('face_presence', 0),
        data.get('expression_score', 0),
        data.get('duration_seconds', 0),
        data.get('mode', 'basic')
    ))
    conn.commit()
    facial_id = cursor.lastrowid
    conn.close()
    return facial_id


def get_latest_facial_result(user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM facial_results WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
    ''', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result


# ============================================================
# COMBINED RESULT FUNCTIONS
# ============================================================

def save_combined_result(user_id, prediction_id, facial_id,
                         aq10_result, aq10_confidence,
                         behavioral_score, combined_score,
                         combined_risk, risk_level):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO combined_results (
            user_id, date, prediction_id, facial_id,
            aq10_result, aq10_confidence, behavioral_score,
            combined_score, combined_risk, risk_level
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        datetime.now().strftime("%d %b %Y, %I:%M %p"),
        prediction_id, facial_id,
        aq10_result, aq10_confidence,
        behavioral_score, combined_score,
        combined_risk, risk_level
    ))
    conn.commit()
    conn.close()


def get_user_combined_results(user_id):
    conn   = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM combined_results WHERE user_id = ?
        ORDER BY id DESC
    ''', (user_id,))
    results = cursor.fetchall()
    conn.close()
    return results


# ============================================================
# STATS FUNCTIONS
# ============================================================

def get_user_stats(user_id):
    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT COUNT(*) as total FROM predictions WHERE user_id = ?',
        (user_id,)
    )
    total = cursor.fetchone()['total']

    cursor.execute('''
        SELECT COUNT(*) as positive FROM predictions
        WHERE user_id = ? AND result = "Autism Detected"
    ''', (user_id,))
    positive = cursor.fetchone()['positive']

    cursor.execute('''
        SELECT AVG(confidence) as avg_conf FROM predictions
        WHERE user_id = ?
    ''', (user_id,))
    avg_conf = cursor.fetchone()['avg_conf']

    cursor.execute(
        'SELECT COUNT(*) as total FROM facial_results WHERE user_id = ?',
        (user_id,)
    )
    facial_total = cursor.fetchone()['total']

    conn.close()
    return {
        'total':        total,
        'positive':     positive,
        'negative':     total - positive,
        'avg_conf':     round(avg_conf, 2) if avg_conf else 0,
        'facial_total': facial_total
    }


def get_admin_stats():
    conn   = get_db()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM users')
    total_users = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM predictions')
    total_predictions = cursor.fetchone()['total']

    cursor.execute('SELECT COUNT(*) as total FROM facial_results')
    total_facial = cursor.fetchone()['total']

    cursor.execute('''
        SELECT COUNT(*) as total FROM predictions
        WHERE result = "Autism Detected"
    ''')
    total_positive = cursor.fetchone()['total']

    conn.close()
    return {
        'total_users':       total_users,
        'total_predictions': total_predictions,
        'total_facial':      total_facial,
        'total_positive':    total_positive
    }