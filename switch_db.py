"""
Script para alternar entre la base de datos personal y la base de datos del repositorio.
"""
import os
import shutil
import sys

# Nombres de los archivos de base de datos
REPO_DB = 'invoices.db'
PERSONAL_DB = 'invoices_personal.db'
TEMP_DB = 'invoices_temp.db'

def switch_to_personal():
    """Cambia a la base de datos personal"""
    if not os.path.exists(PERSONAL_DB):
        print(f"Error: No se encontró la base de datos personal ({PERSONAL_DB})")
        return False
    
    # Hacemos una copia de seguridad de la base de datos actual del repositorio
    if os.path.exists(REPO_DB):
        shutil.copy2(REPO_DB, TEMP_DB)
    
    # Copiamos la base de datos personal como la base de datos principal
    shutil.copy2(PERSONAL_DB, REPO_DB)
    
    print(f"Cambiado a la base de datos personal. La base de datos del repositorio se ha guardado como {TEMP_DB}")
    return True

def switch_to_repo():
    """Cambia a la base de datos del repositorio (vacía)"""
    if not os.path.exists(TEMP_DB):
        print(f"Error: No se encontró la base de datos temporal del repositorio ({TEMP_DB})")
        return False
    
    # Hacemos una copia de seguridad de la base de datos personal actual
    if os.path.exists(REPO_DB):
        shutil.copy2(REPO_DB, PERSONAL_DB)
    
    # Restauramos la base de datos del repositorio
    shutil.copy2(TEMP_DB, REPO_DB)
    
    print(f"Cambiado a la base de datos del repositorio. La base de datos personal se ha guardado como {PERSONAL_DB}")
    return True

def show_help():
    """Muestra la ayuda del script"""
    print("Uso: python switch_db.py [personal|repo]")
    print("  personal: Cambia a la base de datos personal")
    print("  repo: Cambia a la base de datos del repositorio (vacía)")
    print("  help: Muestra esta ayuda")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "personal":
        if switch_to_personal():
            sys.exit(0)
        else:
            sys.exit(1)
    elif command == "repo":
        if switch_to_repo():
            sys.exit(0)
        else:
            sys.exit(1)
    elif command == "help":
        show_help()
        sys.exit(0)
    else:
        print(f"Comando desconocido: {command}")
        show_help()
        sys.exit(1)
