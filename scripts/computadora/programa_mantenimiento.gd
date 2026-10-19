class_name ProgramaMantenimiento
extends Control

@export var lista: VBoxContainer
@export var aviso: Label
@export var progreso: ProgressBar
@export var detalle: Label
@export var boton_todos: Button
@export var boton_interrumpir: Button

var reinicio: ComponenteReinicioMantenimiento
var botones: Array[Button] = []
var etiquetas: Array[Label] = []


func _ready() -> void:
	reinicio = get_tree().get_first_node_in_group("reinicio_mantenimiento") as ComponenteReinicioMantenimiento
	if reinicio == null:
		aviso.text = "Panel sin conexión con los sistemas de la noche."
		boton_todos.disabled = true
		boton_interrumpir.hide()
		return
	for sistema in reinicio.sistemas:
		var fila := VBoxContainer.new()
		var etiqueta := Label.new()
		etiqueta.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		fila.add_child(etiqueta)
		var boton := Button.new()
		boton.custom_minimum_size.y = 36.0
		boton.pressed.connect(_reiniciar.bind(sistema))
		fila.add_child(boton)
		lista.add_child(fila)
		etiquetas.append(etiqueta)
		botones.append(boton)
		sistema.estado_cambiado.connect(_actualizar)
	reinicio.estado_cambiado.connect(_actualizar)
	reinicio.reloj.noche_terminada.connect(_actualizar)
	boton_todos.pressed.connect(_reiniciar.bind(null))
	boton_interrumpir.pressed.connect(reinicio.interrumpir)
	visibility_changed.connect(_al_cambiar_visibilidad)
	_actualizar()


func _process(_delta: float) -> void:
	if reinicio == null or not reinicio.activo():
		return
	progreso.value = reinicio.tiempo / maxf(reinicio.duracion, 0.01) * 100.0
	detalle.text = "Reiniciando %s · %.1f s restantes\nLa vigilancia está bloqueada. Interrumpir descarta el progreso." % [reinicio.afectados[0].nombre if reinicio.afectados.size() == 1 else "sistemas afectados", maxf(reinicio.duracion - reinicio.tiempo, 0.0)]


func _reiniciar(sistema: ComponenteSistemaMantenimiento) -> void:
	if reinicio.iniciar(sistema):
		Sonidos.boton_inicio()


func _al_cambiar_visibilidad() -> void:
	if not is_visible_in_tree():
		reinicio.interrumpir()


func _actualizar() -> void:
	var fallas: int = 0
	var camaras_caidas: bool = false
	for i in reinicio.sistemas.size():
		var sistema: ComponenteSistemaMantenimiento = reinicio.sistemas[i]
		var estado: String = "REINICIANDO" if sistema.reiniciando else ("ERROR" if sistema.fallando else "OPERATIVO")
		etiquetas[i].text = "%s — %s\n%s" % [sistema.nombre, estado, sistema.consecuencia]
		etiquetas[i].modulate = Color(1.0, 0.45, 0.3) if sistema.fallando else Color(0.65, 0.95, 0.7)
		botones[i].text = "Reiniciar %s · %.0f s" % [sistema.nombre, sistema.duracion_reinicio]
		botones[i].disabled = not sistema.fallando or reinicio.activo() or reinicio.reloj.terminada
		if sistema.fallando:
			fallas += 1
			camaras_caidas = camaras_caidas or sistema.is_in_group("sistema_camaras")
	aviso.text = "PRIORIDAD MÁXIMA: restaurar cámaras." if camaras_caidas else ("%d sistema(s) requieren mantenimiento." % fallas if fallas > 0 else "Todos los sistemas operativos.")
	if reinicio.reloj.terminada:
		aviso.text = "Turno terminado. Mantenimiento detenido."
	boton_todos.disabled = fallas == 0 or reinicio.activo() or reinicio.reloj.terminada
	boton_todos.text = "Reiniciar sistemas afectados · %.0f s" % reinicio.duracion_conjunta
	boton_interrumpir.visible = reinicio.activo()
	progreso.visible = reinicio.activo()
	if not reinicio.activo():
		detalle.text = "Repará las cámaras primero. Prepará tus defensas antes de reiniciar.\nLos animatrónicos siguen avanzando durante el mantenimiento."
