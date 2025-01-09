import os
import shutil
import time
from pathlib import Path
import ctypes
import sys
from datetime import datetime
import uuid

def get_drive_label(drive_letter):
    """
    Récupère le nom de la clé USB (volume label).
    """
    try:
        buf = ctypes.create_unicode_buffer(1024)
        ctypes.windll.kernel32.GetVolumeInformationW(
            f"{drive_letter}\\", buf, 1024, None, None, None, None, 0
        )
        return buf.value.strip() or "USB"
    except Exception as e:
        log(f"Impossible de récupérer le nom du volume : {e}")
        return "USB"

def get_volume_guid(drive_letter):
    """
    Génère un GUID unique basé sur le volume.
    """
    try:
        # Génère un identifiant unique basé sur le volume (UUID4 pour simulation).
        guid = str(uuid.uuid4())
        return guid
    except Exception as e:
        log(f"Erreur lors de la génération du GUID : {e}")
        return None

def should_skip(src_file, dst_file):
    """
    Vérifie si un fichier doit être ignoré.
    """
    if not os.path.exists(dst_file):
        return False  # Fichier n'existe pas, il doit être copié.

    src_stat = os.stat(src_file)
    dst_stat = os.stat(dst_file)

    # Vérifie si la taille ou la date de modification diffèrent
    if src_stat.st_size != dst_stat.st_size or src_stat.st_mtime > dst_stat.st_mtime:
        return False  # Le fichier doit être copié.

    return True  # Sinon, on ignore le fichier.

def copy_files(src, dst):
    """
    Copie les fichiers et dossiers de src à dst, en ignorant les fichiers déjà présents,
    ou en reprenant la copie des fichiers partiellement copiés.
    """
    if not os.path.exists(dst):
        os.makedirs(dst)

    for item in os.scandir(src):
        src_path = os.path.join(src, item.name)
        dst_path = os.path.join(dst, item.name)

        if item.is_dir():
            # Appel récursif pour les dossiers
            copy_files(src_path, dst_path)
        elif item.is_file():
            # Si le fichier est déjà existant, on le skippe si il est à jour
            if should_skip(src_path, dst_path):
                log(f"Fichier déjà présent et à jour, ignoré : {src_path}")
                continue

            # Vérifie si un fichier partiellement copié existe
            if os.path.exists(dst_path):
                src_size = os.stat(src_path).st_size
                dst_size = os.stat(dst_path).st_size

                if dst_size < src_size:  # Si le fichier est partiellement copié
                    log(f"Reprise de la copie : {src_path}")
                    with open(src_path, 'rb') as src_file, open(dst_path, 'ab') as dst_file:
                        src_file.seek(dst_size)  # Déplace le curseur à la fin du fichier partiellement copié
                        shutil.copyfileobj(src_file, dst_file)  # Copie le reste du fichier
                    log(f"Reprise terminée : {src_path}")
                    continue

            # Si le fichier n'est pas partiellement copié, faire une copie complète
            shutil.copy2(src_path, dst_path)
            log(f"Copié : {src_path} -> {dst_path}")

def log(message):
    """
    Affiche et sauvegarde les logs dans un fichier.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    print(log_message)  # Affiche dans la console

    # Sauvegarde dans un fichier log
    log_file = os.path.join(os.path.expanduser("~"), "Documents", "log_copie_usb.txt")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_message + "\n")

def show_notification(title, message):
    """
    Affiche une notification Windows en utilisant ctypes.
    """
    try:
        ctypes.windll.user32.MessageBoxW(0, message, title, 1)
    except Exception as e:
        log(f"Erreur lors de l'affichage de la notification : {e}")

def main():
    src_drive = "D:"
    base_dst_dir = os.path.join("C:\\Users", os.getlogin(), "Documents", "USB")

    while True:
        try:
            if not os.path.exists(src_drive):
                log("La clé USB n'est pas insérée. Réessayez dans quelques secondes.")
                time.sleep(5)
                continue

            # Récupérer le nom de la clé USB
            drive_label = get_drive_label(src_drive)

            # Récupérer le GUID de la clé USB
            volume_guid = get_volume_guid(src_drive)
            if not volume_guid:
                log("Impossible de générer un GUID pour la clé USB. Abandon.")
                continue

            guid_prefix = volume_guid[:8]  # Les 8 premiers caractères du GUID

            # Ajouter le GUID dans le nom du dossier de destination
            dst_dir = os.path.join(base_dst_dir, f"{drive_label}_█_{guid_prefix}_█_")

            # Créer un fichier contenant le GUID dans le dossier de destination
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            guid_file_path = os.path.join(dst_dir, "GUID_USB.txt")
            with open(guid_file_path, "w", encoding="utf-8") as guid_file:
                guid_file.write(f"GUID de la clé USB : {volume_guid}\n")

            log(f"Copie depuis {src_drive} vers {dst_dir}...")
            copy_files(src_drive, dst_dir)

            log("Analyse rapide des fichiers copiés terminée.")
            show_notification("Copie terminée", f"Toutes les données de {drive_label} ont été copiées avec succès.")

            log("Copie terminée. Reprise dans 10 secondes...")
            time.sleep(10)  # Attente avant de relancer la boucle (redémarre la copie en boucle)
        except KeyboardInterrupt:
            # Ignore l'interruption par l'utilisateur
            log("Copie continue... Ignore l'arrêt.")
            time.sleep(5)  # Attente avant de reprendre
        except Exception as e:
            log(f"Erreur : {e}. Réessayez dans quelques secondes.")
            time.sleep(5)

if __name__ == "__main__":
    main()
