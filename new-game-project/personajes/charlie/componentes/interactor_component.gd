extends Area2D
class_name InteractorComponent
## InteractorComponent
## Detecta InteractableComponent cercanos, mantiene el mas cercano como
## "enfocado" y dispara la interaccion al presionar la accion "interactuar".

var _en_rango: Array[InteractableComponent] = []
var _enfocado: InteractableComponent = null


func _ready() -> void:
	area_entered.connect(_on_area_entered)
	area_exited.connect(_on_area_exited)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("interactuar") and _enfocado != null:
		SignalBus.interactuado.emit(_enfocado)
		_enfocado.interactuado.emit()


func _on_area_entered(area: Area2D) -> void:
	if area is InteractableComponent:
		_en_rango.append(area)
		_actualizar_foco()


func _on_area_exited(area: Area2D) -> void:
	if area is InteractableComponent:
		_en_rango.erase(area)
		_actualizar_foco()


func _actualizar_foco() -> void:
	var nuevo_foco: InteractableComponent = _calcular_mas_cercano()

	if nuevo_foco == _enfocado:
		return

	if _enfocado != null:
		SignalBus.interactuable_desenfocado.emit(_enfocado)

	_enfocado = nuevo_foco

	if _enfocado != null:
		SignalBus.interactuable_enfocado.emit(_enfocado)


func _calcular_mas_cercano() -> InteractableComponent:
	if _en_rango.is_empty():
		return null

	var mas_cercano: InteractableComponent = _en_rango[0]
	var menor_distancia: float = global_position.distance_squared_to(mas_cercano.global_position)

	for interactuable in _en_rango:
		var distancia: float = global_position.distance_squared_to(interactuable.global_position)
		if distancia < menor_distancia:
			menor_distancia = distancia
			mas_cercano = interactuable

	return mas_cercano
