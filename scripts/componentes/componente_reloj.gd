class_name ComponenteReloj
extends Label

var reloj: ComponenteRelojNoche = null


func _ready() -> void:
	reloj = get_tree().get_first_node_in_group("reloj_noche") as ComponenteRelojNoche


func _process(_delta: float) -> void:
	if reloj != null:
		text = "%d:%02d a.m." % [reloj.hora_reloj(), reloj.minutos()]
	else:
		text = Time.get_time_string_from_system().substr(0, 5)
