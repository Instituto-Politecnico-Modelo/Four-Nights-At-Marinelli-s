class_name ComponenteVigilanciaVentana
extends Node

signal jumpscare_solicitado

@export var estados: ComponenteEstadosAparicion
@export var espera_inicial: float = 10.0
@export var reduccion_por_visita: float = 1.0
@export var espera_minima: float = 4.0

var persiana: ComponentePersiana
var vigilando: bool = false
var visitas: int = 0
var tiempo: float = 0.0


func _ready() -> void:
	persiana = get_tree().get_first_node_in_group("persiana_ventana")
	estados.estado_cambiado.connect(_al_cambiar_estado)


func _process(delta: float) -> void:
	if not vigilando:
		return

	tiempo -= delta
	if tiempo > 0.0:
		return

	vigilando = false
	if persiana.cerrada:
		estados.ir_a(0)
	else:
		jumpscare_solicitado.emit()


func _al_cambiar_estado(indice: int) -> void:
	vigilando = indice == 2
	if vigilando:
		tiempo = maxf(espera_inicial - reduccion_por_visita * visitas, espera_minima)
		visitas += 1
