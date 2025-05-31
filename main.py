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

# Funciones GUI
def select_video():
    filepath = filedialog.askopenfilename(filetypes=video_formats)
    if filepath:
        video_path.set(filepath)

def select_output_folder():
    folder = filedialog.askdirectory()
    if folder:
        output_folder.set(folder)

def check_requirements():
    if not video_path.get():
        messagebox.showerror("Error", "Debes seleccionar un archivo de video.")
        return False
    if not selected_format.get():
        messagebox.showerror("Error", "Debes seleccionar un formato de salida.")
        return False
    return True

def start_conversion():
    if check_requirements():
        progress_bar.start(10)
        status_label.config(text="Convirtiendo...")
        threading.Thread(target=convert, daemon=True).start()

def convert():
    video_file = video_path.get()
    out_format = selected_format.get()
    out_folder = output_folder.get() or DEFAULT_OUTPUT_FOLDER
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    try:
        clip = VideoFileClip(video_file)
        audio = clip.audio
        base_filename = os.path.splitext(os.path.basename(video_file))[0]
        output_path = os.path.join(out_folder, f"{base_filename}.{out_format}")
        audio.write_audiofile(output_path)
        clip.close()

        progress_bar.stop()
        progress_bar['value'] = 0
        status_label.config(text="¡Conversión finalizada!")
        messagebox.showinfo("Éxito", f"Audio convertido:\n{output_path}")
    except Exception as e:
        progress_bar.stop()
        progress_bar['value'] = 0
        status_label.config(text="Error durante la conversión.")
        messagebox.showerror("Error", str(e))

# Interfaz gráfica
root = Tk()
root.title("Conversor de Video a Audio")
root.geometry("500x320")
root.resizable(False, False)

video_path = StringVar()
output_folder = StringVar()
selected_format = StringVar(value=audio_formats[0])

Label(root, text="Conversor de Video a Audio", font=("Helvetica", 16, "bold")).pack(pady=10)

Button(root, text="Seleccionar Video", command=select_video, width=30).pack()
Label(root, textvariable=video_path, wraplength=480).pack(pady=5)

Label(root, text="Formato de audio de salida:").pack()
OptionMenu(root, selected_format, *audio_formats).pack()

Button(root, text="Seleccionar carpeta de salida (opcional)", command=select_output_folder, width=30).pack(pady=5)
Label(root, textvariable=output_folder, wraplength=480).pack()

Button(root, text="Empezar", command=start_conversion, bg="#2196F3", fg="white", width=30).pack(pady=10)

# Barra de progreso en modo indeterminado
progress_bar = ttk.Progressbar(root, orient='horizontal', length=400, mode='indeterminate')
progress_bar.pack(pady=5)

status_label = Label(root, text="")
status_label.pack()

root.mainloop()
