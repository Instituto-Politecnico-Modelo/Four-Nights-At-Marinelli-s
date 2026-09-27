class_name CamaraPersonajeBase
extends Node3D

@export var pivote: Node3D
@export var camara: Camera3D
@export var sensibilidad: float = 0.15
@export var giro_minimo: float = -70.0
@export var giro_maximo: float = 70.0
@export var inclinacion_minima: float = -40.0
@export var inclinacion_maxima: float = 40.0

var movimiento: Vector2 = Vector2.ZERO


func _ready() -> void:
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _input(event: InputEvent) -> void:
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		movimiento += event.relative * sensibilidad
	if event.is_action_pressed("ui_cancel"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	if event is InputEventMouseButton and event.pressed:
		Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _process(_delta: float) -> void:
	var nodo_giro: Node3D = self
	var inclinacion: float = 0.0
	if pivote:
		nodo_giro = pivote
	nodo_giro.rotation_degrees.y = clamp(nodo_giro.rotation_degrees.y - movimiento.x, giro_minimo, giro_maximo)

	if camara:
		camara.rotation_degrees.x = clamp(camara.rotation_degrees.x - movimiento.y, inclinacion_minima, inclinacion_maxima)
		inclinacion = camara.rotation_degrees.x

	_al_rotar(nodo_giro.rotation_degrees.y, inclinacion)
	movimiento = Vector2.ZERO


func _al_rotar(_horizontal: float, _vertical: float) -> void:
	pass
