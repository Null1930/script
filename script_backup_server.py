# Bibliotecas a importar
import os
import smtplib
from ftplib import FTP_TLS
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Comprimimos el directorio que vamos a subir
def comprimirDir(pathDir):
    # Verificar si la carpeta existe
    if not os.path.exists(pathDir):
        print(f"La carpeta '{pathDir}' no existe.")
        return

    # Obtener la fecha actual con formato
    fechaActual = datetime.now().strftime("%Y%m%d")

    # Crear el nombre del archivo zip con el formato backup(fecha).zip
    dirComprimido= f"backup{fechaActual}.zip"

    # Comando para comprimir la carpeta usando tar
    comandoTarBash = f"tar -cf {dirComprimido} -C {os.path.dirname(pathDir)} {os.path.basename(pathDir)}"

    # Ejecutar el comando usando subprocess
    os.system(comandoTarBash)

    print(f"La carpeta '{pathDir}' ha sido comprimida en '{dirComprimido}'.")

    return dirComprimido

# Envio de la copia de seguridad mediante FTPS
def envioFTP(file, serverIP, userFTP, passwdFTP):
    # Datos de conexión FTPS
    host = serverIP
    user = userFTP
    passwd = passwdFTP

    # Subir el archivo comprimido al servidor FTPS
    try:
        with FTP_TLS() as ftps:
            ftps.connect(host)
            ftps.login(user, passwd) # Intenta conectar con las credenciales
            ftps.prot_p()

            # Contamos los archivos que hay en el directorio, no puede haber más de 10
            numFiles = len(ftps.nlst())

            # Si hay más de 10 borramos el más antiguo
            if numFiles > 10:
                listFiles = os.listdir(ftps.nlst()) # Listamos los archivos
                deleteFile = listFiles[0] # Saco el primero
                os.remove(deleteFile) # Lo borro
                print("Archivo más antiguo borrado")

            # Subir el archivo al servidor
            with open(file, 'rb') as archivo:
                ftps.storbinary(f'STOR {os.path.basename(file)}', archivo)

            print(f"Archivo '{file}' enviado exitosamente a {host}")
            enviar_correo_gmail()
    except Exception as e:
        print(f"Error al enviar el archivo a {host}: {e}") # Si falla la conexion

    # Borramos el archivo
    os.remove(file)

def enviar_correo_gmail():
    # Configuración del servidor SMTP de Gmail
    servidor_smtp = "smtp.gmail.com"
    puerto_smtp = 587
    usuario_gmail = 'jesusrazim@gmail.com'
    contrasena_gmail = 'stjv mhac fbyp kejq'
    destinatario = 'jgarcia124@ieszaidinvergeles.org'

    # Configuración del mensaje
    mensaje = MIMEMultipart()
    mensaje['From'] = usuario_gmail
    mensaje['To'] = destinatario
    mensaje['Subject'] = 'FTP-Tarea realizada'
    cuerpo = 'Tarea completada con exito'

    # Agregar cuerpo del mensaje
    mensaje.attach(MIMEText(cuerpo, 'plain'))

    # Iniciar conexión con el servidor SMTP de Gmail
    with smtplib.SMTP(servidor_smtp, puerto_smtp) as servidor:
        servidor.starttls()
        servidor.login(usuario_gmail, contrasena_gmail)

        # Enviar el correo
        servidor.send_message(mensaje)

    print(f"Correo enviado a {destinatario}")

backupDir = '/home/maverick/Escritorio/public_html' # El archivo a subir
servidor = '192.168.112.69'  # La IP del servidor
usuario = 'sancheese' # Un usuario
contraseña = '12345' # Y su contraseña

envioFTP(comprimirDir(backupDir),servidor,usuario,contraseña)

#crontab
0 0 * * * /home/maverick/Escritorio/script_backup_server.py



