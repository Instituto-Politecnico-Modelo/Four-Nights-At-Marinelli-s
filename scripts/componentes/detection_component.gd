extends Node2D
class_name DetectionComponent

@export var cuerpo: CharacterBody2D
@export var patrulla: PatrolComponent
@export var rango_vision: float = 260.0
@export var angulo_vision_grados: float = 100.0
@export var _area_captura: Area2D
@export var mostrar_cono: bool = true
@export var color_borde: Color = Color.RED
@export var color_relleno: Color = Color(1.0, 0.0, 0.0, 0.2)
@export var segmentos_arco: int = 16

var _ya_detecto: bool = false
var _medio_angulo_rad: float
var _charlie: Node2D


func _ready() -> void:
	if cuerpo == null:
		cuerpo = get_parent() as CharacterBody2D
	if patrulla == null and cuerpo != null:
		patrulla = cuerpo.get_node_or_null("PatrolComponent") as PatrolComponent
	if cuerpo != null:
		_area_captura = cuerpo.get_node_or_null("AreaCaptura") as Area2D
	_charlie = get_tree().get_first_node_in_group("charlie") as Node2D
	_medio_angulo_rad = deg_to_rad(angulo_vision_grados / 2.0)


func _physics_process(_delta: float) -> void:
	if mostrar_cono:
		queue_redraw()

	if _ya_detecto or cuerpo == null or _charlie == null:
		return

	if GameManager.charlie_escondido:
		return

	if _area_captura != null and _area_captura.overlaps_body(_charlie):
		if _hay_linea_de_vision(_charlie):
			_capturar()
		return

	if is_in_cone() and _hay_linea_de_vision(_charlie):
		_capturar()


func _direccion() -> Vector2:
	return patrulla.direccion_mirada if patrulla != null else Vector2.RIGHT


func is_in_cone() -> bool:
	var hacia_charlie: Vector2 = _charlie.global_position - cuerpo.global_position
	if hacia_charlie.length() > rango_vision:
		return false
	return abs(_direccion().angle_to(hacia_charlie)) <= _medio_angulo_rad


func _draw() -> void:
	if not mostrar_cono:
		return
	var mirada: Vector2 = _direccion() * rango_vision
	var puntos := PackedVector2Array([Vector2.ZERO])
	for i in segmentos_arco + 1:
		var t: float = lerpf(-_medio_angulo_rad, _medio_angulo_rad, float(i) / segmentos_arco)
		puntos.append(to_local(global_position + mirada.rotated(t)))
	draw_colored_polygon(puntos, color_relleno)
	draw_line(Vector2.ZERO, puntos[1], color_borde, 3.0)
	draw_line(Vector2.ZERO, puntos[puntos.size() - 1], color_borde, 3.0)
	draw_polyline(puntos.slice(1), color_borde, 2.0)


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
