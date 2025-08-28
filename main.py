import os
import threading
from tkinter import Tk, filedialog, Label, Button, StringVar, OptionMenu, messagebox
from tkinter import ttk
from moviepy import VideoFileClip

# Carpeta por defecto
DEFAULT_OUTPUT_FOLDER = os.path.join(os.getcwd(), "AudioConverted")
if not os.path.exists(DEFAULT_OUTPUT_FOLDER):
    os.makedirs(DEFAULT_OUTPUT_FOLDER)

# Formatos soportados
video_formats = [("Video files", "*.mp4 *.mkv *.mov *.m4a *.avi")]
audio_formats = ["mp3", "wav", "aac", "ogg"]

# Variables globales
videos_queue = []  # Cola de videos (lista de rutas)
is_processing = False

# ────────────────────────────
# Funciones GUI
# ────────────────────────────
def select_videos():
    """Seleccionar múltiples videos y agregarlos a la cola"""
    filepaths = filedialog.askopenfilenames(filetypes=video_formats)
    for fp in filepaths:
        if fp not in videos_queue:
            videos_queue.append(fp)
            tree.insert("", "end", values=(os.path.basename(fp), "Pendiente"))

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)

def start_conversion():
    global is_processing
    if not videos_queue:
        messagebox.showerror("Error", "Debes seleccionar al menos un video.")
        return
    if not selected_format.get():
        messagebox.showerror("Error", "Debes seleccionar un formato de salida.")
        return
    if is_processing:
        messagebox.showinfo("En proceso", "Ya hay una conversión en marcha.")
        return

    is_processing = True
    threading.Thread(target=process_queue, daemon=True).start()

def process_queue():
    """Procesa todos los videos de la cola uno por uno"""
    global is_processing
    progress_bar.start(10)

    while videos_queue:
        video_file = videos_queue.pop(0)
        # Buscar item en el tree y actualizar estado
        for item in tree.get_children():
            if tree.item(item, "values")[0] == os.path.basename(video_file):
                tree.item(item, values=(os.path.basename(video_file), "Convirtiendo..."))

        convert(video_file)

    progress_bar.stop()
    is_processing = False
    status_label.config(text="✅ Conversión finalizada")

def convert(video_file):
    """Convierte un solo video a audio"""
    out_format = selected_format.get()
    out_folder = output_folder.get() or DEFAULT_OUTPUT_FOLDER
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    try:
        clip = VideoFileClip(video_file)
        if not clip.audio:
            raise Exception("El video no contiene pista de audio.")
        base_filename = os.path.splitext(os.path.basename(video_file))[0]
        output_path = os.path.join(out_folder, f"{base_filename}.{out_format}")
        clip.audio.write_audiofile(output_path, logger=None)
        clip.close()

        status = f"Completado ✓ ({out_format.upper()})"
        messagebox.showinfo("Éxito", f"Audio convertido:\n{output_path}")
    except Exception as e:
        status = "Error ❌"
        messagebox.showerror("Error", str(e))

    # Actualizar estado en la tabla
    for item in tree.get_children():
        if tree.item(item, "values")[0] == os.path.basename(video_file):
            tree.item(item, values=(os.path.basename(video_file), status))

# ────────────────────────────
# Interfaz gráfica
# ────────────────────────────
root = Tk()
root.title("🎵 Conversor de Video a Audio")
root.geometry("800x600")


# Variables de GUI (ahora después de root)
video_path = StringVar()
output_folder = StringVar()
selected_format = StringVar(value=audio_formats[0])


# Estilos modernos
style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Segoe UI", 10), padding=6)
style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)
style.configure("TLabel", font=("Segoe UI", 10))

Label(root, text="🎥 Conversor de Video a Audio", font=("Segoe UI", 16, "bold")).pack(pady=10)

# Botones
button_frame = ttk.Frame(root)
button_frame.pack(pady=5)
ttk.Button(button_frame, text="➕ Agregar Videos", command=select_videos).grid(row=0, column=0, padx=5)
ttk.Button(button_frame, text="📂 Seleccionar Carpeta de salida", command=select_output_folder).grid(row=0, column=1, padx=5)

Label(root, textvariable=output_folder, wraplength=580, foreground="gray").pack()

# Tabla de videos (cola)
tree = ttk.Treeview(root, columns=("video", "estado"), show="headings", height=8)
tree.heading("video", text="Archivo de Video")
tree.heading("estado", text="Estado")
tree.column("video", width=300)
tree.column("estado", width=150)
tree.pack(pady=10)

# Formato de salida
format_frame = ttk.Frame(root)
format_frame.pack()
Label(format_frame, text="Formato de salida: ").grid(row=0, column=0, padx=5)
ttk.OptionMenu(format_frame, selected_format, *audio_formats).grid(row=0, column=1)

# Botón de empezar
ttk.Button(root, text="🚀 Empezar Conversión", command=start_conversion).pack(pady=10)

# Barra de progreso
progress_bar = ttk.Progressbar(root, orient='horizontal', length=500, mode='indeterminate')
progress_bar.pack(pady=5)

status_label = Label(root, text="", font=("Segoe UI", 10))
status_label.pack()

root.mainloop()
