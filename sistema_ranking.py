import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
from PIL import Image, ImageTk
import os
import matplotlib.pyplot as plt

# ================= BANCO =================

conn = sqlite3.connect("superdata.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS turmas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS alunos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    foto TEXT,
    turma_id INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS notas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    aluno_id INTEGER,
    aula TEXT,
    nota REAL,
    motivo TEXT
)
""")

conn.commit()

# ================= ESTILO =================

BG = "#1e1e2f"
CARD = "#2a2a40"
BTN = "#4e73df"
TXT = "white"

# ================= APP =================

class App:

    def __init__(self, root):
        self.root = root
        self.root.title("SuperData Nexus Academy")
        self.root.geometry("1100x700")
        self.root.configure(bg=BG)
        self.menu()

    # ---------- UTIL ----------

    def limpar(self):
        for w in self.root.winfo_children():
            w.destroy()

    def botao(self, texto, comando):
        return tk.Button(self.root, text=texto, command=comando,
                         bg=BTN, fg="white", font=("Arial",11,"bold"),
                         width=25)

    # ---------- MENU ----------

    def menu(self):
        self.limpar()
        tk.Label(self.root, text="SuperData Nexus Academy",
                 font=("Arial",24,"bold"),
                 bg=BG, fg="white").pack(pady=30)

        self.botao("Gerenciar Turmas", self.turmas).pack(pady=10)
        self.botao("Gerenciar Alunos", self.alunos).pack(pady=10)
        self.botao("Ranking por Turma", self.ranking_turma).pack(pady=10)

    # ---------- TURMAS ----------

    def turmas(self):
        self.limpar()

        tk.Label(self.root, text="Turmas",
                 font=("Arial",18,"bold"),
                 bg=BG, fg="white").pack(pady=10)

        frame = tk.Frame(self.root, bg=CARD)
        frame.pack(pady=10)

        self.lista_turmas = tk.Listbox(frame, width=40)
        self.lista_turmas.pack(padx=10,pady=10)

        self.atualizar_turmas()

        self.nome_turma = tk.Entry(frame)
        self.nome_turma.pack(pady=5)

        tk.Button(frame, text="Adicionar", command=self.add_turma).pack(pady=3)
        tk.Button(frame, text="Editar", command=self.editar_turma).pack(pady=3)
        tk.Button(frame, text="Excluir", command=self.excluir_turma).pack(pady=3)

        self.botao("Voltar", self.menu).pack(pady=20)

    def atualizar_turmas(self):
        self.lista_turmas.delete(0, tk.END)
        cursor.execute("SELECT * FROM turmas")
        for t in cursor.fetchall():
            self.lista_turmas.insert(tk.END, f"{t[0]} - {t[1]}")

    def add_turma(self):
        cursor.execute("INSERT INTO turmas (nome) VALUES (?)",
                       (self.nome_turma.get(),))
        conn.commit()
        self.atualizar_turmas()

    def editar_turma(self):
        sel = self.lista_turmas.get(tk.ACTIVE)
        if sel:
            id_turma = sel.split(" - ")[0]
            cursor.execute("UPDATE turmas SET nome=? WHERE id=?",
                           (self.nome_turma.get(), id_turma))
            conn.commit()
            self.atualizar_turmas()

    def excluir_turma(self):
        sel = self.lista_turmas.get(tk.ACTIVE)
        if sel:
            id_turma = sel.split(" - ")[0]
            cursor.execute("DELETE FROM turmas WHERE id=?", (id_turma,))
            conn.commit()
            self.atualizar_turmas()

    # ---------- ALUNOS ----------

    def alunos(self):
        self.limpar()

        tk.Label(self.root, text="Alunos",
                 font=("Arial",18,"bold"),
                 bg=BG, fg="white").pack(pady=10)

        frame = tk.Frame(self.root, bg=CARD)
        frame.pack(pady=10)

        self.lista_alunos = tk.Listbox(frame, width=50)
        self.lista_alunos.pack(padx=10,pady=10)

        self.atualizar_alunos()

        self.nome_aluno = tk.Entry(frame)
        self.nome_aluno.pack(pady=5)

        self.combo_turma = ttk.Combobox(frame)
        cursor.execute("SELECT * FROM turmas")
        self.combo_turma['values'] = [f"{t[0]} - {t[1]}" for t in cursor.fetchall()]
        self.combo_turma.pack(pady=5)

        tk.Button(frame, text="Selecionar Foto",
                  command=self.selecionar_foto).pack(pady=3)

        tk.Button(frame, text="Adicionar",
                  command=self.add_aluno).pack(pady=3)

        tk.Button(frame, text="Excluir Aluno",
                  command=self.excluir_aluno).pack(pady=3)

        tk.Button(frame, text="Abrir Histórico",
                  command=self.abrir_historico).pack(pady=3)

        self.botao("Voltar", self.menu).pack(pady=20)

    def atualizar_alunos(self):
        self.lista_alunos.delete(0, tk.END)
        cursor.execute("SELECT id,nome FROM alunos")
        for a in cursor.fetchall():
            self.lista_alunos.insert(tk.END, f"{a[0]} - {a[1]}")

    def selecionar_foto(self):
        self.foto = filedialog.askopenfilename(
            filetypes=[("Imagem","*.png *.jpg")])

    def add_aluno(self):
        turma_id = self.combo_turma.get().split(" - ")[0]
        cursor.execute("INSERT INTO alunos (nome,foto,turma_id) VALUES (?,?,?)",
                       (self.nome_aluno.get(), getattr(self,"foto",None), turma_id))
        conn.commit()
        self.atualizar_alunos()

    def excluir_aluno(self):
        sel = self.lista_alunos.get(tk.ACTIVE)
        if sel:
            id_aluno = sel.split(" - ")[0]
            cursor.execute("DELETE FROM alunos WHERE id=?", (id_aluno,))
            cursor.execute("DELETE FROM notas WHERE aluno_id=?", (id_aluno,))
            conn.commit()
            self.atualizar_alunos()

    # ---------- RANKING POR TURMA ----------

    def ranking_turma(self):
        self.limpar()

        tk.Label(self.root, text="Ranking por Turma",
                 font=("Arial",18,"bold"),
                 bg=BG, fg="white").pack(pady=10)

        self.combo_rank = ttk.Combobox(self.root)
        cursor.execute("SELECT * FROM turmas")
        self.combo_rank['values'] = [f"{t[0]} - {t[1]}" for t in cursor.fetchall()]
        self.combo_rank.pack(pady=10)

        tk.Button(self.root, text="Ver Ranking",
                  command=self.mostrar_ranking).pack(pady=5)

        self.tree = ttk.Treeview(self.root,
                                 columns=("Posição","Nome","Média"),
                                 show="headings")

        for col in ("Posição","Nome","Média"):
            self.tree.heading(col, text=col)

        self.tree.pack(fill="both", expand=True, pady=10)

        self.botao("Voltar", self.menu).pack(pady=10)

    def mostrar_ranking(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        turma_id = self.combo_rank.get().split(" - ")[0]

        cursor.execute("""
        SELECT alunos.id, alunos.nome, AVG(notas.nota)
        FROM alunos
        LEFT JOIN notas ON alunos.id = notas.aluno_id
        WHERE alunos.turma_id=?
        GROUP BY alunos.id
        ORDER BY AVG(notas.nota) DESC
        """,(turma_id,))

        dados = cursor.fetchall()

        for i,a in enumerate(dados):
            medalha=""
            if i==0: medalha="🥇"
            elif i==1: medalha="🥈"
            elif i==2: medalha="🥉"

            self.tree.insert("",tk.END,
                             values=(f"{i+1}º {medalha}",
                                     a[1],
                                     round(a[2] or 0,2)))

    # ---------- HISTÓRICO ----------

    def abrir_historico(self):
        sel = self.lista_alunos.get(tk.ACTIVE)
        if not sel:
            return

        id_aluno = sel.split(" - ")[0]

        janela = tk.Toplevel(self.root)
        janela.geometry("750x650")
        janela.title("Histórico do Aluno")

        cursor.execute("SELECT nome,foto FROM alunos WHERE id=?", (id_aluno,))
        aluno = cursor.fetchone()

        tk.Label(janela, text=aluno[0],
                font=("Arial",16,"bold")).pack(pady=5)

        # FOTO
        if aluno[1] and os.path.exists(aluno[1]):
            img = Image.open(aluno[1])
            img = img.resize((120,120))
            foto = ImageTk.PhotoImage(img)
            lbl = tk.Label(janela,image=foto)
            lbl.image=foto
            lbl.pack()

        # ---------- CAMPOS NOTA ----------
        frame_inputs = tk.Frame(janela)
        frame_inputs.pack(pady=10)

        tk.Label(frame_inputs,text="Aula").grid(row=0,column=0)
        entry_aula = tk.Entry(frame_inputs)
        entry_aula.grid(row=0,column=1)

        tk.Label(frame_inputs,text="Nota").grid(row=1,column=0)
        entry_nota = tk.Entry(frame_inputs)
        entry_nota.grid(row=1,column=1)

        tk.Label(frame_inputs,text="Motivo").grid(row=2,column=0)
        entry_motivo = tk.Entry(frame_inputs,width=40)
        entry_motivo.grid(row=2,column=1)

        # ---------- TABELA ----------
        tree = ttk.Treeview(janela,
                            columns=("ID","Aula","Nota","Motivo"),
                            show="headings")
        tree.heading("ID",text="ID")
        tree.heading("Aula",text="Aula")
        tree.heading("Nota",text="Nota")
        tree.heading("Motivo",text="Motivo")
        tree.column("ID",width=40)
        tree.pack(fill="both",expand=True,pady=10)

        # ---------- FUNÇÃO ATUALIZAR ----------
        def atualizar_notas():
            for item in tree.get_children():
                tree.delete(item)

            cursor.execute("SELECT id,aula,nota,motivo FROM notas WHERE aluno_id=?",(id_aluno,))
            dados = cursor.fetchall()

            for n in dados:
                tree.insert("",tk.END,values=n)

            self.atualizar_alunos()

        atualizar_notas()

        # ---------- ADICIONAR ----------
        def adicionar_nota():
            try:
                cursor.execute("""
                INSERT INTO notas (aluno_id,aula,nota,motivo)
                VALUES (?,?,?,?)
                """,(id_aluno,
                    entry_aula.get(),
                    float(entry_nota.get()),
                    entry_motivo.get()))
                conn.commit()
                atualizar_notas()
                entry_aula.delete(0,tk.END)
                entry_nota.delete(0,tk.END)
                entry_motivo.delete(0,tk.END)
            except:
                messagebox.showerror("Erro","Nota inválida")

        # ---------- EDITAR ----------
        def editar_nota():
            sel_item = tree.selection()
            if not sel_item:
                return
            item = tree.item(sel_item)
            id_nota = item["values"][0]

            cursor.execute("""
            UPDATE notas
            SET aula=?, nota=?, motivo=?
            WHERE id=?
            """,(entry_aula.get(),
                float(entry_nota.get()),
                entry_motivo.get(),
                id_nota))
            conn.commit()
            atualizar_notas()

        # ---------- EXCLUIR ----------
        def excluir_nota():
            sel_item = tree.selection()
            if not sel_item:
                return
            item = tree.item(sel_item)
            id_nota = item["values"][0]

            cursor.execute("DELETE FROM notas WHERE id=?",(id_nota,))
            conn.commit()
            atualizar_notas()

        # ---------- BOTÕES ----------
        frame_btn = tk.Frame(janela)
        frame_btn.pack(pady=5)

        tk.Button(frame_btn,text="Adicionar Nota",
                command=adicionar_nota,
                bg="#4e73df",fg="white").grid(row=0,column=0,padx=5)

        tk.Button(frame_btn,text="Editar Nota",
                command=editar_nota,
                bg="#f6c23e").grid(row=0,column=1,padx=5)

        tk.Button(frame_btn,text="Excluir Nota",
                command=excluir_nota,
                bg="#e74a3b",fg="white").grid(row=0,column=2,padx=5)

        # ---------- GRÁFICO AUTOMÁTICO ----------
        def mostrar_grafico():
            cursor.execute("SELECT nota FROM notas WHERE aluno_id=?",(id_aluno,))
            notas=[n[0] for n in cursor.fetchall()]
            if notas:
                plt.figure()
                plt.plot(range(1,len(notas)+1),notas)
                plt.title("Evolução do Aluno")
                plt.xlabel("Aula")
                plt.ylabel("Nota")
                plt.show()

        tk.Button(janela,text="Ver Gráfico",
                command=mostrar_grafico).pack(pady=5)
# ---------- EXEC ----------

root = tk.Tk()
app = App(root)
root.mainloop()