extends CanvasLayer

const CODIGO: String = "1409"

@export var zona: ZonaMonitor
@export var jugador: CamaraPersonajeBase

@onready var inicio: Control = $Pantalla/Inicio
@onready var boton_clave: Button = $Pantalla/Inicio/BotonClave
@onready var campo: LineEdit = $Pantalla/Inicio/Campo
@onready var error: Label = $Pantalla/Inicio/Error
@onready var escritorio: Control = $Pantalla/Escritorio
@onready var boton_camaras: Button = $Pantalla/Escritorio/Iconos/Camaras
@onready var camaras: Control = $Pantalla/Camaras
@onready var camara_vista: Camera3D = $Pantalla/Camaras/Vista/Mundo/Camara
@onready var botones: Array[Button] = [$Pantalla/Camaras/Lateral/Cruz/Norte, $Pantalla/Camaras/Lateral/Cruz/Oeste, $Pantalla/Camaras/Lateral/Cruz/Sur, $Pantalla/Camaras/Lateral/Cruz/Este]
@onready var boton_volver: Button = $Pantalla/Camaras/Lateral/Volver
@onready var boton_salir: Button = $Pantalla/Salir

var desbloqueado: bool = false
var puntos: Array[Node] = []


func _ready() -> void:
	visible = false
	zona.clickeado.connect(abrir)
	boton_clave.pressed.connect(mostrar_campo)
	campo.text_submitted.connect(comprobar)
	boton_salir.pressed.connect(cerrar)
	boton_camaras.pressed.connect(abrir_camaras)
	boton_volver.pressed.connect(cerrar_camaras)
	puntos = get_tree().get_nodes_in_group("camaras_seguridad")
	for i in botones.size():
		if i < puntos.size():
			botones[i].pressed.connect(seleccionar.bind(i))
		else:
			botones[i].disabled = true


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
	camaras.visible = false
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


func abrir_camaras() -> void:
	escritorio.visible = false
	camaras.visible = true
	if puntos.size() > 0:
		seleccionar(0)


func cerrar_camaras() -> void:
	camaras.visible = false
	escritorio.visible = true


func seleccionar(indice: int) -> void:
	var punto: Node3D = puntos[indice]
	camara_vista.global_transform = Transform3D(punto.global_basis.orthonormalized(), punto.global_position)
