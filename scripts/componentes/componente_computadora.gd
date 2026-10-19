class_name ComponenteComputadora
extends Node

@export var interactuable: ComponenteInteractuable
@export var escritorio: EscritorioXP
@export var jugador: Node

var presionado_antes: bool = false


func _ready() -> void:
	add_to_group("computadoras")
	escritorio.hide()
	escritorio.apagado.connect(cerrar)
	var reloj: ComponenteRelojNoche = get_tree().get_first_node_in_group("reloj_noche") as ComponenteRelojNoche
	if reloj != null:
		reloj.noche_terminada.connect(_al_terminar_noche)


func _process(_delta: float) -> void:
	if interactuable.presionado and not presionado_antes:
		abrir()
	presionado_antes = interactuable.presionado


func abrir() -> void:
	escritorio.show()
	jugador.process_mode = Node.PROCESS_MODE_DISABLED
	Input.mouse_mode = Input.MOUSE_MODE_VISIBLE


func cerrar() -> void:
	var reinicio: ComponenteReinicioMantenimiento = get_tree().get_first_node_in_group("reinicio_mantenimiento") as ComponenteReinicioMantenimiento
	if reinicio != null:
		reinicio.interrumpir()
	escritorio.hide()
	jugador.process_mode = Node.PROCESS_MODE_INHERIT
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED


func _al_terminar_noche() -> void:
	if escritorio.visible:
		cerrar()
