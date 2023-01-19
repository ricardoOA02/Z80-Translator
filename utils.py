codigo_LST = []
codigo_HEX = ""

# Recibe la instruccion para almacenarla
def generar_codigo(_contador_localidades, instruccion_hex):
    contador_loc = hex(int(_contador_localidades))[2:].zfill(4)
    return contador_loc.upper()+"    "+str(instruccion_hex).upper()

# Recibe la instruccion en binario y la devuelve en hexadecimal
def transformar(instruccion):
    inst_transformada = format(int(instruccion, 2), "x")
    if len(inst_transformada)%2 != 0:
        inst_transformada = "0" + inst_transformada
    return inst_transformada


# Creador por:
#   Aranda Quiroz Enrique
#   Organista Alvarez Ricardo
#   Rodriguez Urdapilleta Manuel
#   Sanchez Alvirde Andres Ivan
#   Vazquez Reyes Sebastian