extends Node

signal charlie_escondido(esta_escondido: bool)
signal charlie_atrapado()

signal interactuable_focused(interactuable: Node)
signal interactuable_unfocused(interactuable: Node)
signal interactuado(interactuable: Node)

signal pista_descubierta(clue_id: StringName)
signal intento_contrasenia_fallido()
signal laptop_desbloqueada()

signal charlie_descubierto_por(enemy: Node)
