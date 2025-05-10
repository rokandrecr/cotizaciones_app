"""
Pruebas unitarias para el módulo de lógica de cotizaciones.
Este archivo contiene pruebas para la clase GestorCotizaciones y sus métodos.
"""

import unittest
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Importar el módulo a probar
from logica_cotizador import GestorCotizaciones, OPENPYXL_DISPONIBLE

class TestGestorCotizaciones(unittest.TestCase):
    """Clase de pruebas para GestorCotizaciones."""
    
    def setUp(self):
        """
        Configura el entorno para cada prueba.
        Crea un archivo temporal para las cotizaciones.
        """
        # Crear un archivo temporal para las pruebas
        self.temp_dir = tempfile.TemporaryDirectory()
        self.archivo_temp = os.path.join(self.temp_dir.name, "cotizaciones_test.json")
        
        # Guardar el valor original
        self.archivo_original = GestorCotizaciones.ARCHIVO_COTIZACIONES
        
        # Modificar la constante para usar el archivo temporal
        GestorCotizaciones.ARCHIVO_COTIZACIONES = self.archivo_temp
        
        # Cotizaciones de prueba
        self.cotizaciones_prueba = [
            ("Arreglo de mesa", 25000.0, "Decoración"),
            ("Bouquet de novia", 45000.0, "Bouquets"),
            ("Centro de mesa", 15000.0, "Decoración"),
            ("Corona floral", 35000.0, "Coronas")
        ]
        
        # Crear un gestor con datos iniciales
        self.gestor = GestorCotizaciones()
        self.gestor.cargar_cotizaciones_iniciales(self.cotizaciones_prueba)
    
    def tearDown(self):
        """
        Limpia después de cada prueba.
        Restaura la constante original y elimina archivos temporales.
        """
        # Restaurar el valor original
        GestorCotizaciones.ARCHIVO_COTIZACIONES = self.archivo_original
        
        # Limpiar el directorio temporal
        self.temp_dir.cleanup()
    
    def test_inicializacion(self):
        """Prueba la inicialización del gestor de cotizaciones."""
        gestor = GestorCotizaciones()
        self.assertEqual(gestor.cotizaciones_base, self.cotizaciones_prueba)
        self.assertEqual(gestor.cotizaciones_disponibles, self.cotizaciones_prueba)
        self.assertEqual(gestor.cotizaciones_seleccionadas, [])
        self.assertEqual(gestor.comentarios, {})
    
    def test_obtener_categorias_unicas(self):
        """Prueba la obtención de categorías únicas."""
        categorias = self.gestor.obtener_categorias_unicas()
        self.assertEqual(categorias, ["Bouquets", "Coronas", "Decoración"])
    
    def test_filtrar_disponibles_por_categoria(self):
        """Prueba el filtrado de cotizaciones por categoría."""
        # Filtrar por Decoración
        self.gestor.filtrar_disponibles_por_categoria("Decoración")
        self.assertEqual(len(self.gestor.cotizaciones_disponibles), 2)
        
        # Verificar que todos son de Decoración
        for _, _, categoria in self.gestor.cotizaciones_disponibles:
            self.assertEqual(categoria, "Decoración")
        
        # Filtrar por Todas
        self.gestor.filtrar_disponibles_por_categoria("Todas")
        self.assertEqual(len(self.gestor.cotizaciones_disponibles), len(self.cotizaciones_prueba))
    
    def test_agregar_a_seleccionadas(self):
        """Prueba la funcionalidad de agregar a seleccionadas."""
        # Tomar un ítem para agregar
        item = self.cotizaciones_prueba[0]
        
        # Verificar que inicialmente está en disponibles y no en seleccionadas
        self.assertIn(item, self.gestor.cotizaciones_disponibles)
        self.assertNotIn(item, self.gestor.cotizaciones_seleccionadas)
        
        # Agregar a seleccionadas
        resultado = self.gestor.agregar_a_seleccionadas(item)
        
        # Verificar que se agregó correctamente
        self.assertTrue(resultado)
        self.assertIn(item, self.gestor.cotizaciones_seleccionadas)
        self.assertNotIn(item, self.gestor.cotizaciones_disponibles)
        
        # Intentar agregar de nuevo (debería retornar False)
        resultado = self.gestor.agregar_a_seleccionadas(item)
        self.assertFalse(resultado)
    
    def test_quitar_de_seleccionadas(self):
        """Prueba quitar un ítem de seleccionadas."""
        # Primero, agregar un ítem a seleccionadas
        item = self.cotizaciones_prueba[0]
        self.gestor.agregar_a_seleccionadas(item)
        
        # Verificar que está en seleccionadas
        self.assertIn(item, self.gestor.cotizaciones_seleccionadas)
        
        # Quitar de seleccionadas
        resultado = self.gestor.quitar_de_seleccionadas(item)
        
        # Verificar que se quitó correctamente
        self.assertTrue(resultado)
        self.assertNotIn(item, self.gestor.cotizaciones_seleccionadas)
        self.assertIn(item, self.gestor.cotizaciones_disponibles)
        
        # Intentar quitar de nuevo (debería retornar False)
        resultado = self.gestor.quitar_de_seleccionadas(item)
        self.assertFalse(resultado)
    
    def test_calcular_total(self):
        """Prueba el cálculo del total de cotizaciones seleccionadas."""
        # Agregar algunos ítems a seleccionadas
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[0])  # 25000.0
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[2])  # 15000.0
        
        # Calcular el total esperado
        total_esperado = 25000.0 + 15000.0
        
        # Verificar el total calculado
        total_calculado = self.gestor.calcular_total()
        self.assertEqual(total_calculado, total_esperado)
    
    def test_nueva_cotizacion(self):
        """Prueba reiniciar a una nueva cotización."""
        # Agregar algunos ítems a seleccionadas
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[0])
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[1])
        
        # Verificar que hay ítems en seleccionadas
        self.assertTrue(len(self.gestor.cotizaciones_seleccionadas) > 0)
        
        # Crear nueva cotización
        self.gestor.nueva_cotizacion()
        
        # Verificar que seleccionadas está vacía y disponibles tiene todos los ítems
        self.assertEqual(len(self.gestor.cotizaciones_seleccionadas), 0)
        self.assertEqual(len(self.gestor.cotizaciones_disponibles), len(self.cotizaciones_prueba))
    
    def test_agregar_nueva_cotizacion_base(self):
        """Prueba agregar una nueva cotización a la base."""
        # Datos para la nueva cotización
        nombre = "Arco floral"
        precio = 75000.0
        categoria = "Decoración"
        
        # Agregar la nueva cotización
        nueva_cotizacion = self.gestor.agregar_nueva_cotizacion_base(nombre, precio, categoria)
        
        # Verificar que se agregó correctamente
        self.assertIn(nueva_cotizacion, self.gestor.cotizaciones_base)
        self.assertIn(nueva_cotizacion, self.gestor.cotizaciones_disponibles)
        
        # Verificar que se guardó en el archivo JSON
        with open(self.archivo_temp, 'r', encoding='utf-8') as archivo:
            cotizaciones_json = json.load(archivo)
            encontrado = False
            for cotizacion in cotizaciones_json:
                if (cotizacion["nombre"] == nombre and 
                    cotizacion["precio"] == precio and 
                    cotizacion["categoria"] == categoria):
                    encontrado = True
                    break
            self.assertTrue(encontrado)
    
    def test_comentarios(self):
        """Prueba establecer y obtener comentarios."""
        # Tomar un ítem para probar
        item = self.cotizaciones_prueba[0]
        
        # Verificar que inicialmente no tiene comentario
        comentario_inicial = self.gestor.obtener_comentario(item)
        self.assertEqual(comentario_inicial, "")
        
        # Establecer un comentario
        comentario_nuevo = "Este es un comentario de prueba"
        resultado = self.gestor.establecer_comentario(item, comentario_nuevo)
        
        # Verificar que se estableció correctamente
        self.assertTrue(resultado)
        comentario_obtenido = self.gestor.obtener_comentario(item)
        self.assertEqual(comentario_obtenido, comentario_nuevo)
        
        # Verificar que se guardó en el archivo JSON
        with open(self.archivo_temp, 'r', encoding='utf-8') as archivo:
            cotizaciones_json = json.load(archivo)
            nombre, precio, categoria = item
            for cotizacion in cotizaciones_json:
                if (cotizacion["nombre"] == nombre and 
                    cotizacion["precio"] == precio and 
                    cotizacion["categoria"] == categoria):
                    self.assertEqual(cotizacion["comentario"], comentario_nuevo)
                    break
    
    def test_eliminar_cotizacion_base(self):
        """Prueba eliminar una cotización de la base."""
        # Tomar un ítem para eliminar
        item = self.cotizaciones_prueba[0]
        
        # Verificar que está en la base
        self.assertIn(item, self.gestor.cotizaciones_base)
        
        # Eliminar el ítem
        resultado = self.gestor.eliminar_cotizacion_base(item)
        
        # Verificar que se eliminó correctamente
        self.assertTrue(resultado)
        self.assertNotIn(item, self.gestor.cotizaciones_base)
        self.assertNotIn(item, self.gestor.cotizaciones_disponibles)
        
        # Verificar que no está en el archivo JSON
        with open(self.archivo_temp, 'r', encoding='utf-8') as archivo:
            cotizaciones_json = json.load(archivo)
            nombre, precio, categoria = item
            for cotizacion in cotizaciones_json:
                self.assertFalse(
                    cotizacion["nombre"] == nombre and 
                    cotizacion["precio"] == precio and 
                    cotizacion["categoria"] == categoria
                )
    
    @unittest.skipIf(not OPENPYXL_DISPONIBLE, "openpyxl no está instalado")
    def test_exportar_a_excel(self):
        """Prueba la exportación a Excel (solo si openpyxl está disponible)."""
        # Agregar ítems a seleccionadas
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[0])
        self.gestor.agregar_a_seleccionadas(self.cotizaciones_prueba[1])
        
        # Exportar a Excel
        with patch('openpyxl.Workbook') as mock_workbook_class:
            # Configurar el mock
            mock_workbook = MagicMock()
            mock_workbook_class.return_value = mock_workbook
            mock_workbook.active = MagicMock()
            
            # Llamar a la función
            resultado = self.gestor.exportar_a_excel()
            
            # Verificar que se llamó a save con un archivo .xlsx
            args, _ = mock_workbook.save.call_args
            self.assertTrue(args[0].endswith('.xlsx'))
            
            # Verificar que el resultado indica éxito
            self.assertTrue(resultado["exito"])
    
    def test_exportar_a_excel_sin_openpyxl(self):
        """Prueba el manejo de error cuando openpyxl no está disponible."""
        # Guardar el valor original
        openpyxl_original = OPENPYXL_DISPONIBLE
        
        try:
            # Simular que openpyxl no está disponible
            import logica_cotizador
            logica_cotizador.OPENPYXL_DISPONIBLE = False
            
            # Exportar a Excel
            resultado = self.gestor.exportar_a_excel()
            
            # Verificar que el resultado indica error
            self.assertFalse(resultado["exito"])
            self.assertIn("openpyxl", resultado["mensaje"])
            
        finally:
            # Restaurar el valor original
            logica_cotizador.OPENPYXL_DISPONIBLE = openpyxl_original
    
    def test_persistencia_json(self):
        """Prueba la carga y guardado de cotizaciones en JSON."""
        # Crear un gestor nuevo que cargará desde el archivo creado en setUp
        gestor_nuevo = GestorCotizaciones()
        
        # Verificar que cargó las mismas cotizaciones
        self.assertEqual(len(gestor_nuevo.cotizaciones_base), len(self.cotizaciones_prueba))
        for item in self.cotizaciones_prueba:
            self.assertIn(item, gestor_nuevo.cotizaciones_base)
        
        # Modificar las cotizaciones
        nueva_cotizacion = ("Ramo pequeño", 18000.0, "Bouquets")
        gestor_nuevo.agregar_nueva_cotizacion_base(*nueva_cotizacion)
        
        # Crear otro gestor que debería cargar la cotización añadida
        gestor_tercero = GestorCotizaciones()
        self.assertIn(nueva_cotizacion, gestor_tercero.cotizaciones_base)


