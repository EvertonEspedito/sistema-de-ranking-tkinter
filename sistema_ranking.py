import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from PIL import Image, ImageTk
import os

# =========================
# BANCO DE DADOS
# =========================

conn = sqlite3.connect("ranking.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT,
    foto TEXT,
    turma_id INTEGER,
    FOREIGN KEY(turma_id) REFERENCES turmas(id)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    aula TEXT,
    nota REAL,
    motivo TEXT,
    FOREIGN KEY(aluno_id) REFERENCES alunos(id)
)
""")

conn.commit()

# cria usuário padrão
cursor.execute("INSERT OR IGNORE INTO usuarios (username,password) VALUES ('admin','123')")
conn.commit()

# =========================
# LOGIN
# =========================

def login():
    user = entry_user.get()
    pwd = entry_pass.get()

    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?", (user, pwd))
    if cursor.fetchone():
        login_window.destroy()
        main_window()
    else:
        messagebox.showerror("Erro", "Login inválido")


login_window = tk.Tk()
login_window.title("⭐ SuperData Nexus Academy")

tk.Label(login_window, text="Usuário").pack()
entry_user = tk.Entry(login_window)
entry_user.pack()

tk.Label(login_window, text="Senha").pack()
entry_pass = tk.Entry(login_window, show="*")
entry_pass.pack()

tk.Button(login_window, text="Entrar", command=login).pack(pady=10)
login_window.geometry("600x400")


# =========================
# JANELA PRINCIPAL
# =========================

def main_window():
    global root
    root = tk.Tk()
    root.title("⭐ SuperData Nexus Academy")
    root.geometry("1000x600")

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # ===== ABA TURMAS =====
    frame_turmas = tk.Frame(notebook)
    notebook.add(frame_turmas, text="Turmas")

    tk.Label(frame_turmas, text="Nome da Turma").pack()
    entry_turma = tk.Entry(frame_turmas)
    entry_turma.pack()

    def add_turma():
        cursor.execute("INSERT INTO turmas (nome) VALUES (?)", (entry_turma.get(),))
        conn.commit()
        messagebox.showinfo("Sucesso", "Turma cadastrada!")

    tk.Button(frame_turmas, text="Cadastrar Turma", command=add_turma).pack()

    # ===== ABA ALUNOS =====
    frame_alunos = tk.Frame(notebook)
    notebook.add(frame_alunos, text="Alunos")

    tk.Label(frame_alunos, text="Nome do Aluno").pack()
    entry_nome = tk.Entry(frame_alunos)
    entry_nome.pack()

    tk.Label(frame_alunos, text="Selecionar Turma").pack()
    combo_turma = ttk.Combobox(frame_alunos)
    combo_turma.pack()

    def atualizar_turmas():
        cursor.execute("SELECT id, nome FROM turmas")
        turmas = cursor.fetchall()
        combo_turma['values'] = [f"{t[0]} - {t[1]}" for t in turmas]

    atualizar_turmas()

    foto_path = tk.StringVar()

    def escolher_foto():
        caminho = filedialog.askopenfilename()
        foto_path.set(caminho)

    tk.Button(frame_alunos, text="Escolher Foto", command=escolher_foto).pack()

    def cadastrar_aluno():
        turma_id = combo_turma.get().split(" - ")[0]
        cursor.execute("INSERT INTO alunos (nome, foto, turma_id) VALUES (?,?,?)",
                       (entry_nome.get(), foto_path.get(), turma_id))
        conn.commit()
        messagebox.showinfo("Sucesso", "Aluno cadastrado!")

    tk.Button(frame_alunos, text="Cadastrar Aluno", command=cadastrar_aluno).pack()

    # ===== ABA NOTAS =====
    frame_notas = tk.Frame(notebook)
    notebook.add(frame_notas, text="Notas")

    tk.Label(frame_notas, text="Selecionar Aluno (ID)").pack()
    entry_aluno_id = tk.Entry(frame_notas)
    entry_aluno_id.pack()

    tk.Label(frame_notas, text="Aula").pack()
    entry_aula = tk.Entry(frame_notas)
    entry_aula.pack()

    tk.Label(frame_notas, text="Nota").pack()
    entry_nota = tk.Entry(frame_notas)
    entry_nota.pack()

    tk.Label(frame_notas, text="Motivo").pack()
    entry_motivo = tk.Entry(frame_notas)
    entry_motivo.pack()

    def inserir_nota():
        cursor.execute("""
        INSERT INTO notas (aluno_id,aula,nota,motivo)
        VALUES (?,?,?,?)
        """, (entry_aluno_id.get(), entry_aula.get(), entry_nota.get(), entry_motivo.get()))
        conn.commit()
        messagebox.showinfo("Sucesso", "Nota lançada!")

    tk.Button(frame_notas, text="Inserir Nota", command=inserir_nota).pack()

    # ===== ABA RANKING =====
    frame_ranking = tk.Frame(notebook)
    notebook.add(frame_ranking, text="Ranking")

    tree = ttk.Treeview(frame_ranking, columns=("Nome","Média"), show="headings")
    tree.heading("Nome", text="Nome")
    tree.heading("Média", text="Média")
    tree.pack(fill="both", expand=True)

    def atualizar_ranking():
        for i in tree.get_children():
            tree.delete(i)

        cursor.execute("""
        SELECT alunos.nome, AVG(notas.nota) as media
        FROM alunos
        JOIN notas ON alunos.id = notas.aluno_id
        GROUP BY alunos.id
        ORDER BY media DESC
        """)
        dados = cursor.fetchall()

        for d in dados:
            tree.insert("", "end", values=d)

    tk.Button(frame_ranking, text="Atualizar Ranking", command=atualizar_ranking).pack()

    root.mainloop()


login_window.mainloop()