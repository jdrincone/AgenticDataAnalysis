from graphviz import Digraph

dot = Digraph(comment='Flujo General Okuo IA DataLab', format='gv')

dot.attr(rankdir='LR', size='12,6')  # Más ancho

# Nodos principales
# Colores corporativos aproximados

dot.node('A', 'Inicio / Login', style='filled', fillcolor='#1C8074', fontcolor='white', shape='ellipse')
dot.node('B', 'Gestión de Datos', style='filled', fillcolor='#e0e0e0', shape='ellipse')
dot.node('C', 'Carga y selección de archivos', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('D', 'Botón Conectar a BD', style='filled', fillcolor='#e0e0e0', shape='ellipse')
dot.node('E', 'Describe datasets', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('F', 'Selecciona archivos a analizar', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('G', 'Funcionalidad próximamente disponible', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('H', 'Interfaz de Chat', style='filled', fillcolor='#e0e0e0', shape='ellipse')
dot.node('I', 'Usuario hace pregunta', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('J', 'Chatbot responde y muestra visualizaciones', style='filled', fillcolor='#f5f5f5', shape='ellipse')
dot.node('K', 'Depuración (opcional)', style='filled', fillcolor='#e0e0e0', shape='ellipse')
dot.node('L', 'Ver pasos intermedios, código y salidas', style='filled', fillcolor='#f5f5f5', shape='ellipse')

# Conexiones

dot.edge('A', 'B')
dot.edge('B', 'C', label='Selecciona CSV')
dot.edge('B', 'D', label='Selecciona BD')
dot.edge('C', 'E')
dot.edge('C', 'F')
dot.edge('D', 'G')
dot.edge('F', 'H')
dot.edge('H', 'I')
dot.edge('I', 'J')
dot.edge('J', 'K')
dot.edge('K', 'L')

# Exportar a GV y SVG
dot.format = 'gv'
dot.render('flujo_general', view=False)
dot.format = 'svg'
dot.render('flujo_general', view=False)

print('Diagramas generados: flujo_general.gv y flujo_general.svg') 