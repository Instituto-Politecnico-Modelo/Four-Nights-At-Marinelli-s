extends Node
class_name MovementComponent
## MovementComponent
## Maneja el movimiento top-down de Charlie a partir del Input Map (WASD)
## y cambia la textura del sprite (derecha/izquierda) segun la direccion
## horizontal.

@export var cuerpo: CharacterBody2D
@export var sprite: Sprite2D
@export var textura_derecha: Texture2D
@export var textura_izquierda: Texture2D
@export var velocidad: float = 200.0


func _ready() -> void:
	if cuerpo == null:
		cuerpo = get_parent() as CharacterBody2D
	if sprite == null and cuerpo != null:
		sprite = cuerpo.get_node_or_null("Sprite") as Sprite2D


func _physics_process(_delta: float) -> void:
	if cuerpo == null:
		return
	var direccion := Input.get_vector("mover_izquierda", "mover_derecha", "mover_arriba", "mover_abajo")
	cuerpo.velocity = direccion * velocidad
	cuerpo.move_and_slide()
	_actualizar_orientacion(direccion)


func _actualizar_orientacion(direccion: Vector2) -> void:
	if sprite == null:
		return
	if direccion.x > 0.0:
		sprite.texture = textura_derecha
	elif direccion.x < 0.0:
		sprite.texture = textura_izquierda
