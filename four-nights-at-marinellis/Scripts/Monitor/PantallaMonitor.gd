extends CanvasLayer

const CODIGO: String = "1431"

@export var zona: ZonaMonitor
@export var jugador: CamaraPersonajeBase

@onready var inicio: Control = $Pantalla/Inicio
@onready var boton_clave: Button = $Pantalla/Inicio/BotonClave
@onready var campo: LineEdit = $Pantalla/Inicio/Campo
@onready var error: Label = $Pantalla/Inicio/Error
@onready var escritorio: Control = $Pantalla/Escritorio
@onready var boton_salir: Button = $Pantalla/Salir

var desbloqueado: bool = false


func _ready() -> void:
	visible = false
	zona.clickeado.connect(abrir)
	boton_clave.pressed.connect(mostrar_campo)
	campo.text_submitted.connect(comprobar)
	boton_salir.pressed.connect(cerrar)


func _input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("ui_cancel"):
		cerrar()
		get_viewport().set_input_as_handled()


func abrir() -> void:
	visible = true
	jugador.set_process_input(false)
	jugador.set_process(false)
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	inicio.visible = not desbloqueado
	escritorio.visible = desbloqueado
	boton_clave.visible = true
	campo.visible = false
	campo.clear()
	error.text = ""


func cerrar() -> void:
	visible = false
	jugador.set_process_input(true)
	jugador.set_process(true)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func mostrar_campo() -> void:
	boton_clave.visible = false
	campo.visible = true
	campo.grab_focus()


func comprobar(texto: String) -> void:
	if texto == CODIGO:
		desbloqueado = true
		inicio.visible = false
		escritorio.visible = true
	else:
		campo.clear()
		error.text = "Incorrect password"
