#!/usr/bin/python3


import os
import subprocess
import platform

def open_with_default_text_editor(filepath):
    filepath = os.path.expanduser(filepath)
    if os.path.exists(filepath):
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)  # No Windows, continua sem bloquear
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', filepath])  # macOS, não bloqueia
            else:  # Linux e outros sistemas Unix-like
                subprocess.Popen(['xdg-open', filepath])  # Linux, não bloqueia
            return True
        except Exception as e:
            print(f"Erro ao tentar abrir o arquivo: {e}")
            return False
    else:
        return False;
    
    return True
# Exemplo de uso:
#open_with_default_text_editor("~/config/stock-viewer/default.stock-viewer.conf.json")