class TestGestorCotizacionesArchivosInexistentes(unittest.TestCase):
    """Pruebas para situaciones con archivos inexistentes o errores."""
    
    def setUp(self):
        """Configuración para pruebas con archivos inexistentes."""
        # Crear ruta a un archivo que no existe
        self.archivo_inexistente = os.path.join(
            tempfile.gettempdir(), 
            f"archivo_que_no_existe_{os.urandom(8).hex()}.json"
        )
        
        # Guardar el valor original
        self.archivo_original = GestorCotizaciones.ARCHIVO_COTIZACIONES
        
        # Modificar la constante para usar el archivo inexistente
        GestorCotizaciones.ARCHIVO_COTIZACIONES = self.archivo_inexistente
    
    def tearDown(self):
        """Limpieza después de cada prueba."""
        # Restaurar el valor original
        GestorCotizaciones.ARCHIVO_COTIZACIONES = self.archivo_original
        
        # Eliminar el archivo si se creó
        if os.path.exists(self.archivo_inexistente):
            os.remove(self.archivo_inexistente)
    
    def test_inicializacion_archivo_inexistente(self):
        """Prueba inicialización cuando el archivo JSON no existe."""
        gestor = GestorCotizaciones()
        
        # Verificar que se inicializó con listas vacías
        self.assertEqual(gestor.cotizaciones_base, [])
        self.assertEqual(gestor.cotizaciones_disponibles, [])
        self.assertEqual(gestor.cotizaciones_seleccionadas, [])
    
    def test_cargar_cotizaciones_iniciales_archivo_inexistente(self):
        """Prueba cargar cotizaciones iniciales cuando el archivo no existe."""
        gestor = GestorCotizaciones()
        
        # Cotizaciones de prueba
        cotizaciones_prueba = [
            ("Prueba 1", 1000.0, "Categoría 1"),
            ("Prueba 2", 2000.0, "Categoría 2")
        ]
        
        # Cargar cotizaciones iniciales
        gestor.cargar_cotizaciones_iniciales(cotizaciones_prueba)
        
        # Verificar que se cargaron correctamente
        self.assertEqual(gestor.cotizaciones_base, cotizaciones_prueba)
        self.assertEqual(gestor.cotizaciones_disponibles, cotizaciones_prueba)
        
        # Verificar que se creó el archivo
        self.assertTrue(os.path.exists(self.archivo_inexistente))
    
    @patch("json.load")
    def test_manejo_error_json(self, mock_json_load):
        """Prueba el manejo de errores al cargar un JSON mal formado."""
        # Configurar el mock para lanzar una excepción
        mock_json_load.side_effect = json.JSONDecodeError("Error de formato", "", 0)
        
        # Crear el archivo vacío para que exista
        with open(self.archivo_inexistente, 'w') as f:
            f.write("{")  # JSON mal formado
        
        # Inicializar el gestor (debería manejar el error)
        gestor = GestorCotizaciones()
        
        # Verificar que se inicializó con listas vacías
        self.assertEqual(gestor.cotizaciones_base, [])
        self.assertEqual(gestor.cotizaciones_disponibles, [])
        self.assertEqual(gestor.cotizaciones_seleccionadas, [])


if __name__ == "__main__":
    unittest.main()
