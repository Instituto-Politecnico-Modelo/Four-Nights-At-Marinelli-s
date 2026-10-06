extends Node3D

## Escena de prueba: reproduce el jumpscare en bucle.
## Espacio = repetir ataque, I = idle, C = caminar.

@onready var freddy: MariFreddy = $MariFreddy


func _ready() -> void:
	freddy.ataque_terminado.connect(_al_terminar_ataque)
	await get_tree().create_timer(1.0).timeout
	freddy.atacar()


func _al_terminar_ataque() -> void:
	await get_tree().create_timer(1.5).timeout
	freddy.atacando = false
	freddy.atacar()


func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventKey and event.pressed and not event.echo:
		match event.keycode:
			KEY_SPACE:
				freddy.atacando = false
				freddy.atacar()
			KEY_I:
				freddy.atacando = false
				freddy.reproducir_idle()
			KEY_C:
				freddy.atacando = false
				freddy.caminar()
