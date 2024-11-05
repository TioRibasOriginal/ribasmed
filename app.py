# Rota raiz para teste
@app.route('/')
def home():
    return "<h1>Sistema de Prontuário Eletrônico</h1><p>API funcionando corretamente!</p>"

from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect("hospital.db")
    conn.row_factory = sqlite3.Row
    return conn

# Rota para cadastrar paciente
@app.route('/register_patient', methods=['POST'])
def register_patient():
    data = request.json
    name = data['name']
    age = data['age']
    gender = data['gender']
    admission_date = data['admission_date']
    
    conn = get_db_connection()
    conn.execute("INSERT INTO patients (name, age, gender, admission_date) VALUES (?, ?, ?, ?)",
                 (name, age, gender, admission_date))
    conn.commit()
    conn.close()
    return jsonify({"message": "Paciente cadastrado com sucesso!"}), 201

# Rota para registrar tratamento
@app.route('/register_treatment', methods=['POST'])
def register_treatment():
    data = request.json
    patient_id = data['patient_id']
    treatment_date = data['treatment_date']
    treatment_description = data['treatment_description']
    progress_report = data['progress_report']
    
    conn = get_db_connection()
    conn.execute("INSERT INTO treatments (patient_id, treatment_date, treatment_description, progress_report) VALUES (?, ?, ?, ?)",
                 (patient_id, treatment_date, treatment_description, progress_report))
    conn.commit()
    conn.close()
    return jsonify({"message": "Tratamento registrado com sucesso!"}), 201

# Rota para gerar relatório de progresso
@app.route('/generate_progress_report/<int:patient_id>', methods=['GET'])
def generate_progress_report(patient_id):
    conn = get_db_connection()
    patient = conn.execute("SELECT * FROM patients WHERE id = ?", (patient_id,)).fetchone()
    
    if not patient:
        return jsonify({"error": "Paciente não encontrado"}), 404
    
    treatments = conn.execute("SELECT * FROM treatments WHERE patient_id = ? ORDER BY treatment_date", (patient_id,)).fetchall()
    conn.close()
    
    report = {
        "patient_name": patient["name"],
        "treatments": [{"date": t["treatment_date"], "description": t["treatment_description"], "progress": t["progress_report"]} for t in treatments]
    }
    return jsonify(report), 200

# Criação das tabelas no primeiro uso
def create_tables():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        admission_date TEXT
    )
    """)
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        treatment_date TEXT,
        treatment_description TEXT,
        progress_report TEXT,
        FOREIGN KEY (patient_id) REFERENCES patients(id)
    )
    """)
    
    conn.commit()
    conn.close()

# Inicialização
if __name__ == "__main__":
    create_tables()
    app.run(debug=True)
