class_name ComponenteTurnosAtaque
extends Node

@export var reloj: ComponenteRelojNoche
@export var descanso_entre_ataques: float = 5.0

var encuentro: Node
var descanso: float = 0.0
var bloqueado: bool = false


func _ready() -> void:
	reloj.noche_terminada.connect(detener)


func _process(delta: float) -> void:
	descanso = maxf(descanso - delta, 0.0)


func solicitar(solicitante: Node) -> bool:
	if bloqueado or reloj.terminada:
		return false
	if encuentro == solicitante:
		return true
	if encuentro != null or descanso > 0.0:
		return false
	encuentro = solicitante
	return true


func liberar(solicitante: Node) -> void:
	if encuentro != solicitante:
		return
	encuentro = null
	descanso = descanso_entre_ataques


func detener() -> void:
	bloqueado = true
	encuentro = null
