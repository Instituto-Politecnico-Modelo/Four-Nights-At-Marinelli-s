class_name ComponenteHorarioApariciones
extends Node

@export var estados: ComponenteEstadosAparicion
@export var horarios: Array[int] = [60, 120, 160, 210, 270, 300, 315, 345]
@export var espera_inicial: float = 30.0
@export var reduccion_por_visita: float = 3.0
@export var espera_minima: float = 8.0

var reloj: ComponenteRelojNoche
var turnos: ComponenteTurnosAtaque
var siguiente: int = 0
var visitas: int = 0
var tiempo: float = 0.0


func _ready() -> void:
	reloj = get_tree().get_first_node_in_group("reloj_noche")
	turnos = get_tree().get_first_node_in_group("turnos_ataque") as ComponenteTurnosAtaque
	reloj.tiempo_restaurado.connect(_sincronizar_horario)
	reloj.noche_terminada.connect(_detener)
	estados.estado_cambiado.connect(_al_cambiar_estado)
	_sincronizar_horario()


func _process(delta: float) -> void:
	if reloj.terminada or (turnos != null and turnos.bloqueado):
		return
	if estados.indice == 0:
		_revisar_horario()
	elif estados.indice == 1:
		_esperar_en_camara(delta)


func _revisar_horario() -> void:
	if siguiente >= horarios.size():
		return

	var minutos: float = reloj.tiempo / reloj.segundos_por_hora * 60.0
	if minutos >= horarios[siguiente]:
		if turnos != null and not turnos.solicitar(self):
			return
		siguiente += 1
		estados.avanzar()


func _esperar_en_camara(delta: float) -> void:
	tiempo -= delta
	if tiempo <= 0.0:
		estados.avanzar()


func _al_cambiar_estado(indice: int) -> void:
	if indice == 0 and turnos != null:
		turnos.liberar(self)
	if indice == 1:
		tiempo = maxf(espera_inicial - reduccion_por_visita * visitas, espera_minima)
		visitas += 1


func _sincronizar_horario() -> void:
	siguiente = 0
	var minutos: float = reloj.tiempo / reloj.segundos_por_hora * 60.0
	while siguiente < horarios.size() and horarios[siguiente] < minutos:
		siguiente += 1
	visitas = siguiente
	estados.ir_a(0)


func _detener() -> void:
	estados.ir_a(0)
