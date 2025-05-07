"""
Módulo de interfaz gráfica para el sistema de cotizaciones.
Gestiona toda la interfaz y las interacciones del usuario,
utilizando la lógica de negocio del módulo logica_cotizador.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from logica_cotizador import GestorCotizaciones, OPENPYXL_DISPONIBLE

class CotizadorApp:
    """
    Clase principal de la interfaz gráfica del sistema de cotizaciones.
    Crea y gestiona todos los elementos visuales y las interacciones del usuario,
    delegando la lógica de negocio a un objeto GestorCotizaciones.
    """
    
    def __init__(self, root):
        """
        Inicializa la aplicación de cotizaciones para festivales.
        
        Args:
            root: Ventana principal de la aplicación
        """
        self.root = root
        self.root.title("Cotizador de Festivales")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Crear el gestor de lógica de negocio
        self.gestor = GestorCotizaciones()
        self.gestor.cargar_cotizaciones_iniciales()
        
        # Configurar el estilo
        self.configurar_estilo()
        
        # Crear el marco principal
        self.crear_interfaz()
        
        # Inicializar las listas
        self.actualizar_lista_disponibles()
        self.actualizar_lista_seleccionadas()
    
    def configurar_estilo(self):
        """Configura el estilo visual de la aplicación."""
        estilo = ttk.Style()
        estilo.theme_use('clam')  # Usar un tema moderno
        
        # Configurar estilos para los botones
        estilo.configure('TButton', font=('Arial', 10))
        estilo.configure('Accion.TButton', font=('Arial', 12, 'bold'))
        
        # Configurar estilos para las etiquetas
        estilo.configure('Titulo.TLabel', font=('Arial', 12, 'bold'))
        estilo.configure('Total.TLabel', font=('Arial', 12, 'bold'), foreground='blue')
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de la aplicación."""
        # Marco principal que contiene toda la interfaz
        marco_principal = ttk.Frame(self.root, padding=10)
        marco_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título de la aplicación
        titulo_app = ttk.Label(marco_principal, text="Sistema de Cotizaciones para Festivales", font=('Arial', 16, 'bold'))
        titulo_app.pack(pady=10)
        
        # Marco para contener las dos columnas y los botones centrales
        marco_columnas = ttk.Frame(marco_principal)
        marco_columnas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # ----- COLUMNA IZQUIERDA: DISPONIBLES -----
        marco_disponibles = ttk.LabelFrame(marco_columnas, text="Cotizaciones Disponibles", padding=10)
        marco_disponibles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Filtro por categoría
        marco_filtro = ttk.Frame(marco_disponibles)
        marco_filtro.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(marco_filtro, text="Filtrar por categoría:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Obtener categorías únicas de las cotizaciones
        categorias = self.gestor.obtener_categorias_unicas()
        categorias.insert(0, "Todas")  # Añadir opción para mostrar todas
        
        self.combo_categoria = ttk.Combobox(marco_filtro, values=categorias, state="readonly")
        self.combo_categoria.current(0)  # Seleccionar "Todas" por defecto
        self.combo_categoria.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_categoria.bind("<<ComboboxSelected>>", self.filtrar_por_categoria)
        
        # Lista de cotizaciones disponibles
        marco_lista_disponibles = ttk.Frame(marco_disponibles)
        marco_lista_disponibles.pack(fill=tk.BOTH, expand=True)
        
        columnas_disponibles = ('nombre', 'precio', 'categoria')
        self.tree_disponibles = ttk.Treeview(marco_lista_disponibles, columns=columnas_disponibles, show='headings', selectmode='browse')
        
        # Configurar las columnas
        self.tree_disponibles.heading('nombre', text='Descripción')
        self.tree_disponibles.heading('precio', text='Precio (CRC)')
        self.tree_disponibles.heading('categoria', text='Categoría')
        
        self.tree_disponibles.column('nombre', width=150)
        self.tree_disponibles.column('precio', width=80, anchor=tk.E)
        self.tree_disponibles.column('categoria', width=100)
        
        # Añadir scrollbars
        scroll_y_disponibles = ttk.Scrollbar(marco_lista_disponibles, orient=tk.VERTICAL, command=self.tree_disponibles.yview)
        self.tree_disponibles.configure(yscrollcommand=scroll_y_disponibles.set)
        
        self.tree_disponibles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y_disponibles.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botón para añadir nueva cotización
        btn_anadir_cotizacion = ttk.Button(
            marco_disponibles,
            text="Añadir Cotización",
            command=self.mostrar_dialog_nueva_cotizacion
        )
        btn_anadir_cotizacion.pack(pady=(10, 0), anchor=tk.W)

        # Botón para eliminar cotización
        btn_eliminar_cotizacion = ttk.Button(
            marco_disponibles,
            text="Eliminar Cotización",
            command=self.eliminar_cotizacion
        )
        btn_eliminar_cotizacion.pack(pady=(5, 0), anchor=tk.W)
        
        # ----- BOTONES CENTRALES -----
        marco_botones = ttk.Frame(marco_columnas, padding=10)
        marco_botones.pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Espacio superior para centrar los botones verticalmente
        ttk.Frame(marco_botones).pack(expand=True)
        
        # Botón para agregar a la cotización
        self.btn_agregar = ttk.Button(
            marco_botones, 
            text="→", 
            style='Accion.TButton',
            width=3,
            command=self.agregar_a_seleccionadas
        )
        self.btn_agregar.pack(pady=5)
        
        # Botón para quitar de la cotización
        self.btn_quitar = ttk.Button(
            marco_botones, 
            text="←", 
            style='Accion.TButton',
            width=3,
            command=self.quitar_de_seleccionadas
        )
        self.btn_quitar.pack(pady=5)
        
        # Espacio inferior para centrar los botones verticalmente
        ttk.Frame(marco_botones).pack(expand=True)
        
        # ----- COLUMNA DERECHA: SELECCIONADAS -----
        marco_seleccionadas = ttk.LabelFrame(marco_columnas, text="Cotización Actual", padding=10)
        marco_seleccionadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Lista de cotizaciones seleccionadas
        marco_lista_seleccionadas = ttk.Frame(marco_seleccionadas)
        marco_lista_seleccionadas.pack(fill=tk.BOTH, expand=True)
        
        columnas_seleccionadas = ('nombre', 'precio', 'categoria', 'comentario')
        self.tree_seleccionadas = ttk.Treeview(marco_lista_seleccionadas, columns=columnas_seleccionadas, show='headings', selectmode='browse')
        
        # Configurar las columnas
        self.tree_seleccionadas.heading('nombre', text='Descripción')
        self.tree_seleccionadas.heading('precio', text='Precio (CRC)')
        self.tree_seleccionadas.heading('categoria', text='Categoría')
        self.tree_seleccionadas.heading('comentario', text='Comentario')
        
        self.tree_seleccionadas.column('nombre', width=150)
        self.tree_seleccionadas.column('precio', width=80, anchor=tk.E)
        self.tree_seleccionadas.column('categoria', width=100)
        self.tree_seleccionadas.column('comentario', width=120)

        # Para cotizaciones disponibles:
        self.tree_disponibles.bind("<Double-1>", self.editar_comentario_disponible)

        # Para cotizaciones seleccionadas:
        self.tree_seleccionadas.bind("<Double-1>", self.editar_comentario)

        # Añadir scrollbars
        scroll_y_seleccionadas = ttk.Scrollbar(marco_lista_seleccionadas, orient=tk.VERTICAL, command=self.tree_seleccionadas.yview)
        self.tree_seleccionadas.configure(yscrollcommand=scroll_y_seleccionadas.set)
        
        self.tree_seleccionadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll_y_seleccionadas.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Marco para el total
        marco_total = ttk.Frame(marco_seleccionadas)
        marco_total.pack(fill=tk.X, pady=(10, 0))
        
        # Etiqueta para el total
        self.lbl_total = ttk.Label(
            marco_total, 
            text="Total: 0.00 CRC", 
            style='Total.TLabel',
            anchor=tk.E
        )
        self.lbl_total.pack(side=tk.RIGHT)
        
        # ----- BOTONES DE ACCIÓN -----
        marco_acciones = ttk.Frame(marco_principal)
        marco_acciones.pack(fill=tk.X, pady=(10, 0))
        
        # Botón para generar Excel
        btn_guardar = ttk.Button(
            marco_acciones, 
            text="Guardar Cotización", 
            command=self.guardar_cotizacion
        )
        btn_guardar.pack(side=tk.RIGHT, padx=5)
        
        # Botón para nueva cotización
        btn_nueva = ttk.Button(
            marco_acciones, 
            text="Nueva Cotización", 
            command=self.nueva_cotizacion
        )
        btn_nueva.pack(side=tk.RIGHT, padx=5)
    
    def actualizar_lista_disponibles(self):
        """Actualiza la lista de cotizaciones disponibles en la interfaz."""
        # Limpiar lista actual
        for item in self.tree_disponibles.get_children():
            self.tree_disponibles.delete(item)
        
        # Insertar ítems actualizados
        for nombre, precio, categoria in self.gestor.cotizaciones_disponibles:
            precio_formateado = f"{precio:.2f}"
            self.tree_disponibles.insert('', tk.END, values=(nombre, precio_formateado, categoria))
    
    def actualizar_lista_seleccionadas(self):
        """Actualiza la lista de cotizaciones seleccionadas y recalcula el total."""
        # Limpiar lista actual
        for item in self.tree_seleccionadas.get_children():
            self.tree_seleccionadas.delete(item)
        
        # Insertar ítems actualizados
        for nombre, precio, categoria in self.gestor.cotizaciones_seleccionadas:
            precio_formateado = f"{precio:.2f}"
            item = (nombre, precio, categoria)
            comentario = self.gestor.obtener_comentario(item) if hasattr(self.gestor, 'obtener_comentario') else ""
            self.tree_seleccionadas.insert('', tk.END, values=(nombre, precio_formateado, categoria, comentario))
            # Configurar doble clic en cotizaciones seleccionadas para editar comentarios
            self.tree_seleccionadas.bind("<Double-1>", self.editar_comentario)
            # Configurar doble clic en cotizaciones disponibles para ver/editar comentarios
            self.tree_disponibles.bind("<Double-1>", self.editar_comentario_disponible)
        
        # Actualizar el total
        total = self.gestor.calcular_total()
        self.lbl_total.config(text=f"Total: {total:.2f} CRC")
    
    def filtrar_por_categoria(self, event=None):
        """
        Filtra las cotizaciones disponibles por categoría.
        
        Args:
            event: Evento del combobox (no usado directamente)
        """
        categoria_seleccionada = self.combo_categoria.get()
        self.gestor.filtrar_disponibles_por_categoria(categoria_seleccionada)
        self.actualizar_lista_disponibles()
    
    def agregar_a_seleccionadas(self):
        """Agrega el ítem seleccionado a la lista de cotizaciones seleccionadas."""
        seleccion = self.tree_disponibles.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Por favor, seleccione un ítem para agregar.")
            return
        
        # Obtener el ítem seleccionado
        item_id = seleccion[0]
        valores = self.tree_disponibles.item(item_id, 'values')
        
        # Convertir los valores al formato adecuado
        nombre = valores[0]
        precio = float(valores[1].replace('$', ''))
        categoria = valores[2]
        
        # Añadir a seleccionadas y quitar de disponibles usando el gestor
        item = (nombre, precio, categoria)
        self.gestor.agregar_a_seleccionadas(item)
        
        # Actualizar las listas
        self.actualizar_lista_disponibles()
        self.actualizar_lista_seleccionadas()
    
    def eliminar_cotizacion(self):
        """Elimina la cotización seleccionada de la lista de disponibles y del JSON."""
        # Verificar si hay alguna selección
        seleccion = self.tree_disponibles.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Por favor, seleccione una cotización para eliminar.")
            return
        
        # Obtener datos del ítem seleccionado
        item_id = seleccion[0]
        valores = self.tree_disponibles.item(item_id, 'values')
        
        # Convertir los valores al formato adecuado
        nombre = valores[0]
        precio = float(valores[1].replace('$', ''))
        categoria = valores[2]
        
        # Crear la tupla que representa al ítem
        item = (nombre, precio, categoria)
        
        # Pedir confirmación antes de eliminar
        if messagebox.askyesno("Confirmar eliminación", 
                            f"¿Está seguro de eliminar la cotización '{nombre}'?\n\n"
                            f"Esta acción no se puede deshacer."):
            
            # Eliminar usando el gestor de lógica
            if self.gestor.eliminar_cotizacion_base(item):
                # Actualizar listas
                self.filtrar_por_categoria()  # Esto actualizará la lista de disponibles
                
                messagebox.showinfo("Éxito", f"La cotización '{nombre}' ha sido eliminada.")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cotización.")

    
    def quitar_de_seleccionadas(self):
        """Quita el ítem seleccionado de la lista de cotizaciones seleccionadas."""
        seleccion = self.tree_seleccionadas.selection()
        if not seleccion:
            messagebox.showinfo("Información", "Por favor, seleccione un ítem para quitar.")
            return
        
        # Obtener el ítem seleccionado
        item_id = seleccion[0]
        valores = self.tree_seleccionadas.item(item_id, 'values')
        
        # Convertir los valores al formato adecuado
        nombre = valores[0]
        precio = float(valores[1].replace('$', ''))
        categoria = valores[2]
        
        # Quitar de seleccionadas y añadir a disponibles usando el gestor
        item = (nombre, precio, categoria)
        self.gestor.quitar_de_seleccionadas(item)
        
        # Actualizar las listas
        self.filtrar_por_categoria()  # Para respetar el filtro actual
        self.actualizar_lista_seleccionadas()
    
    def nueva_cotizacion(self):
        """Crea una nueva cotización, limpiando la lista de seleccionados."""
        if self.gestor.cotizaciones_seleccionadas:
            if messagebox.askyesno("Nueva Cotización", "¿Está seguro de iniciar una nueva cotización? Se perderán los datos actuales."):
                # Restaurar todas las cotizaciones a disponibles usando el gestor
                self.gestor.nueva_cotizacion()
                
                # Resetear el filtro
                self.combo_categoria.current(0)
                
                # Actualizar las listas
                self.actualizar_lista_disponibles()
                self.actualizar_lista_seleccionadas()
        else:
            messagebox.showinfo("Información", "Ya tiene una cotización vacía.")
    
    def guardar_cotizacion(self):
        """Gestiona el guardado de la cotización actual."""
        if not self.gestor.cotizaciones_seleccionadas:
            messagebox.showinfo("Información", "No hay items en la cotización actual.")
            return
        
        # Verificar si openpyxl está disponible
        if not OPENPYXL_DISPONIBLE:
            messagebox.showerror(
                "Error: Módulo no encontrado", 
                "El módulo 'openpyxl' no está instalado.\n\n" +
                "Por favor, instale el módulo usando:\n" +
                "pip install openpyxl\n\n" +
                "Y luego reinicie la aplicación."
            )
            return
        
        # Exportar a Excel usando el gestor
        resultado = self.gestor.exportar_a_excel()
        
        if resultado["exito"]:
            messagebox.showinfo(
                "Éxito",
                f"Cotización guardada exitosamente como:\n{resultado['archivo']}"
            )
        else:
            messagebox.showerror(
                "Error al guardar",
                f"Ocurrió un error al guardar el archivo:\n{resultado['mensaje']}"
            )
    
    def mostrar_dialog_nueva_cotizacion(self):
        """Muestra un diálogo para añadir una nueva cotización."""
        # Crear ventana emergente
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir Nueva Cotización")
        dialog.geometry("400x350")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Hace que la ventana sea modal
        dialog.grab_set()  # Bloquea la ventana principal hasta que esta se cierre
        
        # Centrar la ventana en la pantalla
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Marco del formulario
        marco_form = ttk.Frame(dialog, padding=20)
        marco_form.pack(fill=tk.BOTH, expand=True)
        
        # Obtener categorías existentes para el combobox
        categorias_existentes = self.gestor.obtener_categorias_unicas()
        
        # Campo: Descripción
        ttk.Label(marco_form, text="Descripción:").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        entrada_descripcion = ttk.Entry(marco_form, width=40)
        entrada_descripcion.grid(row=0, column=1, sticky=tk.W, pady=(0, 10))
        
        # Campo: Precio
        ttk.Label(marco_form, text="Precio (CRC):").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        entrada_precio = ttk.Entry(marco_form, width=15)
        entrada_precio.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        
        # Campo: Categoría (combobox con opción de entrada)
        ttk.Label(marco_form, text="Categoría:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        combo_categoria = ttk.Combobox(marco_form, values=categorias_existentes, width=38)
        combo_categoria.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # Campo: Comentario
        ttk.Label(marco_form, text="Comentario:").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        texto_comentario = tk.Text(marco_form, wrap=tk.WORD, width=38, height=4)
        texto_comentario.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # Texto informativo
        info_text = "* Puedes seleccionar una categoría existente o escribir una nueva."
        ttk.Label(marco_form, text=info_text, font=('Arial', 8), foreground='gray').grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Mensaje de error (inicialmente oculto)
        lbl_error = ttk.Label(marco_form, text="", foreground='red')
        lbl_error.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        # Marco para los botones
        marco_botones = ttk.Frame(marco_form)
        marco_botones.grid(row=6, column=0, columnspan=2, pady=(10, 0))
        
        def validar_y_guardar():
            """Valida los campos y guarda la nueva cotización si son válidos."""
            # Obtener valores ingresados
            descripcion = entrada_descripcion.get().strip()
            precio_str = entrada_precio.get().strip()
            categoria = combo_categoria.get().strip()
            comentario = texto_comentario.get('1.0', 'end-1c').strip()
            
            # Validar campos
            if not descripcion:
                lbl_error.config(text="Error: La descripción no puede estar vacía.")
                return
                
            if not precio_str:
                lbl_error.config(text="Error: El precio no puede estar vacío.")
                return
                
            if not categoria:
                lbl_error.config(text="Error: La categoría no puede estar vacía.")
                return
            
            # Validar que el precio sea un número positivo
            try:
                precio = float(precio_str)
                if precio <= 0:
                    lbl_error.config(text="Error: El precio debe ser un número positivo.")
                    return
            except ValueError:
                lbl_error.config(text="Error: El precio debe ser un número válido.")
                return
            
            # Si pasó todas las validaciones, agregar la cotización usando el gestor
            item = self.gestor.agregar_nueva_cotizacion_base(descripcion, precio, categoria)
            
            # Si hay comentario, establecerlo
            if comentario:
                self.gestor.establecer_comentario(item, comentario)
            
            # Actualizar el combobox de categorías si es una categoría nueva
            if categoria not in self.combo_categoria['values']:
                categorias = list(self.combo_categoria['values'])
                if "Todas" in categorias:
                    categorias.remove("Todas")
                categorias.append(categoria)
                categorias.sort()
                categorias.insert(0, "Todas")
                self.combo_categoria['values'] = categorias
            
            # Actualizar la interfaz
            self.actualizar_lista_disponibles()
            
            # Cerrar el diálogo
            dialog.destroy()
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Éxito", f"Cotización '{descripcion}' añadida correctamente.")
        
        # Botón: Aceptar
        btn_aceptar = ttk.Button(marco_botones, text="Aceptar", command=validar_y_guardar)
        btn_aceptar.pack(side=tk.RIGHT, padx=5)
        
        # Botón: Cancelar
        btn_cancelar = ttk.Button(marco_botones, text="Cancelar", command=dialog.destroy)
        btn_cancelar.pack(side=tk.RIGHT)









    def editar_comentario_disponible(self, event=None):
        """
        Muestra un diálogo para editar el comentario de una cotización disponible.
        
        Args:
            event: Evento de doble clic (no usado directamente)
        """
        # Verificar si hay alguna selección
        seleccion = self.tree_disponibles.selection()
        if not seleccion:
            return  # No hacer nada si no hay selección
        
        # Obtener datos del ítem seleccionado
        item_id = seleccion[0]
        valores = self.tree_disponibles.item(item_id, 'values')
        
        # Convertir los valores al formato adecuado
        nombre = valores[0]
        precio = float(valores[1].replace('$', ''))
        categoria = valores[2]
        
        # Crear la tupla que representa al ítem
        item = (nombre, precio, categoria)
        
        # Obtener el comentario actual
        comentario_actual = self.gestor.obtener_comentario(item)
        
        # Mostrar el diálogo para editar comentario
        self.mostrar_dialog_comentario(item, comentario_actual)

    def editar_comentario(self, event=None):
        """
        Muestra un diálogo para editar el comentario de una cotización seleccionada.
        
        Args:
            event: Evento de doble clic (no usado directamente)
        """
        # Verificar si hay alguna selección
        seleccion = self.tree_seleccionadas.selection()
        if not seleccion:
            return  # No hacer nada si no hay selección
        
        # Obtener datos del ítem seleccionado
        item_id = seleccion[0]
        valores = self.tree_seleccionadas.item(item_id, 'values')
        
        # Convertir los valores al formato adecuado
        nombre = valores[0]
        precio = float(valores[1].replace('$', ''))
        categoria = valores[2]
        
        # Crear la tupla que representa al ítem
        item = (nombre, precio, categoria)
        
        # Obtener el comentario actual
        comentario_actual = self.gestor.obtener_comentario(item)
        
        # Mostrar el diálogo para editar comentario
        self.mostrar_dialog_comentario(item, comentario_actual)
        
    
    def mostrar_dialog_comentario(self, item, comentario_actual=""):
        """
        Muestra un diálogo para editar el comentario de una cotización.
        
        Args:
            item: Tupla (nombre, precio, categoria) de la cotización
            comentario_actual: Comentario actual de la cotización
        """
        nombre, precio, categoria = item
        
        # Crear ventana emergente
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Comentario para: {nombre}")
        dialog.geometry("400x300")
        dialog.resizable(True, True)
        dialog.transient(self.root)  # Hace que la ventana sea modal
        dialog.grab_set()  # Bloquea la ventana principal hasta que esta se cierre
        
        # Centrar la ventana en la pantalla
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Marco del formulario
        marco_form = ttk.Frame(dialog, padding=20)
        marco_form.pack(fill=tk.BOTH, expand=True)
        
        # Información de la cotización
        info_text = f"Cotización: {nombre}\nPrecio: {precio:.2f} CRC\nCategoría: {categoria}"
        ttk.Label(marco_form, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=(0, 10))
        
        # Etiqueta para el comentario
        ttk.Label(marco_form, text="Comentario:").pack(anchor=tk.W)
        
        # Campo de texto para el comentario
        texto_comentario = tk.Text(marco_form, wrap=tk.WORD, width=40, height=8)
        texto_comentario.pack(fill=tk.BOTH, expand=True, pady=(5, 10))
        texto_comentario.insert('1.0', comentario_actual)
        
        # Marco para los botones
        marco_botones = ttk.Frame(marco_form)
        marco_botones.pack(fill=tk.X)
        
        def guardar_comentario():
            """Guarda el comentario y cierra el diálogo."""
            nuevo_comentario = texto_comentario.get('1.0', 'end-1c').strip()
            self.gestor.establecer_comentario(item, nuevo_comentario)
            
            # Actualizar la vista de las listas para mostrar el nuevo comentario
            self.actualizar_lista_disponibles()
            self.actualizar_lista_seleccionadas()
            
            dialog.destroy()
        
        # Botón: Guardar
        btn_guardar = ttk.Button(marco_botones, text="Guardar", command=guardar_comentario)
        btn_guardar.pack(side=tk.RIGHT, padx=5)
        
        # Botón: Cancelar
        btn_cancelar = ttk.Button(marco_botones, text="Cancelar", command=dialog.destroy)
        btn_cancelar.pack(side=tk.RIGHT)


    