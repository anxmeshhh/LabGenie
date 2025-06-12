import sqlite3

def init_db():
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            readings TEXT NOT NULL,
            aim TEXT,
            theory TEXT,
            procedure TEXT,
            result TEXT,
            graph TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_experiment(name, readings, lab_record, graph):
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO experiments (name, readings, aim, theory, procedure, result, graph)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        readings,
        lab_record.get('aim', ''),
        lab_record.get('theory', ''),
        lab_record.get('procedure', ''),
        lab_record.get('result', ''),
        graph
    ))
    conn.commit()
    experiment_id = c.lastrowid
    conn.close()
    return experiment_id

def get_all_experiments():
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('SELECT id, name FROM experiments')
    experiments = c.fetchall()
    conn.close()
    return experiments

def get_experiment_by_id(experiment_id):
    conn = sqlite3.connect('experiments.db')
    c = conn.cursor()
    c.execute('SELECT * FROM experiments WHERE id = ?', (experiment_id,))
    experiment = c.fetchone()
    conn.close()
    if experiment:
        return {
            'id': experiment[0],
            'name': experiment[1],
            'readings': experiment[2],
            'aim': experiment[3],
            'theory': experiment[4],
            'procedure': experiment[5],
            'result': experiment[6],
            'graph': experiment[7]
        }
    return None