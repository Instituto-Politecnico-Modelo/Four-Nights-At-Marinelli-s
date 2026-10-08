extends Node
class_name HidingComponent
## HidingComponent
## Permite a Charlie esconderse/salir con una tecla propia ("esconderse"),
## siempre que una Computadora este actualmente enfocada (en rango del
## InteractorComponent) - los escondites de la Fase 1 son los mismos
## escritorios que tienen las pistas. No depende de la accion generica
## "interactuar". Mientras esta escondido: el sprite se oculta y el
## MovementComponent hermano deja de procesar fisica, asi Charlie queda
## inmovil hasta salir.

@export var cuerpo: CharacterBody2D
@export var sprite: Sprite2D
@export var movimiento: MovementComponent

var esta_escondido: bool = false
var _escondite_en_rango: Computadora = null


func _ready() -> void:
	if cuerpo == null:
		cuerpo = get_parent() as CharacterBody2D
	if sprite == null and cuerpo != null:
		sprite = cuerpo.get_node_or_null("Sprite") as Sprite2D
	if movimiento == null and cuerpo != null:
		movimiento = cuerpo.get_node_or_null("MovementComponent") as MovementComponent

	SignalBus.interactuable_enfocado.connect(_on_enfocado)
	SignalBus.interactuable_desenfocado.connect(_on_desenfocado)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("esconderse") and _escondite_en_rango != null:
		_alternar()


func _on_enfocado(interactuable: Node) -> void:
	var duenio: Node = interactuable.get_parent()
	if duenio is Computadora:
		_escondite_en_rango = duenio


func _on_desenfocado(interactuable: Node) -> void:
	var duenio: Node = interactuable.get_parent()
	if duenio == _escondite_en_rango:
		_escondite_en_rango = null


func _alternar() -> void:
	esta_escondido = not esta_escondido
	SignalBus.charlie_escondido.emit(esta_escondido)

	if sprite:
		sprite.visible = not esta_escondido

	if movimiento:
		movimiento.set_physics_process(not esta_escondido)
