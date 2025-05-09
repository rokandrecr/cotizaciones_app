"""
Módulo de interfaz gráfica para el sistema de cotizaciones.
Gestiona toda la interfaz y las interacciones del usuario,
utilizando la lógica de negocio del módulo logica_cotizador.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import platform
from logica_cotizador import GestorCotizaciones, OPENPYXL_DISPONIBLE

class Tooltip:
    """
    Clase para crear tooltips en widgets de Tkinter.
    Muestra información contextual al mantener el cursor sobre un elemento.
    """
    def __init__(self, widget, text):
        """
        Inicializa un tooltip para un widget.
        
        Args:
            widget: Widget al que se le asignará el tooltip
            text: Texto a mostrar en el tooltip
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        """Muestra el tooltip cerca del cursor."""
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Crear ventana de tooltip
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)  # Sin decoración de ventana
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Marco para el contenido
        frame = ttk.Frame(self.tooltip, style="Tooltip.TFrame", padding=4)
        frame.pack(fill="both", expand=True)
        
        # Etiqueta con el texto
        label = ttk.Label(frame, text=self.text, style="Tooltip.TLabel", 
                          wraplength=250, justify="left")
        label.pack()
        
        # Programar la desaparición automática después de 3 segundos
        self.widget.after(3000, self.hide_tooltip)
    
    def hide_tooltip(self, event=None):
        """Oculta el tooltip si está visible."""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

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
        self.root.title("Cotizador de We Love Flowers")
        self.root.geometry("1000x650")
        self.root.minsize(900, 600)
        
        # Variable para mensajes de estado
        self.status_message = tk.StringVar()
        self.status_message.set("Listo")
        
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
        
        # Detectar sistema operativo para elegir el tema más adecuado
        sistema = platform.system()
        if sistema == "Windows":
            # En Windows, 'vista' suele verse mejor
            estilo.theme_use('vista')
        elif sistema == "Darwin":  # macOS
            # En macOS, el tema por defecto suele ser adecuado
            pass
        else:  # Linux y otros
            # En Linux, 'alt' suele funcionar bien
            try:
                estilo.theme_use('alt')
            except tk.TclError:
                # Si 'alt' no está disponible, usar el tema predeterminado
                pass
        
        # Colores principales (esquema moderno)
        COLOR_BG = "#f5f5f7"           # Fondo claro
        COLOR_ACCENT = "#0071e3"       # Azul acento
        COLOR_ACCENT_HOVER = "#0077ed" # Azul acento hover
        COLOR_TEXT = "#1d1d1f"         # Texto casi negro
        COLOR_SECONDARY = "#86868b"    # Gris secundario
        COLOR_SUCCESS = "#34c759"      # Verde éxito
        
        # Determinar la fuente del sistema según la plataforma
        if sistema == "Windows":
            fuente_sistema = "Segoe UI"
        elif sistema == "Darwin":  # macOS
            fuente_sistema = "SF Pro Text"
        else:  # Linux y otros
            fuente_sistema = "DejaVu Sans"
        
        # Configurar estilos para los marcos
        estilo.configure('TFrame', background=COLOR_BG)
        estilo.configure('Main.TFrame', background=COLOR_BG)
        
        # Configurar estilos para etiquetas
        estilo.configure('TLabel', 
                        font=(fuente_sistema, 10),
                        background=COLOR_BG, 
                        foreground=COLOR_TEXT)
        
        estilo.configure('Title.TLabel', 
                        font=(fuente_sistema, 16, 'bold'),
                        padding=(0, 10),
                        background=COLOR_BG, 
                        foreground=COLOR_TEXT)
        
        estilo.configure('Header.TLabel', 
                        font=(fuente_sistema, 12, 'bold'),
                        background=COLOR_BG, 
                        foreground=COLOR_TEXT)
        
        estilo.configure('Status.TLabel', 
                        font=(fuente_sistema, 9),
                        background="#e5e5e7", 
                        foreground=COLOR_SECONDARY,
                        padding=(10, 5))
        
        estilo.configure('Total.TLabel', 
                        font=(fuente_sistema, 12, 'bold'),
                        background=COLOR_BG, 
                        foreground=COLOR_ACCENT)
        
        # Configurar estilos para botones
        estilo.configure('TButton', 
                        font=(fuente_sistema, 10),
                        padding=(10, 5))
                        
        estilo.configure('Accent.TButton', 
                        font=(fuente_sistema, 10, 'bold'),
                        background=COLOR_ACCENT,
                        foreground=COLOR_TEXT)
        # Mapeo de colores para efectos al pasar el ratón sobre botones
        estilo.map('Accent.TButton',
                background=[('active', COLOR_ACCENT_HOVER), ('pressed', COLOR_ACCENT_HOVER)],
                foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Estilo para botones de acción (→/←)
        estilo.configure('Action.TButton', 
                        font=(fuente_sistema, 12, 'bold'),
                        padding=(6, 8),
                        width=3)
        
        # Mapeo de colores para efectos al pasar el ratón sobre botones
        estilo.map('Accent.TButton',
                background=[('active', COLOR_ACCENT_HOVER), ('pressed', COLOR_ACCENT_HOVER)],
                foreground=[('active', 'white'), ('pressed', 'white')])
        
        # Configurar estilos para los combobox
        estilo.configure('TCombobox', 
                        font=(fuente_sistema, 10),
                        padding=(5, 2))
        
        # Configurar Treeview (listas)
        estilo.configure('Treeview', 
                        font=(fuente_sistema, 10),
                        rowheight=25,
                        background="white",
                        fieldbackground="white",
                        foreground=COLOR_TEXT)
        
        estilo.configure('Treeview.Heading', 
                        font=(fuente_sistema, 10, 'bold'),
                        background=COLOR_BG,
                        foreground=COLOR_TEXT)
        
        # Configurar colores alternos para filas en Treeview
        estilo.map('Treeview', 
                background=[('selected', COLOR_ACCENT)],
                foreground=[('selected', 'white')])
        
        # Estilo para LabelFrame
        estilo.configure('TLabelframe', 
                        background=COLOR_BG)
        
        estilo.configure('TLabelframe.Label', 
                        font=(fuente_sistema, 11, 'bold'),
                        background=COLOR_BG,
                        foreground=COLOR_TEXT)
        
        # Estilo para tooltip
        estilo.configure('Tooltip.TFrame',
                        background="#333333")
        
        estilo.configure('Tooltip.TLabel',
                        font=(fuente_sistema, 9),
                        background="#333333",
                        foreground="white")
    
    def crear_interfaz(self):
        """Crea la interfaz gráfica de la aplicación."""
        # Marco principal que contiene toda la interfaz
        marco_principal = ttk.Frame(self.root, style="Main.TFrame")
        marco_principal.pack(fill=tk.BOTH, expand=True)
        
        # Título de la aplicación
        titulo_app = ttk.Label(marco_principal, 
                            text="Sistema de Cotizaciones para Festivales", 
                            style="Title.TLabel")
        titulo_app.pack(pady=(15, 5))
        
        # Separador debajo del título
        separador_titulo = ttk.Separator(marco_principal, orient=tk.HORIZONTAL)
        separador_titulo.pack(fill=tk.X, padx=20, pady=10)
        
        # Marco para contener las dos columnas y los botones centrales
        marco_columnas = ttk.Frame(marco_principal)
        marco_columnas.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)
        
        # ----- COLUMNA IZQUIERDA: DISPONIBLES -----
        marco_disponibles = ttk.LabelFrame(marco_columnas, text="Cotizaciones Disponibles", padding=10)
        marco_disponibles.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Filtro por categoría
        marco_filtro = ttk.Frame(marco_disponibles)
        marco_filtro.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(marco_filtro, text="Filtrar por categoría:").pack(side=tk.LEFT, padx=(0, 5))
        
        # Obtener categorías únicas de las cotizaciones
        categorias = self.gestor.obtener_categorias_unicas()
        categorias.insert(0, "Todas")  # Añadir opción para mostrar todas
        
        self.combo_categoria = ttk.Combobox(marco_filtro, values=categorias, state="readonly")
        self.combo_categoria.current(0)  # Seleccionar "Todas" por defecto
        self.combo_categoria.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.combo_categoria.bind("<<ComboboxSelected>>", self.filtrar_por_categoria)
        
        # Crear tooltip para el combobox de categorías
        Tooltip(self.combo_categoria, "Filtrar las cotizaciones disponibles por categoría")
        
        # Separador debajo del filtro
        separador_filtro = ttk.Separator(marco_disponibles, orient=tk.HORIZONTAL)
        separador_filtro.pack(fill=tk.X, pady=5)
        
        # Lista de cotizaciones disponibles
        marco_lista_disponibles = ttk.Frame(marco_disponibles)
        marco_lista_disponibles.pack(fill=tk.BOTH, expand=True)
        
        columnas_disponibles = ('nombre', 'precio', 'categoria')
        self.tree_disponibles = ttk.Treeview(marco_lista_disponibles, columns=columnas_disponibles, 
                                            show='headings', selectmode='browse')
        
        # Configurar las columnas
        self.tree_disponibles.heading('nombre', text='Descripción')
        self.tree_disponibles.heading('precio', text='Precio (CRC)')
        self.tree_disponibles.heading('categoria', text='Categoría')
        
        self.tree_disponibles.column('nombre', width=200, minwidth=150)
        self.tree_disponibles.column('precio', width=100, minwidth=80, anchor=tk.E)
        self.tree_disponibles.column('categoria', width=120, minwidth=100)
        
        # Configurar colores alternos para filas
        self.tree_disponibles.tag_configure('odd', background='#f6f6f6')
        self.tree_disponibles.tag_configure('even', background='white')
        
        # Añadir scrollbars
        scroll_y_disponibles = ttk.Scrollbar(marco_lista_disponibles, orient=tk.VERTICAL, 
                                            command=self.tree_disponibles.yview)
        scroll_x_disponibles = ttk.Scrollbar(marco_lista_disponibles, orient=tk.HORIZONTAL, 
                                            command=self.tree_disponibles.xview)
        
        self.tree_disponibles.configure(yscrollcommand=scroll_y_disponibles.set,
                                      xscrollcommand=scroll_x_disponibles.set)
        
        # Ubicar los elementos en la cuadrícula
        self.tree_disponibles.grid(row=0, column=0, sticky='nsew')
        scroll_y_disponibles.grid(row=0, column=1, sticky='ns')
        scroll_x_disponibles.grid(row=1, column=0, sticky='ew')
        
        # Configurar expansión de filas y columnas
        marco_lista_disponibles.rowconfigure(0, weight=1)
        marco_lista_disponibles.columnconfigure(0, weight=1)
        
        # Marco para botones de acción disponibles
        marco_botones_disponibles = ttk.Frame(marco_disponibles)
        marco_botones_disponibles.pack(fill=tk.X, pady=(10, 0))
        
        # Botón para añadir nueva cotización
        btn_anadir_cotizacion = ttk.Button(
            marco_botones_disponibles,
            text="Añadir Cotización",
            command=self.mostrar_dialog_nueva_cotizacion,
            style="TButton"
        )
        btn_anadir_cotizacion.pack(side=tk.LEFT, padx=(0, 5))
        Tooltip(btn_anadir_cotizacion, "Crear una nueva cotización en el sistema")
        
        # Botón para eliminar cotización
        btn_eliminar_cotizacion = ttk.Button(
            marco_botones_disponibles,
            text="Eliminar Cotización",
            command=self.eliminar_cotizacion,
            style="TButton"
        )
        btn_eliminar_cotizacion.pack(side=tk.LEFT)
        Tooltip(btn_eliminar_cotizacion, "Eliminar la cotización seleccionada del sistema")
        
        # ----- BOTONES CENTRALES -----
        marco_botones = ttk.Frame(marco_columnas, padding=5)
        marco_botones.pack(side=tk.LEFT, fill=tk.Y)
        
        # Espacio para centrar visualmente
        ttk.Frame(marco_botones, height=50).pack()
        
        # Botón para agregar a la cotización
        self.btn_agregar = ttk.Button(
            marco_botones, 
            text="→", 
            style='Action.TButton',
            command=self.agregar_a_seleccionadas
        )
        self.btn_agregar.pack(pady=5)
        Tooltip(self.btn_agregar, "Agregar el ítem seleccionado a la cotización actual")
        
        # Botón para quitar de la cotización
        self.btn_quitar = ttk.Button(
            marco_botones, 
            text="←", 
            style='Action.TButton',
            command=self.quitar_de_seleccionadas
        )
        self.btn_quitar.pack(pady=5)
        Tooltip(self.btn_quitar, "Quitar el ítem seleccionado de la cotización actual")
        
        # ----- COLUMNA DERECHA: SELECCIONADAS -----
        marco_seleccionadas = ttk.LabelFrame(marco_columnas, text="Cotización Actual", padding=10)
        marco_seleccionadas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Lista de cotizaciones seleccionadas
        marco_lista_seleccionadas = ttk.Frame(marco_seleccionadas)
        marco_lista_seleccionadas.pack(fill=tk.BOTH, expand=True)
        
        columnas_seleccionadas = ('nombre', 'precio', 'categoria', 'comentario')
        self.tree_seleccionadas = ttk.Treeview(marco_lista_seleccionadas, columns=columnas_seleccionadas, 
                                            show='headings', selectmode='browse')
        
        # Configurar las columnas
        self.tree_seleccionadas.heading('nombre', text='Descripción')
        self.tree_seleccionadas.heading('precio', text='Precio (CRC)')
        self.tree_seleccionadas.heading('categoria', text='Categoría')
        self.tree_seleccionadas.heading('comentario', text='Comentario')
        
        self.tree_seleccionadas.column('nombre', width=180, minwidth=150)
        self.tree_seleccionadas.column('precio', width=100, minwidth=80, anchor=tk.E)
        self.tree_seleccionadas.column('categoria', width=120, minwidth=100)
        self.tree_seleccionadas.column('comentario', width=150, minwidth=120)

        # Configurar colores alternos para filas
        self.tree_seleccionadas.tag_configure('odd', background='#f6f6f6')
        self.tree_seleccionadas.tag_configure('even', background='white')
        
        # Para cotizaciones disponibles:
        self.tree_disponibles.bind("<Double-1>", self.editar_comentario_disponible)
        self.tree_disponibles.bind("<Return>", self.agregar_a_seleccionadas)

        # Para cotizaciones seleccionadas:
        self.tree_seleccionadas.bind("<Double-1>", self.editar_comentario)
        self.tree_seleccionadas.bind("<Return>", self.quitar_de_seleccionadas)
        self.tree_seleccionadas.bind("<Delete>", self.quitar_de_seleccionadas)

        # Añadir scrollbars
        scroll_y_seleccionadas = ttk.Scrollbar(marco_lista_seleccionadas, orient=tk.VERTICAL, 
                                            command=self.tree_seleccionadas.yview)
        scroll_x_seleccionadas = ttk.Scrollbar(marco_lista_seleccionadas, orient=tk.HORIZONTAL, 
                                            command=self.tree_seleccionadas.xview)
        
        self.tree_seleccionadas.configure(yscrollcommand=scroll_y_seleccionadas.set,
                                       xscrollcommand=scroll_x_seleccionadas.set)
        
        # Ubicar los elementos en la cuadrícula
        self.tree_seleccionadas.grid(row=0, column=0, sticky='nsew')
        scroll_y_seleccionadas.grid(row=0, column=1, sticky='ns')
        scroll_x_seleccionadas.grid(row=1, column=0, sticky='ew')
        
        # Configurar expansión de filas y columnas
        marco_lista_seleccionadas.rowconfigure(0, weight=1)
        marco_lista_seleccionadas.columnconfigure(0, weight=1)
        
        # Separador encima del total
        separador_total = ttk.Separator(marco_seleccionadas, orient=tk.HORIZONTAL)
        separador_total.pack(fill=tk.X, pady=10)
        
        # Marco para el total
        marco_total = ttk.Frame(marco_seleccionadas)
        marco_total.pack(fill=tk.X)
        
        # Etiqueta para el total
        self.lbl_total = ttk.Label(
            marco_total, 
            text="Total: 0.00 CRC", 
            style='Total.TLabel',
            anchor=tk.E
        )
        self.lbl_total.pack(side=tk.RIGHT)
        
        # ----- BOTONES DE ACCIÓN -----
        marco_acciones = ttk.Frame(marco_principal, padding=(20, 10))
        marco_acciones.pack(fill=tk.X, pady=10)
        
        # Botón para generar Excel
        btn_guardar = ttk.Button(
            marco_acciones, 
            text="Guardar Cotización", 
            style="Accent.TButton",
            command=self.guardar_cotizacion
        )
        btn_guardar.pack(side=tk.RIGHT, padx=5)
        Tooltip(btn_guardar, "Exportar la cotización actual a un archivo Excel")
        
        # Botón para nueva cotización
        btn_nueva = ttk.Button(
            marco_acciones, 
            text="Nueva Cotización", 
            command=self.nueva_cotizacion
        )
        btn_nueva.pack(side=tk.RIGHT, padx=5)
        Tooltip(btn_nueva, "Iniciar una nueva cotización (limpia la selección actual)")
        
        # ----- BARRA DE ESTADO -----
        self.barra_estado = ttk.Label(
            self.root,
            textvariable=self.status_message,
            style="Status.TLabel",
            anchor=tk.W
        )
        self.barra_estado.pack(side=tk.BOTTOM, fill=tk.X)
    
    def actualizar_lista_disponibles(self):
        """Actualiza la lista de cotizaciones disponibles en la interfaz."""
        # Limpiar lista actual
        for item in self.tree_disponibles.get_children():
            self.tree_disponibles.delete(item)
        
        # Insertar ítems actualizados
        for i, (nombre, precio, categoria) in enumerate(self.gestor.cotizaciones_disponibles):
            precio_formateado = f"{precio:.2f}"
            tag = 'even' if i % 2 == 0 else 'odd'  # Alternar colores
            self.tree_disponibles.insert('', tk.END, values=(nombre, precio_formateado, categoria), tags=(tag,))
            
        # Mostrar mensaje en la barra de estado
        self.status_message.set(f"Cotizaciones disponibles: {len(self.gestor.cotizaciones_disponibles)}")
    
    def actualizar_lista_seleccionadas(self):
        """Actualiza la lista de cotizaciones seleccionadas y recalcula el total."""
        # Limpiar lista actual
        for item in self.tree_seleccionadas.get_children():
            self.tree_seleccionadas.delete(item)
        
        # Insertar ítems actualizados
        for i, (nombre, precio, categoria) in enumerate(self.gestor.cotizaciones_seleccionadas):
            precio_formateado = f"{precio:.2f}"
            item = (nombre, precio, categoria)
            comentario = self.gestor.obtener_comentario(item) if hasattr(self.gestor, 'obtener_comentario') else ""
            tag = 'even' if i % 2 == 0 else 'odd'  # Alternar colores
            self.tree_seleccionadas.insert('', tk.END, values=(nombre, precio_formateado, categoria, comentario), tags=(tag,))
        
        # Actualizar el total
        total = self.gestor.calcular_total()
        self.lbl_total.config(text=f"Total: {total:.2f} CRC")
        
        # Mostrar mensaje en la barra de estado
        self.status_message.set(f"Ítems en la cotización actual: {len(self.gestor.cotizaciones_seleccionadas)}")
    
    def filtrar_por_categoria(self, event=None):
        """
        Filtra las cotizaciones disponibles por categoría.
        
        Args:
            event: Evento del combobox (no usado directamente)
        """
        categoria_seleccionada = self.combo_categoria.get()
        self.gestor.filtrar_disponibles_por_categoria(categoria_seleccionada)
        self.actualizar_lista_disponibles()
        
        # Actualizar mensaje de estado
        if categoria_seleccionada == "Todas":
            self.status_message.set(f"Mostrando todas las cotizaciones disponibles ({len(self.gestor.cotizaciones_disponibles)})")
        else:
            self.status_message.set(f"Filtrando por categoría: {categoria_seleccionada} ({len(self.gestor.cotizaciones_disponibles)} resultados)")
    
    def agregar_a_seleccionadas(self, event=None):
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
        # Eliminar posibles caracteres no numéricos (como $) y convertir a float
        precio = float(valores[1].replace('$', '').replace(',', ''))
        categoria = valores[2]
        
        # Añadir a seleccionadas y quitar de disponibles usando el gestor
        item = (nombre, precio, categoria)
        self.gestor.agregar_a_seleccionadas(item)
        
        # Actualizar las listas
        self.actualizar_lista_disponibles()
        self.actualizar_lista_seleccionadas()
        
        # Mensaje de estado
        self.status_message.set(f"Ítem agregado a la cotización: {nombre}")
    
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
        precio = float(valores[1].replace('$', '').replace(',', ''))
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
                
                # Mensaje de éxito
                messagebox.showinfo("Éxito", f"La cotización '{nombre}' ha sido eliminada.")
                self.status_message.set(f"Cotización eliminada: {nombre}")
            else:
                messagebox.showerror("Error", "No se pudo eliminar la cotización.")
                self.status_message.set("Error al eliminar la cotización")
    
    def quitar_de_seleccionadas(self, event=None):
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
        precio = float(valores[1].replace('$', '').replace(',', ''))
        categoria = valores[2]
        
        # Quitar de seleccionadas y añadir a disponibles usando el gestor
        item = (nombre, precio, categoria)
        self.gestor.quitar_de_seleccionadas(item)
        
        # Actualizar las listas
        self.filtrar_por_categoria()  # Para respetar el filtro actual
        self.actualizar_lista_seleccionadas()
        
        # Mensaje de estado
        self.status_message.set(f"Ítem quitado de la cotización: {nombre}")
    
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
                
                # Mensaje de estado
                self.status_message.set("Nueva cotización iniciada")
        else:
            messagebox.showinfo("Información", "Ya tiene una cotización vacía.")
            self.status_message.set("La cotización actual ya está vacía")
    
    def guardar_cotizacion(self):
        """Gestiona el guardado de la cotización actual."""
        if not self.gestor.cotizaciones_seleccionadas:
            messagebox.showinfo("Información", "No hay ítems en la cotización actual.")
            self.status_message.set("No hay ítems para guardar")
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
            self.status_message.set("Error: módulo openpyxl no disponible")
            return
        
        # Exportar a Excel usando el gestor
        resultado = self.gestor.exportar_a_excel()
        
        if resultado["exito"]:
            messagebox.showinfo(
                "Éxito",
                f"Cotización guardada exitosamente como:\n{resultado['archivo']}"
            )
            self.status_message.set(f"Cotización guardada como: {resultado['archivo']}")
        else:
            messagebox.showerror(
                "Error al guardar",
                f"Ocurrió un error al guardar el archivo:\n{resultado['mensaje']}"
            )
            self.status_message.set("Error al guardar la cotización")
    
    def mostrar_dialog_nueva_cotizacion(self):
        """Muestra un diálogo para añadir una nueva cotización."""
        # Crear ventana emergente
        dialog = tk.Toplevel(self.root)
        dialog.title("Añadir Nueva Cotización")
        dialog.geometry("450x400")
        dialog.resizable(False, False)
        dialog.transient(self.root)  # Hace que la ventana sea modal
        dialog.grab_set()  # Bloquea la ventana principal hasta que esta se cierre
        
        # Centrar la ventana en la pantalla
        dialog.update_idletasks()
        x = self.root.winfo_x() + (self.root.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.root.winfo_y() + (self.root.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Marco del formulario con padding
        marco_form = ttk.Frame(dialog, padding=20)
        marco_form.pack(fill=tk.BOTH, expand=True)
        
        # Título del formulario
        titulo_form = ttk.Label(marco_form, text="Añadir Nueva Cotización", style="Header.TLabel")
        titulo_form.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 15))
        
        # Obtener categorías existentes para el combobox
        categorias_existentes = self.gestor.obtener_categorias_unicas()
        
        # Campo: Descripción
        ttk.Label(marco_form, text="Descripción:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        entrada_descripcion = ttk.Entry(marco_form, width=40)
        entrada_descripcion.grid(row=1, column=1, sticky=tk.W, pady=(0, 10))
        entrada_descripcion.focus_set()  # Poner el foco inicial aquí
        
        # Campo: Precio
        ttk.Label(marco_form, text="Precio (CRC):").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        entrada_precio = ttk.Entry(marco_form, width=15)
        entrada_precio.grid(row=2, column=1, sticky=tk.W, pady=(0, 10))
        
        # Campo: Categoría (combobox con opción de entrada)
        ttk.Label(marco_form, text="Categoría:").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        combo_categoria = ttk.Combobox(marco_form, values=categorias_existentes, width=38)
        combo_categoria.grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        # Campo: Comentario
        ttk.Label(marco_form, text="Comentario:").grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        texto_comentario = tk.Text(marco_form, wrap=tk.WORD, width=38, height=5)
        texto_comentario.grid(row=4, column=1, sticky=tk.W, pady=(0, 10))
        
        # Texto informativo
        info_text = "* Puedes seleccionar una categoría existente o escribir una nueva."
        ttk.Label(marco_form, text=info_text, font=('Arial', 8), foreground='gray').grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Mensaje de error (inicialmente oculto)
        lbl_error = ttk.Label(marco_form, text="", foreground='red')
        lbl_error.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=(5, 10))
        
        # Separador antes de los botones
        separador = ttk.Separator(marco_form, orient=tk.HORIZONTAL)
        separador.grid(row=7, column=0, columnspan=2, sticky=tk.EW, pady=10)
        
        # Marco para los botones
        marco_botones = ttk.Frame(marco_form)
        marco_botones.grid(row=8, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
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
                entrada_descripcion.focus_set()
                return
                
            if not precio_str:
                lbl_error.config(text="Error: El precio no puede estar vacío.")
                entrada_precio.focus_set()
                return
                
            if not categoria:
                lbl_error.config(text="Error: La categoría no puede estar vacía.")
                combo_categoria.focus_set()
                return
            
            # Validar que el precio sea un número positivo
            try:
                precio = float(precio_str.replace(',', '.'))  # Permitir comas como separador decimal
                if precio <= 0:
                    lbl_error.config(text="Error: El precio debe ser un número positivo.")
                    entrada_precio.focus_set()
                    return
            except ValueError:
                lbl_error.config(text="Error: El precio debe ser un número válido.")
                entrada_precio.focus_set()
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
            self.filtrar_por_categoria()  # Para mantener el filtro actual
            
            # Mensaje de estado
            self.status_message.set(f"Cotización '{descripcion}' añadida correctamente")
            
            # Cerrar el diálogo
            dialog.destroy()
            
            # Mostrar mensaje de confirmación
            messagebox.showinfo("Éxito", f"Cotización '{descripcion}' añadida correctamente.")
        
        # Botón: Cancelar
        btn_cancelar = ttk.Button(marco_botones, text="Cancelar", command=dialog.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón: Aceptar
        btn_aceptar = ttk.Button(marco_botones, text="Aceptar", style="Accent.TButton", command=validar_y_guardar)
        btn_aceptar.pack(side=tk.RIGHT)
        
        # Configurar comportamiento de teclas
        dialog.bind("<Return>", lambda event: validar_y_guardar())
        dialog.bind("<Escape>", lambda event: dialog.destroy())
    
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
        precio = float(valores[1].replace(',', ''))
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
        precio = float(valores[1].replace(',', ''))
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
        dialog.geometry("450x350")
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
        info_frame = ttk.Frame(marco_form)
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Título del diálogo
        ttk.Label(info_frame, text="Detalles de la Cotización", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 10))
        
        # Detalles con etiquetas de campo
        detalle_frame = ttk.Frame(info_frame)
        detalle_frame.pack(fill=tk.X)
        
        # Descripción
        ttk.Label(detalle_frame, text="Descripción:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Label(detalle_frame, text=nombre).grid(row=0, column=1, sticky=tk.W)
        
        # Precio
        ttk.Label(detalle_frame, text="Precio:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Label(detalle_frame, text=f"{precio:.2f} CRC").grid(row=1, column=1, sticky=tk.W)
        
        # Categoría
        ttk.Label(detalle_frame, text="Categoría:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, padx=(0, 5))
        ttk.Label(detalle_frame, text=categoria).grid(row=2, column=1, sticky=tk.W)
        
        # Separador
        separador = ttk.Separator(marco_form, orient=tk.HORIZONTAL)
        separador.pack(fill=tk.X, pady=10)
        
        # Etiqueta para el comentario
        ttk.Label(marco_form, text="Comentario:", style="Header.TLabel").pack(anchor=tk.W, pady=(0, 5))
        
        # Campo de texto para el comentario
        texto_comentario = tk.Text(marco_form, wrap=tk.WORD, width=45, height=8)
        texto_comentario.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        texto_comentario.insert('1.0', comentario_actual)
        texto_comentario.focus_set()  # Poner el foco inicial aquí
        
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
            
            # Actualizar mensaje de estado
            self.status_message.set(f"Comentario actualizado para: {nombre}")
            
            # Cerrar el diálogo
            dialog.destroy()
        
        # Botón: Cancelar
        btn_cancelar = ttk.Button(marco_botones, text="Cancelar", command=dialog.destroy)
        btn_cancelar.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Botón: Guardar
        btn_guardar = ttk.Button(marco_botones, text="Guardar", style="Accent.TButton", command=guardar_comentario)
        btn_guardar.pack(side=tk.RIGHT)
        
        # Configurar comportamiento de teclas
        dialog.bind("<Escape>", lambda event: dialog.destroy())
        dialog.bind("<Control-Return>", lambda event: guardar_comentario())  # Ctrl+Enter para guardar