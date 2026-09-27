extends Node

signal charlie_escondido(esta_escondido: bool)
signal charlie_atrapado()

signal interactuable_enfocado(interactuable: Node)
signal interactuable_desenfocado(interactuable: Node)
signal interactuado(interactuable: Node)

signal pista_descubierta(pista: PistaResource)
signal intento_contrasenia_fallido()
signal laptop_desbloqueada()

signal charlie_descubierto_por(enemigo: Node)
