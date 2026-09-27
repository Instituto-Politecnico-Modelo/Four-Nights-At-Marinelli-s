class_name CamaraGuardiaOficina
extends CamaraPersonajeBase

signal llego_al_limite(lado: String)

var aviso_emitido: bool = false


func _al_rotar(horizontal: float, _vertical: float) -> void:
	var en_limite: bool = horizontal <= giro_minimo or horizontal >= giro_maximo

	if en_limite and not aviso_emitido:
		aviso_emitido = true
		if horizontal <= giro_minimo:
			llego_al_limite.emit("izquierda")
		else:
			llego_al_limite.emit("derecha")
	elif not en_limite:
		aviso_emitido = false
