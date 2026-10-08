extends Node
class_name DetectionComponent
## DetectionComponent
## Detecta por proximidad con AreaCaptura o por cono de vision (rango + angulo respecto a la
## direccion en la que Pruscino esta mirando, segun PatrolComponent) y
## confirma con un raycast que no haya nada en el medio (linea de vision
## libre). Si Charlie esta escondido (GameManager.charlie_escondido), nunca
## lo detecta. Al detectarlo, emite charlie_descubierto_por y charlie_atrapado
## una unica vez; GameManager y la UI gestionan la captura.

@export var cuerpo: CharacterBody2D
@export var patrulla: PatrolComponent
@export var rango_vision: float = 260.0
@export var angulo_vision_grados: float = 100.0

var _ya_detecto: bool = false
var _area_captura: Area2D


func _ready() -> void:
	if cuerpo == null:
		cuerpo = get_parent() as CharacterBody2D
	if patrulla == null and cuerpo != null:
		patrulla = cuerpo.get_node_or_null("PatrolComponent") as PatrolComponent
	if cuerpo != null:
		_area_captura = cuerpo.get_node_or_null("AreaCaptura") as Area2D


func _physics_process(_delta: float) -> void:
	if _ya_detecto or cuerpo == null:
		return

	if GameManager.charlie_escondido:
		return

	var charlie: Node2D = get_tree().get_first_node_in_group("charlie") as Node2D
	if charlie == null:
		return

	# Reevaluar mientras permanece dentro: salir del escondite tambien captura.
	if _area_captura != null and _area_captura.overlaps_body(charlie):
		if _hay_linea_de_vision(charlie):
			_capturar()
		return

	var hacia_charlie: Vector2 = charlie.global_position - cuerpo.global_position
	var distancia: float = hacia_charlie.length()

	if distancia > rango_vision:
		return

	var mirada: Vector2 = patrulla.direccion_mirada if patrulla != null else Vector2.RIGHT
	var angulo: float = rad_to_deg(mirada.angle_to(hacia_charlie))

	if abs(angulo) > angulo_vision_grados * 0.5:
		return

	if not _hay_linea_de_vision(charlie):
		return

	_capturar()


func _capturar() -> void:
	_ya_detecto = true
	SignalBus.charlie_descubierto_por.emit(cuerpo)
	SignalBus.charlie_atrapado.emit()


func _hay_linea_de_vision(charlie: Node2D) -> bool:
	var espacio: PhysicsDirectSpaceState2D = cuerpo.get_world_2d().direct_space_state
	var colision := charlie.get_node_or_null("CollisionShape2D") as CollisionShape2D
	var destino := colision.global_position if colision != null else charlie.global_position
	var parametros: PhysicsRayQueryParameters2D = PhysicsRayQueryParameters2D.create(
		cuerpo.global_position, destino
	)
	parametros.exclude = [cuerpo.get_rid()]

	var resultado: Dictionary = espacio.intersect_ray(parametros)

	if resultado.is_empty():
		return false

	return resultado.collider == charlie
