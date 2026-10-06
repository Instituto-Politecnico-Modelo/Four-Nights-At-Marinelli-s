extends Node
class_name PatrolComponent
## Patrulla estatica en el orden de los Marker2D de Puntos.
## Las posiciones se fijan al iniciar: no deben seguir al personaje.

@export var cuerpo: CharacterBody2D
@export var sprite: Sprite2D
@export var textura_derecha: Texture2D
@export var textura_izquierda: Texture2D
@export var velocidad: float = 120.0
@export var tiempo_espera: float = 2.0

var direccion_mirada: Vector2 = Vector2.RIGHT

var _puntos_resueltos: PackedVector2Array = []
var _indice_actual: int = 0
var _esperando: bool = false
var _tiempo_espera_restante: float = 0.0


func _ready() -> void:
	if cuerpo == null:
		cuerpo = get_parent() as CharacterBody2D
	if cuerpo == null:
		push_error("PatrolComponent necesita un CharacterBody2D.")
		return
	if sprite == null:
		sprite = cuerpo.get_node_or_null("Sprite") as Sprite2D

	var contenedor := cuerpo.get_node_or_null("Puntos") as Node2D
	if contenedor != null:
		# Mantener tambien los marcadores de depuracion quietos en el mundo.
		var transformacion_inicial := contenedor.global_transform
		contenedor.top_level = true
		contenedor.global_transform = transformacion_inicial
		for hijo in contenedor.get_children():
			if hijo is Marker2D:
				_puntos_resueltos.append(hijo.global_position)
	if _puntos_resueltos.is_empty():
		push_error("PatrolComponent necesita Marker2D dentro de Puntos.")


func _physics_process(delta: float) -> void:
	if cuerpo == null or _puntos_resueltos.is_empty() or delta <= 0.0:
		return

	if _esperando:
		cuerpo.velocity = Vector2.ZERO
		_tiempo_espera_restante -= delta
		if _tiempo_espera_restante <= 0.00001:
			_esperando = false
			_indice_actual = (_indice_actual + 1) % _puntos_resueltos.size()
		return

	var objetivo := _puntos_resueltos[_indice_actual]
	var desplazamiento := objetivo - cuerpo.global_position
	var distancia := desplazamiento.length()
	if distancia > 0.01:
		var direccion := desplazamiento / distancia
		# No pasarse del objetivo ni cortar esquinas por un radio de llegada.
		cuerpo.velocity = direccion * minf(velocidad, distancia / delta)
		cuerpo.move_and_slide()
		direccion_mirada = direccion
		_actualizar_orientacion(direccion)

	if cuerpo.global_position.distance_to(objetivo) <= 0.01:
		cuerpo.velocity = Vector2.ZERO
		_esperando = true
		_tiempo_espera_restante = tiempo_espera


func _actualizar_orientacion(direccion: Vector2) -> void:
	if sprite == null:
		return
	if direccion.x > 0.0:
		sprite.texture = textura_derecha
	elif direccion.x < 0.0:
		sprite.texture = textura_izquierda
