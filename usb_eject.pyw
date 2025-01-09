import ctypes
from ctypes import wintypes
import os
import subprocess

def eject_usb(drive_letter):
    """
    Éjecte un périphérique USB en utilisant les API Windows.
    """
    drive_path = f"\\\\.\\{drive_letter}:"
    GENERIC_READ = 0x80000000
    FILE_SHARE_READ = 0x00000001
    FILE_SHARE_WRITE = 0x00000002
    OPEN_EXISTING = 3
    IOCTL_STORAGE_EJECT_MEDIA = 0x2D4808

    # Ouvrir un handle pour le périphérique
    handle = ctypes.windll.kernel32.CreateFileW(
        drive_path,
        GENERIC_READ,
        FILE_SHARE_READ | FILE_SHARE_WRITE,
        None,
        OPEN_EXISTING,
        0,
        None
    )

    if handle == -1:
        print(f"Impossible d'ouvrir le périphérique {drive_letter}:")
        return False

    # Envoyer la commande d'éjection
    result = ctypes.windll.kernel32.DeviceIoControl(
        handle,
        IOCTL_STORAGE_EJECT_MEDIA,
        None,
        0,
        None,
        0,
        ctypes.byref(wintypes.DWORD()),
        None
    )

    # Fermer le handle
    ctypes.windll.kernel32.CloseHandle(handle)

    if result:
        print(f"Le périphérique {drive_letter}: a été éjecté avec succès.")
        return True
    else:
        print(f"Échec de l'éjection du périphérique {drive_letter}:")
        return False


def kill_pythonw():
    """
    Arrête tous les processus 'pythonw.exe' via la commande TASKKILL.
    """
    try:
        print("Arrêt de tous les processus pythonw.exe...")
        subprocess.run(["cmd", "/c", "TASKKILL /F /IM pythonw.exe /T"], check=True)
        print("Tous les processus pythonw.exe ont été arrêtés.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'arrêt des processus pythonw.exe : {e}")


if __name__ == "__main__":
    drive_letter = "D"  # Remplacez par la lettre attribuée à votre clé USB
    if os.path.exists(f"{drive_letter}:\\"):
        if eject_usb(drive_letter):
            kill_pythonw()  # Arrête pythonw.exe après éjection réussie
    else:
        print(f"Aucun périphérique trouvé sur {drive_letter}:\\")
