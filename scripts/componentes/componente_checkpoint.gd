class_name ComponenteCheckpoint
extends Node

@export var reloj: ComponenteRelojNoche
@export var etiqueta_noche: Label
@export var noche: int = 1


func _ready() -> void:
	if reloj == null:
		reloj = get_tree().get_first_node_in_group("reloj_noche") as ComponenteRelojNoche
	if Guardado.continuar_partida:
		noche = Guardado.noche_guardada()
	if etiqueta_noche != null:
		etiqueta_noche.text = "Noche %d" % noche
	if reloj == null:
		push_error("El checkpoint no encontró el reloj de la noche")
		return
	if Guardado.continuar_partida:
		reloj.restaurar(Guardado.hora_guardada())
	reloj.hora_cambiada.connect(_al_cambiar_hora)
	reloj.noche_terminada.connect(_al_terminar_noche)
	Guardado.guardar_avance(noche, reloj.hora)


func _al_cambiar_hora(hora: int) -> void:
	Guardado.guardar_avance(noche, hora)


func _al_terminar_noche() -> void:
	Sonidos.seis_am()
