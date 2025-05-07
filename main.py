"""
Punto de entrada principal para la aplicación de cotizaciones.
Inicia la interfaz y el sistema de cotizaciones.
"""

import tkinter as tk
import os
from interfaz_cotizador import CotizadorApp
from logica_cotizador import GestorCotizaciones

def crear_cotizaciones_iniciales():
    """
    Crea cotizaciones iniciales si no existe el archivo de persistencia.
    Útil para la primera ejecución o fines de demostración.
    """
    # Verificar si ya existe el archivo de cotizaciones
    if os.path.exists(GestorCotizaciones.ARCHIVO_COTIZACIONES):
        print(f"El archivo {GestorCotizaciones.ARCHIVO_COTIZACIONES} ya existe. No se crearán cotizaciones iniciales.")
        return
    
    # Crear gestor temporal para inicializar el archivo
    gestor = GestorCotizaciones()
    
    # Lista de cotizaciones iniciales de ejemplo
    cotizaciones_ejemplo = [

    ]
    
    # Cargar cotizaciones iniciales y guardar en JSON
    gestor.cargar_cotizaciones_iniciales(cotizaciones_ejemplo)
    gestor.guardar_cotizaciones_en_json()
    
    print(f"Cotizaciones iniciales creadas y guardadas en {GestorCotizaciones.ARCHIVO_COTIZACIONES}")

def main():
    """Función principal para iniciar la aplicación."""
    # Crear cotizaciones de ejemplo si es la primera ejecución
    crear_cotizaciones_iniciales()
    
    # Iniciar la aplicación
    root = tk.Tk()
    app = CotizadorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()