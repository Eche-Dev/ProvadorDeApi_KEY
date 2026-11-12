"""
Punto de entrada principal para el Probador de API Keys.
Por defecto abre la GUI de escritorio. Si pasas --web, abre la interfaz web.
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Probador de API Keys & REST APIs ⚡")
    parser.add_argument("--web", action="store_true", help="Iniciar la interfaz Web en el navegador en lugar de la ventana nativa.")
    args = parser.parse_args()

    if args.web:
        import app_web
        print("Iniciando Interfaz Web...")
        app_web.open_browser()
        app_web.app.run(host="127.0.0.1", port=5000)
    else:
        import gui
        print("Iniciando Interfaz de Escritorio...")
        app = gui.ApiKeyTesterApp()
        app.mainloop()

if __name__ == "__main__":
    main()
