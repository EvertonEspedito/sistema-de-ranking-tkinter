import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from PIL import Image, ImageTk
import os

# =========================
# CONFIG VISUAL
# =========================
BG = "#1e1e2f"
FG = "#ffffff"
BTN = "#4e73df"

# =========================
# BANCO DE DADOS
# =========================
conn = sqlite3.connect("ranking.db")
cursor = conn.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS usuarios(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS turmas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS alunos(
id INTEGER PRIMARY KEY AUTOINCREMENT,
nome TEXT,
foto TEXT,
turma_id INTEGER)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS notas(
id INTEGER PRIMARY KEY AUTOINCREMENT,
aluno_id INTEGER,
aula TEXT,
nota REAL,
motivo TEXT)""")

conn.commit()
cursor.execute("INSERT OR IGNORE INTO usuarios(username,password) VALUES('admin','123')")
conn.commit()

# =========================
# LOGIN
# =========================
def login():
    cursor.execute("SELECT * FROM usuarios WHERE username=? AND password=?",
                   (entry_user.get(), entry_pass.get()))
    if cursor.fetchone():
        login_window.destroy()
        main_window()
    else:
        messagebox.showerror("Erro", "Login inválido")

login_window = tk.Tk()
login_window.title("⭐ SuperData Nexus Academy")
login_window.geometry("400x300")
login_window.configure(bg=BG)

tk.Label(login_window,text="Usuário",bg=BG,fg=FG).pack(pady=5)
entry_user = tk.Entry(login_window)
entry_user.pack()

tk.Label(login_window,text="Senha",bg=BG,fg=FG).pack(pady=5)
entry_pass = tk.Entry(login_window,show="*")
entry_pass.pack()

tk.Button(login_window,text="Entrar",bg=BTN,fg="white",command=login).pack(pady=20)

# =========================
# JANELA PRINCIPAL
# =========================
def main_window():
    root = tk.Tk()
    root.title("⭐ SuperData Nexus Academy")
    root.geometry("1100x650")
    root.configure(bg=BG)

    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True)

    # ================= TURMAS =================
    frame_turmas = tk.Frame(notebook, bg=BG)
    notebook.add(frame_turmas, text="Turmas")

    tk.Label(frame_turmas,text="Nome da Turma",bg=BG,fg=FG).pack()
    entry_turma = tk.Entry(frame_turmas)
    entry_turma.pack()

    tree_turmas = ttk.Treeview(frame_turmas,columns=("ID","Nome"),show="headings")
    tree_turmas.heading("ID",text="ID")
    tree_turmas.heading("Nome",text="Nome")
    tree_turmas.pack(fill="both",expand=True,pady=10)

    def carregar_turmas():
        tree_turmas.delete(*tree_turmas.get_children())
        cursor.execute("SELECT * FROM turmas")
        for t in cursor.fetchall():
            tree_turmas.insert("", "end", values=t)

    def add_turma():
        cursor.execute("INSERT INTO turmas(nome) VALUES(?)",(entry_turma.get(),))
        conn.commit()
        carregar_turmas()

    def atualizar_turma():
        selected = tree_turmas.focus()
        if selected:
            id = tree_turmas.item(selected)['values'][0]
            cursor.execute("UPDATE turmas SET nome=? WHERE id=?",
                           (entry_turma.get(),id))
            conn.commit()
            carregar_turmas()

    def excluir_turma():
        selected = tree_turmas.focus()
        if selected:
            id = tree_turmas.item(selected)['values'][0]
            cursor.execute("DELETE FROM turmas WHERE id=?", (id,))
            conn.commit()
            carregar_turmas()

    tk.Button(frame_turmas,text="Cadastrar",bg=BTN,fg="white",command=add_turma).pack()
    tk.Button(frame_turmas,text="Atualizar",bg="#f6c23e",command=atualizar_turma).pack()
    tk.Button(frame_turmas,text="Excluir",bg="#e74a3b",fg="white",command=excluir_turma).pack()

    carregar_turmas()

    # ================= ALUNOS =================
    frame_alunos = tk.Frame(notebook,bg=BG)
    notebook.add(frame_alunos,text="Alunos")

    tk.Label(frame_alunos,text="Nome do Aluno",bg=BG,fg=FG).pack()
    entry_nome = tk.Entry(frame_alunos)
    entry_nome.pack()

    tk.Label(frame_alunos,text="Turma",bg=BG,fg=FG).pack()
    combo_turma = ttk.Combobox(frame_alunos)
    combo_turma.pack()

    def atualizar_combo_turmas():
        cursor.execute("SELECT id,nome FROM turmas")
        combo_turma['values']=[f"{t[0]} - {t[1]}" for t in cursor.fetchall()]

    atualizar_combo_turmas()

    def cadastrar_aluno():
        turma_id = combo_turma.get().split(" - ")[0]
        cursor.execute("INSERT INTO alunos(nome,foto,turma_id) VALUES(?,?,?)",
                       (entry_nome.get(),"",turma_id))
        conn.commit()
        messagebox.showinfo("Sucesso","Aluno cadastrado!")

    tk.Button(frame_alunos,text="Cadastrar",bg=BTN,fg="white",
              command=cadastrar_aluno).pack(pady=10)

    # ================= NOTAS =================
    frame_notas = tk.Frame(notebook,bg=BG)
    notebook.add(frame_notas,text="Notas")

    tk.Label(frame_notas,text="Selecionar Aluno",bg=BG,fg=FG).pack()
    combo_aluno = ttk.Combobox(frame_notas,width=40)
    combo_aluno.pack()

    def atualizar_alunos():
        cursor.execute("SELECT id,nome FROM alunos")
        combo_aluno['values']=[f"{a[0]} - {a[1]}" for a in cursor.fetchall()]

    atualizar_alunos()

    tk.Label(frame_notas,text="Aula",bg=BG,fg=FG).pack()
    entry_aula = tk.Entry(frame_notas)
    entry_aula.pack()

    tk.Label(frame_notas,text="Nota",bg=BG,fg=FG).pack()
    entry_nota = tk.Entry(frame_notas)
    entry_nota.pack()

    tk.Label(frame_notas,text="Motivo",bg=BG,fg=FG).pack()
    entry_motivo = tk.Entry(frame_notas)
    entry_motivo.pack()

    def inserir_nota():
        aluno_id = combo_aluno.get().split(" - ")[0]
        cursor.execute("INSERT INTO notas(aluno_id,aula,nota,motivo) VALUES(?,?,?,?)",
                       (aluno_id,entry_aula.get(),entry_nota.get(),entry_motivo.get()))
        conn.commit()
        messagebox.showinfo("Sucesso","Nota inserida!")

    tk.Button(frame_notas,text="Salvar Nota",bg=BTN,fg="white",
              command=inserir_nota).pack(pady=10)

    # ================= RANKING =================
    frame_rank = tk.Frame(notebook,bg=BG)
    notebook.add(frame_rank,text="Ranking")

    tk.Label(frame_rank,text="Selecionar Turma",bg=BG,fg=FG).pack()
    combo_rank = ttk.Combobox(frame_rank)
    combo_rank.pack()

    def atualizar_combo_rank():
        cursor.execute("SELECT id,nome FROM turmas")
        combo_rank['values']=[f"{t[0]} - {t[1]}" for t in cursor.fetchall()]

    atualizar_combo_rank()

    tree_rank = ttk.Treeview(frame_rank,columns=("Nome","Média"),show="headings")
    tree_rank.heading("Nome",text="Aluno")
    tree_rank.heading("Média",text="Média")
    tree_rank.pack(fill="both",expand=True,pady=10)

    def gerar_ranking():
        tree_rank.delete(*tree_rank.get_children())
        turma_id = combo_rank.get().split(" - ")[0]

        cursor.execute("""
        SELECT alunos.nome, AVG(notas.nota)
        FROM alunos
        JOIN notas ON alunos.id = notas.aluno_id
        WHERE alunos.turma_id=?
        GROUP BY alunos.id
        ORDER BY AVG(notas.nota) DESC
        """,(turma_id,))

        for r in cursor.fetchall():
            tree_rank.insert("", "end", values=(r[0], round(r[1],2)))

    tk.Button(frame_rank,text="Gerar Ranking",bg=BTN,fg="white",
              command=gerar_ranking).pack()

    root.mainloop()

login_window.mainloop()