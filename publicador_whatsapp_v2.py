
import os
import time
import threading
from tkinter import Tk, Label, Button, Text, END, DISABLED, NORMAL, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Ruta base
CARPETA_BASE = r"F:\ventas\no vendidos"
NOMBRE_GRUPO = "De Shopping Chihuahua"
INTERVALO_IMAGENES = 60  # segundos
INTERVALO_CARPETAS = 3600  # segundos

class WhatsAppPublisherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Publicador WhatsApp - De Shopping Chihuahua")

        self.label = Label(root, text="Estado del Publicador:")
        self.label.pack()

        self.log_area = Text(root, height=20, width=80)
        self.log_area.pack()

        self.iniciar_btn = Button(root, text="Iniciar", command=self.iniciar)
        self.iniciar_btn.pack(pady=10)

        self.detener_btn = Button(root, text="Detener", command=self.detener, state=DISABLED)
        self.detener_btn.pack()

        self.publicando = False
        self.driver = None

    def log(self, mensaje):
        self.log_area.config(state=NORMAL)
        self.log_area.insert(END, f"{mensaje}\n")
        self.log_area.see(END)
        self.log_area.config(state=DISABLED)

    def iniciar(self):
        self.iniciar_btn.config(state=DISABLED)
        self.detener_btn.config(state=NORMAL)
        self.publicando = True
        threading.Thread(target=self.proceso_publicacion).start()

    def detener(self):
        self.publicando = False
        self.detener_btn.config(state=DISABLED)
        self.iniciar_btn.config(state=NORMAL)
        self.log("⛔ Publicación detenida por el usuario.")

    def iniciar_whatsapp(self):
        self.log("🔄 Iniciando navegador y cargando WhatsApp Web...")
        options = Options()
        options.add_argument("--user-data-dir=chrome-data")
        options.add_argument("--remote-debugging-port=9222")
        options.add_argument("--disable-extensions")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-infobars")
        options.add_argument("--start-maximized")

        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        self.driver.get("https://web.whatsapp.com")
        self.log("✅ Escanea el código QR si es la primera vez.")
        time.sleep(15)

    def abrir_chat(self, nombre_chat):
        try:
            self.log(f"🔍 Buscando grupo '{nombre_chat}'...")
            search_box = self.driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
            search_box.click()
            search_box.clear()
            search_box.send_keys(nombre_chat)
            time.sleep(3)
            wait = WebDriverWait(self.driver, 10)
            chat = wait.until(EC.element_to_be_clickable(
                (By.XPATH, f'//span[@title="{nombre_chat}"]')
            ))
            chat.click()
            self.log(f"✅ Grupo '{nombre_chat}' abierto.")
        except Exception as e:
            self.log(f"❌ No se pudo abrir el grupo: {e}")
            raise

    def enviar_imagen(self, imagen_path):
        try:
            self.driver.find_element(By.CSS_SELECTOR, "span[data-icon='clip']").click()
            time.sleep(1)
            attach_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            attach_input.send_keys(imagen_path)
            time.sleep(2)
            send_button = self.driver.find_element(By.XPATH, '//span[@data-icon="send"]')
            send_button.click()
            self.log(f"📤 Imagen enviada: {os.path.basename(imagen_path)}")
        except Exception as e:
            self.log(f"⚠️ Error al enviar imagen: {e}")

    def proceso_publicacion(self):
        try:
            self.iniciar_whatsapp()
            self.abrir_chat(NOMBRE_GRUPO)

            while self.publicando:
                for carpeta_num in range(1, 10):
                    carpeta_path = os.path.join(CARPETA_BASE, str(carpeta_num))
                    if not os.path.exists(carpeta_path):
                        self.log(f"⚠️ Carpeta no encontrada: {carpeta_path}")
                        continue

                    imagenes = [f for f in os.listdir(carpeta_path) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
                    if not imagenes:
                        self.log(f"ℹ️ No hay imágenes en la carpeta {carpeta_num}.")
                        continue

                    self.log(f"🚀 Publicando imágenes de la carpeta {carpeta_num}...")

                    for imagen in imagenes:
                        if not self.publicando:
                            break
                        imagen_path = os.path.join(carpeta_path, imagen)
                        self.enviar_imagen(imagen_path)
                        time.sleep(INTERVALO_IMAGENES)

                    if not self.publicando:
                        break

                    self.log(f"⏳ Esperando 1 hora antes de pasar a la siguiente carpeta...")
                    for i in range(INTERVALO_CARPETAS // 60):
                        if not self.publicando:
                            break
                        time.sleep(60)

            self.log("✅ Proceso de publicación finalizado.")

        except Exception as e:
            self.log(f"❌ Error en la publicación: {e}")

        finally:
            if self.driver:
                self.driver.quit()
            self.publicando = False
            self.iniciar_btn.config(state=NORMAL)
            self.detener_btn.config(state=DISABLED)

if __name__ == "__main__":
    root = Tk()
    app = WhatsAppPublisherApp(root)
    root.mainloop()
