from tkinter import *
from tkinter import filedialog
import Z80Table
import utils
import re
import os

# Creador por:
#   Aranda Quiroz Enrique
#   Organista Alvarez Ricardo
#   Rodriguez Urdapilleta Manuel
#   Sanchez Alvirde Andres Ivan
#   Vazquez Reyes Sebastian

def on_button_click():
    # Mostramos un diálogo de selección de archivos y almacenamos la ruta del archivo seleccionado
    ruta_archivo = filedialog.askopenfilename(
    filetypes=[('Archivos ASM', '*.asm')]
    )
    nombre, extension = os.path.splitext(ruta_archivo)
    # Abrimos el archivo en modo lectura ('r') y lo almacenamos en una variable
    with open(ruta_archivo, 'r') as archivo:
        etiquetas = {}
        bug_flag = False
        seg_pasada = {}
        codigo = []
        instruction = []
        no_linea = 0
        CL = 0
        ins_large = 0

        archivo_lst = nombre + '.lst'
        #Lee cada linea del archivo
        for linea in archivo:
            #Variables de apoyo
            instruccion_binario = ""
            instruccion_no_tag = ""

            subins = []
            linea = linea.strip()
            #En caso de que se encuentre una linea vacia la salta
            if linea == '':
                
                continue
            else:
                no_linea += 1

            #Encontrar etiquetas
            etiStart = linea.find(":")
            if etiStart != -1:
                #Toma la etiqueta y la asocia con el contador de localidades
                etiqueta = linea[:etiStart]
                etiqueta = etiqueta.upper()
                etiqueta = etiqueta.strip()
                linea = linea[etiStart+1:]
                linea = linea.strip()
                etiquetas[etiqueta] = str(bin(CL)[2:])
            linea = linea.upper()
            linea = linea.strip()
            
            instruction.append(linea)
            
            #Encontrar comentarios
            coment = linea.find(";")
            if coment != -1:
                linea = linea[:coment] + linea[len(linea):]
            
            #Separa la instruccion 
            division = linea.find(" ")
            if not (division == -1):
                subins.append(linea[:division])
                subins.append(linea[division+1:])
            elif division == -1:
                subins.append(linea)

            #Tabla A-1 y A-2. Grupo de carga de 8 y 16 bits
            #Separa la instruccion de los operandos
            if subins[0] == "LD":
                #Separa los operandos
                registro = subins[1].split(",")
                registro[0] = registro[0].strip()
                registro[1] = registro[1].strip()
                rAux0 = registro[0]
                rAux1 = registro[1]

            #8 bits
                #LD r,r'
                if registro[0] in Z80Table.registros and registro[1] in Z80Table.registros:
                    #Se obtiene la instruccion en binario
                    instruccion_binario = "01"+Z80Table.registros[registro[0]]+Z80Table.registros[registro[1]] 

                #LD r,n
                elif registro[0] in Z80Table.registros and re.match(r'^[0-9]{1,4}$',registro[1]):
                    #Se obtiene el dato y se transforma a decimal
                    if int(registro[1]) < 256:
                        dato = str(bin(int(registro[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "00"+Z80Table.registros[registro[0]]+"110"+dato

                #LD r,(HL)
                elif registro[0] in Z80Table.registros and registro[1] == "(HL)":
                    instruccion_binario = "01"+Z80Table.registros[registro[0]]+"110"


                #LD r,(IX+d)
                elif registro[0] in Z80Table.registros and re.match(r'^\(IX\+[0-9]{1,4}\)$',registro[1]):
                    registro[1] = registro[1].replace("(","")
                    registro[1] = registro[1].replace(")","")
                    reg_data = registro[1].split("+")
                    if int(reg_data[1]) < 256:
                        dato = str(bin(int(reg_data[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "1101110101"+Z80Table.registros[registro[0]]+"110"+dato

                #LD r,(IY+d)
                elif registro[0] in Z80Table.registros and re.match(r'^\(IY\+[0-9]{1,4}\)$',registro[1]):
                    registro[1] = registro[1].replace("(","")
                    registro[1] = registro[1].replace(")","")
                    reg_data = registro[1].split("+")
                    if int(reg_data) < 256:
                        dato = str(bin(int(reg_data[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "1111110101"+Z80Table.registros[registro[0]]+"110"+dato


                #LD (HL),r
                elif registro[0] == "(HL)" and registro[1] in Z80Table.registros:
                    instruccion_binario = "01110"+Z80Table.registros[registro[1]]

                #LD (IX+d),r
                elif re.match(r'^\(IX\+[0-9]{1,4}\)$',registro[0]) and registro[1] in Z80Table.registros:
                    registro[0] = registro[0].replace("(","")
                    registro[0] = registro[0].replace(")","")
                    reg_data = registro[0].split("+")
                    if int(reg_data[1]) < 256:
                        dato = str(bin(int(reg_data[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "1101110101110"+Z80Table.registros[registro[1]]+dato

                #LD (IY+d),r
                elif re.match(r'^\(IY\+[0-9]{1,4}\)$',registro[0]) and registro[1] in Z80Table.registros:
                    registro[0] = registro[0].replace("(","")
                    registro[0] = registro[0].replace(")","")
                    reg_data = registro[0].split("+")
                    if int(reg_data[1]) < 256:
                        dato = str(bin(int(reg_data[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "1111110101110"+Z80Table.registros[registro[1]]+dato

                #LD (HL),n
                elif registro[0] == "(HL)" and str.isdigit(registro[1]):
                    if int(registro[1]) < 256:
                        #Se obtiene el dato y se transforma a decimal
                        dato = str(bin(int(registro[1]))[2:])
                        dato = dato.zfill(8)
                        instruccion_binario = "00110110"+dato
                
                #LD (IX+d),n
                elif re.match(r'\(IX\+[0-9]{1,4}\)',registro[0]) and str.isdigit(registro[1]):
                    if int(registro[1]) < 256:
                        registro[0] = registro[0].replace("(","")
                        registro[0] = registro[0].replace(")","")
                        reg_data = registro[0].split("+")
                        if int(reg_data[1]) < 256:
                            dato_ix = str(bin(int(reg_data[1]))[2:])
                            dato_ix = dato_ix.zfill(8)
                            num = str(bin(int(registro[1]))[2:])
                            num = num.zfill(8)
                            instruccion_binario = "1101110100110110"+dato_ix+num

                #LD (IY+d),n
                elif re.match(r'^\(IY\+[0-9]{1,4}\)$',registro[0]) and str.isdigit(registro[1]):
                    if int(registro[1]) < 256:
                        registro[0] = registro[0].replace("(","")
                        registro[0] = registro[0].replace(")","")
                        reg_data = registro[0].split("+")
                        if int(reg_data[1]) < 256:
                            dato_iy = str(bin(int(reg_data[1]))[2:])
                            dato_iy = dato_iy.zfill(8)
                            num = str(bin(int(registro[1]))[2:])
                            num = num.zfill(8)
                            instruccion_binario = "1111110100110110"+dato_iy+num

                #LD A,(BC)
                elif registro[0] == "A" and registro[1] == "(BC)":
                    instruccion_binario = "00001010"
                
                #LD A,(DE)
                elif registro[0] == "A" and registro[1] == "(DE)":
                    instruccion_binario = "00011010"

                #LD A,(nn)
                elif registro[0] == "A" and (re.match(r'^\([0-9]+\)$',registro[1]) or re.match(r'^\([0-9]+H\)$',registro[1])):
                    registro[1] = registro[1].replace("(","")
                    registro[1] = registro[1].replace(")","")
                    #Si el numero tiene H indica que esta en binario
                    regg = registro[1]
                    if regg[-1] == "H":
                        registro[1] = registro[1].replace("H","")
                        regi = int(registro[1], 16)
                        nn = bin(regi)[2:]
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00111010" + nn

                    #Si no tiene H indica que esta en decimal
                    elif int(registro[1]) < 65355:
                        nn = bin(int(registro[1]))[2:]
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00111010" + nn
                
                #LD (BC),A
                elif registro[0] == "(BC)" and registro[1] == "A":
                    instruccion_binario = "00000010"

                #LD (DE),A
                elif registro[0] == "(DE)" and registro[1] == "A":
                    instruccion_binario = "00010010"

                #LD (nn),A
                elif (re.match(r'^\([0-9]+\)$',registro[0]) or re.match(r'^\([0-9]+H\)$',registro[0])) and registro[1] == "A":
                    registro[0] = registro[0].replace("(","")
                    registro[0] = registro[0].replace(")","")
                    #Si el numero tiene H indica que esta en binario
                    regg = registro[0]
                    if regg[-1] == "H":
                        registro[0] = registro[0].replace("H","")
                        regi = int(registro[0], 16)
                        nn = bin(regi)[2:]
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00110010" + nn

                    #Si no tiene H indica que esta en decimal
                    elif int(registro[0]) < 65355:
                        nn = bin(int(registro[0]))[2:]
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00110010" + nn

                
                #LD A,I
                #LD A,R
                elif registro[0] == "A" and (registro[1] == "I" or registro[1] == "R"):
                    if registro[1] == "I":
                        instruccion_binario = "1110110101010111"
                    elif registro[1] == "R":
                        instruccion_binario = "1110110101011111"
                
                #LD I,A
                #LD R,A
                elif (registro[0] == "I" or registro[0] == "R") and registro[1] == "A":
                    if registro[0] == "I":
                        instruccion_binario = "1110110101000111"
                    elif registro[0] == "R":
                        instruccion_binario = "1110110101001111"
            
            #16 bits

                #LD dd,nn
                elif registro[0] in Z80Table.reg_par and (str.isdigit(registro[1]) or re.match(r'^[0-9A-F]{1,4}H$',registro[1])):
                    regg = registro[1]
                    if regg[-1] == "H":
                        regg = regg.replace("H","")
                        if len(regg) < 5:
                            nn = str(bin(int(regg, 16))[2:])
                            nn = nn.zfill(16)
                            nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                            instruccion_binario = "00" + Z80Table.reg_par[registro[0]] + "0001" + nn
                    elif int(regg) < 65355:
                        dato = bin(int(registro[1]))[2:]
                        dato = dato.zfill(16)
                        dato = dato[len(dato)//2:] + dato[:len(dato)//2]
                        instruccion_binario = "00" + Z80Table.reg_par[registro[0]] + "0001" + dato
                

                #LD IX,nn
                elif registro[0] == "IX" and (re.match(r'^[0-9A-F]{1,4}H$',registro[1]) or str.isdigit(registro[1])):
                    regg = registro[1]
                    if regg[-1] == "H":
                        regg = regg.replace("H","")
                        if len(regg) < 5:
                            regg = int(regg,16)
                            nn = str(bin(regg)[2:])
                            nn = nn.zfill(16)
                            nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                            instruccion_binario = "1101110100100001" + nn
                    elif int(regg) < 65355:
                        nn = str(bin(int(registro[1],10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1101110100100001" + nn

                #LD IY,nn
                elif registro[0] == "IY" and (re.match(r'^[0-9A-F]{1,4}H$',registro[1]) or str.isdigit(registro[1])):
                    regg = registro[1]
                    if regg[-1] == "H":
                        regg = regg.replace("H","")
                        if len(regg) < 5:
                            regg = int(regg,16)
                            nn = str(bin(regg)[2:])
                            nn = nn.zfill(16)
                            nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                            instruccion_binario = "1111110100100001" + nn
                    elif int(regg) < 65355:
                        nn = str(bin(int(registro[1], 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1111110100100001" + nn
                
                #LD HL,(nn)
                elif registro[0] == "HL" and (re.match(r'^\([0-9A-F]{1,4}H\)',registro[1]) or re.match(r'^\([0-9]{1,5}\)',registro[1])):
                    regg = registro[1]
                    regg = regg[1:-1]
                    if regg[-1] == "H":
                        regg = regg.replace("H")
                        if len(regg) < 5:
                            nn = str(bin(int(regg, 16))[2:])
                            nn = nn.zfill(16)
                            nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                            instruccion_binario = "00101010" + nn
                    elif int(regg) < 65355:
                        nn = str(bin(int(regg, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00101010" + nn

                #LD dd,(nn)
                elif registro[0] in Z80Table.reg_par and (re.match(r'^\([0-9A-F]{1,4}H\)',registro[1]) or re.match(r'^\([0-9]{1,5}\)',registro[1])):
                    rAux1 = registro[1]
                    rAux1 = rAux1[1:-1]
                    if rAux1[-1] == "H":
                        rAux1 = rAux1.replace("H","")
                        nn = str(bin(int(rAux1, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1110110101" + Z80Table.reg_par[registro[0]] + "1011" + nn
                    elif str.isdigit(rAux1):
                        nn = str(bin(int(rAux1, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1110110101" + Z80Table.reg_par[registro[0]] + "1011" + nn
                    

                #LD IX,(nn)
                elif registro[0] == "IX" and (re.match(r'^\([0-9A-F]{1,4}H\)',registro[1]) or re.match(r'^\([0-9]{1,5}\)',registro[1])):
                    rAux1 = registro[1]
                    rAux1 = rAux1[1:-1]
                    if rAux1[-1] == "H":
                        rAux1 = rAux1.replace("H","")
                        nn = str(bin(int(rAux1, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1101110100101010" + nn
                    elif str.isdigit(rAux1):
                        nn = str(bin(int(rAux1, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1101110100101010" + nn
                
                #LD IY,(nn)
                elif registro[0] == "IY" and (re.match(r'^\([0-9A-F]{1,4}H\)',registro[1]) or re.match(r'^\([0-9]{1,5}\)',registro[1])):
                    rAux1 = registro[1]
                    rAux1 = rAux1[1:-1]
                    if rAux1[-1] == "H":
                        rAux1 = rAux1.replace("H","")
                        nn = str(bin(int(rAux1, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1111110100101010" + nn
                    elif str.isdigit(rAux1):
                        nn = str(bin(int(rAux1, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1111110100101010" + nn
                
                #LD (nn),HL
                elif (re.match(r'^\([0-9A-F]{1,4}H\)',registro[0]) or re.match(r'^\([0-9]{1,5}\)',registro[0])) and registro[1] == "HL":
                    regg = registro[0]
                    regg = regg[1:-1]
                    if regg[-1] == "H":
                        regg = regg.replace("H", "")
                        if len(regg) < 5:
                            nn = str(bin(int(regg, 16))[2:])
                            nn = nn.zfill(16)
                            nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                            instruccion_binario = "00100010" + nn
                    elif int(regg) < 65355:
                        nn = str(bin(int(regg, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "00100010" + nn
                
                #LD (nn),dd
                elif (re.match(r'^\([0-9A-F]{1,4}H\)',registro[0]) or re.match(r'^\([0-9]{1,5}\)',registro[0])) and registro[1] in Z80Table.reg_par:
                    rAux0 = registro[0]
                    rAux0 = rAux0[1:-1]
                    if rAux0[-1] == "H":
                        rAux0 = rAux0.replace("H","")
                        nn = str(bin(int(rAux0, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1110110101" + Z80Table.reg_par[registro[1]] + "0011" + nn
                    elif str.isdigit(rAux0):
                        nn = str(bin(int(rAux0, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1110110101" + Z80Table.reg_par[registro[1]] + "0011" + nn

                #LD (nn),IX
                elif (re.match(r'^\([0-9A-F]{1,4}H\)',registro[0]) or re.match(r'^\([0-9]{1,5}\)',registro[0])) and registro[1] == " IX":
                    
                    rAux0 = registro[0]
                    rAux0 = rAux0[1:-1]
                    if rAux0[-1] == "H":
                        rAux0 = rAux0.replace("H","")
                        nn = str(bin(int(rAux0, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1101110100100010" + nn
                    elif str.isdigit(rAux0):
                        nn = str(bin(int(rAux0, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1101110100100010" + nn

                #LD (nn),IY
                elif (re.match(r'^\([0-9A-F]{1,4}H\)',registro[0]) or re.match(r'^\([0-9]{1,5}\)',registro[0])) and registro[1] == " IY":
                    rAux0 = registro[0]
                    rAux0 = rAux0[1:-1]
                    if rAux0[-1] == "H":
                        rAux0 = rAux0.replace("H","")
                        nn = str(bin(int(rAux0, 16))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1111110100100010" + nn
                    elif str.isdigit(rAux0):
                        nn = str(bin(int(rAux0, 10))[2:])
                        nn = nn.zfill(16)
                        nn = nn[len(nn)//2:] + nn[:len(nn)//2]
                        instruccion_binario = "1111110100100010" + nn
                
                #LD SP,HL , LD SP,IX , LD SP,IY
                elif registro[0] == "SP":
                    if registro[1] == "HL":
                        instruccion_binario = "11111001"
                    elif registro[1] == "IX":
                        instruccion_binario = "1101110111111001"
                    elif registro[1] == "IY":
                        instruccion_binario = "1111110111111001"

            
            #PUSH qq, PUSH IX, PUSH IY
            elif subins[0] == "PUSH":
                reg = subins[1]
                if reg in Z80Table.reg_par:
                    instruccion_binario = "11" + Z80Table.reg_par[reg] + "0101"
                elif reg == "IX":
                    instruccion_binario = "1101110111100101"
                elif reg == "IY":
                    instruccion_binario = "1111110111100101"
            
            #POP qq, POP IX, POP IY    
            elif subins[0] == "POP":
                reg = subins[1]
                if reg in Z80Table.reg_par:
                    instruccion_binario = "11" + Z80Table.reg_par[reg] + "0001"
                elif reg == "IX":
                    instruccion_binario = "1101110111100001"
                elif reg == "IY":
                    instruccion_binario = "1111110111100001"
            
            #Tabla A-3. Grupo de intercambio y transferencia y busqueda de bloques

            elif subins[0] == "EX":
                ins_flag = False
                reg = subins[1].split(",")
                reg0 = reg[0].strip()
                reg1 = reg[1].strip()
                instruccion = subins[0] + " " + reg0 + "," + reg1

                if instruccion in Z80Table.tA3:
                    instruccion_binario = Z80Table.tA3[instruccion]
                

            elif subins[0] in Z80Table.tA3:
                instruccion_binario = Z80Table.tA3[subins[0]]

            #Tabla A-4. El grupo aritmetico y logico de 8 bits
                    
            #ADD hasta CP
            elif subins[0] in Z80Table.ins_TA4 and (subins[1] in Z80Table.registros or subins[1].isdigit() or subins[1] == "(HL)" or re.match(r'\(IX\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IX\+[0-9A-F]{1,2}H\)',subins[1]) or re.match(r'\(IY\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IY\+[0-9A-F]{1,2}H\)',subins[1])):
                instr = subins[0]
                #ADD r
                if subins[1] in Z80Table.registros:
                    instruccion_binario = Z80Table.tA4["reg"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])
                    instruccion_binario = instruccion_binario.replace("r",Z80Table.registros[subins[1]])

                #ADD (HL)
                elif subins[1] == "(HL)":
                    instruccion_binario = Z80Table.tA4["(HL)"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])

                #ADD (IX+d)
                elif re.match(r'\(IX\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IX\+[0-9A-F]{1,2}H\)',subins[1]):
                    data = subins[1]
                    data = data[4:]
                    data = data[:-1]
                    if data[-1] == "H":
                        data = data.replace("H","")
                        data = str(bin(int(data, 16))[2:])
                        data = data.zfill(8)
                    elif data.isdigit():
                        data = str(bin(int(data, 10))[2:])
                        data = data.zfill(8)
                    instruccion_binario = Z80Table.tA4["(IX+d)"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])
                    instruccion_binario = instruccion_binario.replace("d",data)

                #ADD (IY+d)
                elif re.match(r'\(IY\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IY\+[0-9A-F]{1,2}H\)',subins[1]):
                    data = subins[1]
                    data = data[4:]
                    data = data[:-1]
                    if data[-1] == "H":
                        data = data.replace("H","")
                        data = str(bin(int(data, 16))[2:])
                        data = data.zfill(8)
                    elif data.isdigit():
                        data = str(bin(int(data, 10))[2:])
                        data = data.zfill(8)
                    instruccion_binario = Z80Table.tA4["(IY+d)"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])
                    instruccion_binario = instruccion_binario.replace("d",data)

                #ADD n
                elif subins[1].isdigit or re.match(r'[0-9A-F]{1,2}H',subins[1]):
                    data = subins[1]
                    if subins[1].isdigit():
                        data = str(bin(int(data, 10))[2:])
                        data = data.zfill(8)
                    elif data[-1] == "H":
                        data = data.replace("H","")
                        data = str(bin(int(data, 16))[2:])
                        data = data.zfill(8)
                    instruccion_binario = Z80Table.tA4["num"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])
                    instruccion_binario = instruccion_binario.replace("n",data)
    
            #INC y DEC
            elif (subins[0] == "INC" or subins[0] == "DEC") and (subins[1] != "IX" and subins[1] != "IY" and not(subins[1] in Z80Table.reg_par)):
                idc = {"INC":"100","DEC":"101"} 
                instr = idc[subins[0]]
                #INC r
                if subins[1] in Z80Table.registros:
                    instruccion_binario = Z80Table.tA4["regID"]
                    instruccion_binario = instruccion_binario.replace("x",instr)
                    instruccion_binario = instruccion_binario.replace("r",Z80Table.registros[subins[1]])

                #INC (HL)
                elif subins[1] == "(HL)":
                    instruccion_binario = Z80Table.tA4["(HL)ID"]
                    instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA4[instr])

                #INC (IX+d)
                elif re.match(r'\(IX\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IX\+[0-9A-F]{1,2}H\)',subins[1]):
                    data = subins[1]
                    data = data[4:]
                    data = data[:-1]
                    if data[-1] == "H":
                        data = data.replace("H","")
                        data = str(bin(int(data, 16))[2:])
                        data = data.zfill(8)
                    elif data.isdigit():
                        data = str(bin(int(data, 10))[2:])
                        data = data.zfill(8)
                    instruccion_binario = Z80Table.tA4["IXID"]
                    instruccion_binario = instruccion_binario.replace("x",instr)
                    instruccion_binario = instruccion_binario.replace("d",data)

                #INC (IY+d)
                elif re.match(r'\(IY\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IY\+[0-9A-F]{1,2}H\)',subins[1]):
                    data = subins[1]
                    data = data[4:]
                    data = data[:-1]
                    if data[-1] == "H":
                        data = data.replace("H","")
                        data = str(bin(int(data, 16))[2:])
                        data = data.zfill(8)
                    elif data.isdigit():
                        data = str(bin(int(data, 10))[2:])
                        data = data.zfill(8)
                    instruccion_binario = Z80Table.tA4["IYID"]
                    instruccion_binario = instruccion_binario.replace("x",instr)
                    instruccion_binario = instruccion_binario.replace("d",data)
                

            #Tabla A-5. Grupo aritmetico y de control de la CPU de aplicacion general
            elif subins[0] in Z80Table.tA5:
                instruccion_binario = Z80Table.tA5[subins[0]]
                if len(subins) > 1:
                    if subins[1] == "0":
                        instruccion_binario = instruccion_binario.replace("x","000")
                    elif subins[1] == "1":
                        instruccion_binario = instruccion_binario.replace("x","010")
                    elif subins[1] == "2":
                        instruccion_binario = instruccion_binario.replace("x","011")

            #Tabla A-6. Grupo aritmetico y de control de la CPU de aplicacion general
            elif subins[0] in Z80Table.ins_TA6 and len(subins) == 2:
                coma = subins[1].find(",")
                if subins[0] == "INC" or subins[0] == "DEC":
                    if subins[1] in Z80Table.reg_par:
                        instruccion_binario = Z80Table.tA6[subins[0]]
                        instruccion_binario = instruccion_binario.replace("ss",Z80Table.reg_par[subins[1]])
                    elif subins[1] == "IX" or subins[1] == "IY":
                        inst = subins[0] + subins[1]
                        instruccion_binario = Z80Table.tA6[inst]
                elif coma != -1:
                    reg = subins[1]
                    regs = []
                    regs.append(reg[:coma])
                    regs.append(reg[coma+1:])
                    inst = subins[0] + regs[0]
                    if inst in Z80Table.tA6:
                        instruccion_binario = Z80Table.tA6[inst]
                        if regs[1] in Z80Table.reg_par:
                            instruccion_binario = instruccion_binario.replace("ss",Z80Table.reg_par[regs[1]])

            #Tabla A-7. Grupo de rotacion y desplazamiento
            elif subins[0] in Z80Table.ins_TA7 or subins[0] in Z80Table.ins_TA7_P2:
                inst = subins[0]
                if inst in Z80Table.ins_TA7_P2:
                    instruccion_binario = Z80Table.ins_TA7_P2[inst]
                elif inst in Z80Table.ins_TA7:
                    if subins[1] in Z80Table.registros:
                        instruccion_binario = Z80Table.tA7["reg"]
                        instruccion_binario = instruccion_binario.replace("r",Z80Table.registros[subins[1]])
                        instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])

                    elif subins[1] == "(HL)":
                        instruccion_binario = Z80Table.tA7["(HL)"]
                        instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])

                    elif re.match(r'\(IX\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IX\+[0-9A-F]{1,3}H\)',subins[1]):
                        data = subins[1]
                        data = data[4:]
                        data = data[:-1]
                        if data.isdigit():
                            if int(data) < 256:
                                data = str(bin(int(data, 10))[2:])
                                data = data.zfill(8)
                                instruccion_binario = Z80Table.tA7["(IX+d)"]
                                instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])
                                instruccion_binario = instruccion_binario.replace("d",data)
                        elif data[-1] == "H":
                            data = data.replace("H","")
                            if int(data,16) < int('FF',16):
                                data = str(bin(int(data, 16))[2:])
                                data = data.zfill(8)
                                instruccion_binario = Z80Table.tA7["(IX+d)"]
                                instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])
                                instruccion_binario = instruccion_binario.replace("d",data)

                    elif re.match(r'\(IY\+[0-9]{1,3}\)',subins[1]) or re.match(r'\(IY\+[0-9A-F]{1,3}H\)',subins[1]):
                        data = subins[1]
                        data = data[4:]
                        data = data[:-1]
                        if data.isdigit():
                            if int(data) < 256:
                                data = str(bin(int(data, 10))[2:])
                                data = data.zfill(8)
                                instruccion_binario = Z80Table.tA7["(IY+d)"]
                                instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])
                                instruccion_binario = instruccion_binario.replace("d",data)
                        elif data[-1] == "H":
                            data = data.replace("H","")
                            if int(data,16) < int('FF',16):
                                data = str(bin(int(data, 16))[2:])
                                data = data.zfill(8)
                                instruccion_binario = Z80Table.tA7["(IY+d)"]
                                instruccion_binario = instruccion_binario.replace("x",Z80Table.ins_TA7[subins[0]])
                                instruccion_binario = instruccion_binario.replace("d",data)

            #Tabla A-8. Grupo BIT, SET Y RESET
            elif subins[0] in Z80Table.t8_ins:
                subins[1].find(",")
                regs = subins[1].split(",")
                if regs[0].isdigit:
                    if int(regs[0]) < 8:
                        if regs[1] in Z80Table.registros:
                            num_bit = str(bin(int(regs[0],10))[2:])
                            instruccion_binario = Z80Table.tA8["reg"]
                            instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                            instruccion_binario = instruccion_binario.replace("b",num_bit)
                            instruccion_binario = instruccion_binario.replace("r",Z80Table.registros[regs[1]])
                        elif regs[1] == "(HL)":
                            num_bit = str(bin(int(regs[0],10))[2:])
                            instruccion_binario = Z80Table.tA8["(HL)"]
                            instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                            instruccion_binario = instruccion_binario.replace("b",num_bit)
                        elif re.match(r'\(IX\+[0-9]{1,3}\)',regs[1]) or re.match(r'\(IX\+[0-9A-F]{1,3}H\)',regs[1]):
                            num_bit = str(bin(int(regs[0],10))[2:])
                            data = regs[1]
                            data = data[4:]
                            data = data[:-1]
                            if data.isdigit():
                                if int(data) < 256:
                                    data = str(bin(int(data, 10))[2:])
                                    data = data.zfill(8)
                                    instruccion_binario = Z80Table.tA8["(IX+d)"]
                                    instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                                    instruccion_binario = instruccion_binario.replace("b",num_bit)
                                    instruccion_binario = instruccion_binario.replace("d",data)
                            elif data[-1] == "H":
                                data = data.replace("H","")
                                if int(data,16) < int('FF',16):
                                    data = str(bin(int(data, 16))[2:])
                                    data = data.zfill(8)
                                    instruccion_binario = Z80Table.tA8["(IX+d)"]
                                    instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                                    instruccion_binario = instruccion_binario.replace("b",num_bit)
                                    instruccion_binario = instruccion_binario.replace("d",data)
                        elif re.match(r'\(IY\+[0-9]{1,3}\)',regs[1]) or re.match(r'\(IY\+[0-9A-F]{1,3}H\)',regs[1]):
                            num_bit = str(bin(int(regs[0],10))[2:])
                            data = regs[1]
                            data = data[4:]
                            data = data[:-1]
                            if data.isdigit():
                                if int(data) < 256:
                                    data = str(bin(int(data, 10))[2:])
                                    data = data.zfill(8)
                                    instruccion_binario = Z80Table.tA8["(IY+d)"]
                                    instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                                    instruccion_binario = instruccion_binario.replace("b",num_bit)
                                    instruccion_binario = instruccion_binario.replace("d",data)
                            elif data[-1] == "H":
                                data = data.replace("H","")
                                if int(data,16) < int('FF',16):
                                    data = str(bin(int(data, 16))[2:])
                                    data = data.zfill(8)
                                    instruccion_binario = Z80Table.tA8["(IY+d)"]
                                    instruccion_binario = instruccion_binario.replace("x",Z80Table.t8_ins[subins[0]])
                                    instruccion_binario = instruccion_binario.replace("b",num_bit)
                                    instruccion_binario = instruccion_binario.replace("d",data)

            #Tabla A-9. Grupo de JUMP (salto)
            elif subins[0] == "JP":
                coma = subins[1].find(",")
                if subins[1] in Z80Table.extra_TA9: #JP (HL|IX|IY)
                    inst = subins[0] + subins[1]
                    instruccion_binario = Z80Table.tA9[inst]

                elif coma != -1: #JP cc,nn
                    regs = subins[1].split(",")
                    if regs[0] in Z80Table.tcc and regs[1] in etiquetas:
                        instruccion_binario = Z80Table.tA9["JPC"]
                        direct = etiquetas[regs[1]]
                        direct = direct.zfill(16)
                        direct = direct[len(direct)//2:] + direct[:len(direct)//2]
                        instruccion_binario = instruccion_binario.replace("cc",Z80Table.tcc[regs[0]])
                        instruccion_binario = instruccion_binario.replace("nn",direct)
                    else:
                        if regs[0] in Z80Table.tcc:
                            instruccion_no_tag = Z80Table.tA9["JPC"]
                            tagged = "-" + regs[1]
                            instruccion_no_tag = instruccion_no_tag.replace("cc",Z80Table.tcc[regs[0]])
                            instruccion_no_tag = instruccion_no_tag.replace("nn",tagged)
                            contador_loc = hex(int(CL))[2:].zfill(4)
                            instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                            seg_pasada[no_linea] = regs[1]
                            CL = CL + 3
                            if ins_large < 6:
                                ins_large = 6

                elif coma == -1: #JP nn
                    if subins[1] in etiquetas:
                        instruccion_binario = Z80Table.tA9["JPN"]
                        direct = etiquetas[subins[1]]
                        direct = direct.zfill(16)
                        direct = direct[len(direct)//2:] + direct[:len(direct)//2]
                        instruccion_binario = instruccion_binario.replace("nn",direct)
                    else:
                        instruccion_no_tag = Z80Table.tA9["JPN"]
                        tagged = "-" + subins[1]
                        instruccion_no_tag = instruccion_no_tag.replace("nn",tagged)
                        contador_loc = hex(int(CL))[2:].zfill(4)
                        instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                        seg_pasada[no_linea] = subins[1]
                        CL = CL + 3
                        if ins_large < 6:
                            ins_large = 6
            
            elif subins[0] == "JR":
                coma = subins[1].find(",")
                if coma == -1: #JR e
                    if subins[1] in etiquetas:
                        instruccion_binario = Z80Table.tA9["JR"]
                        direct = etiquetas[subins[1]]
                        dista = int(direct, 2) - CL - 2
                        if dista < 0:
                            dist = abs(dista)
                            dist = str(bin(dist)[2:])
                            dist = dist.zfill(8)
                            complemento = format(int(dist, 2) ^ int("1"*len(dist), 2), 'b').zfill(len(dist))
                            complemento = str(int(complemento,2) + 1)
                            complemento = str(bin(int(complemento))[2:])
                            instruccion_binario = instruccion_binario.replace("e",complemento)
                        elif dista > 0:
                            dist = abs(dista)
                            dist = str(bin(dist)[2:]) 
                            instruccion_binario = instruccion_binario.replace("e",dist)

                    else:
                        instruccion_no_tag = Z80Table.tA9["JR"]
                        tagged = "$" + subins[1]
                        instruccion_no_tag = instruccion_no_tag.replace("e", tagged)
                        contador_loc = hex(int(CL))[2:].zfill(4)
                        instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                        seg_pasada[no_linea] = subins[1]
                        CL = CL + 2
                        if ins_large < 4:
                            ins_large = 4


                if coma != -1:
                    regis = subins[1].split(",")
                    if regis[0] in Z80Table.tcc_JR:
                        if regis[1] in etiquetas: 
                            ins = subins[0] + regis[0]
                            instruccion_binario = Z80Table.tA9[ins]
                            direct = etiquetas[regis[1]]
                            dista = int(direct, 2) - CL - 2
                            if dista < 0:
                                dist = abs(dista)
                                dist = str(bin(dist)[2:])
                                dist = dist.zfill(8)
                                complemento = format(int(dist, 2) ^ int("1"*len(dist), 2), 'b').zfill(len(dist))
                                complemento = str(int(complemento,2) + 1)
                                complemento = str(bin(int(complemento))[2:])
                                instruccion_binario = instruccion_binario.replace("e",complemento)
                        else:
                            ins = subins[0] + regis[0]
                            instruccion_no_tag = Z80Table.tA9[ins]
                            tagged = "$" + regis[1]
                            instruccion_no_tag = instruccion_no_tag.replace("e", tagged)
                            contador_loc = hex(int(CL))[2:].zfill(4)
                            instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                            seg_pasada[no_linea] = subins[1]
                            CL = CL + 2
                            if ins_large < 4:
                                ins_large = 4
                    
            elif (subins[0].find(",") != -1) and len(subins) == 1:
                data = subins[0].split(",")
                if data[1] in etiquetas:
                    instruccion_binario = Z80Table.tA9["DJNZ"]
                    direct = etiquetas[data[1]]
                    dista = int(direct, 2) - CL - 2
                    dist = abs(dista)
                    dist = str(bin(dist)[2:])
                    dist = dist.zfill(8)
                    complemento = format(int(dist, 2) ^ int("1"*len(dist), 2), 'b').zfill(len(dist))
                    complemento = str(int(complemento,2) + 1)
                    complemento = str(bin(int(complemento))[2:])
                    instruccion_binario = instruccion_binario.replace("e",complemento)
                else:
                    instruccion_no_tag = Z80Table.tA9["DJNZ"]
                    tagged = "R" + data[1]
                    instruccion_no_tag = instruccion_no_tag.replace("e", tagged)
                    contador_loc = hex(int(CL))[2:].zfill(4)
                    instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                    seg_pasada[no_linea] = subins[1]
                    CL = CL + 2
                    if ins_large < 4:
                        ins_large = 4

            elif subins[0] == "CALL":
                coma = subins[1].find(",")
                if coma == -1:
                    if subins[1] in etiquetas:
                        instruccion_binario = Z80Table.tA10["CALLN"]
                        direct = etiquetas[subins[1]]
                        direct = direct.zfill(16)
                        direct = direct[len(direct)//2:] + direct[:len(direct)//2]
                        instruccion_binario = instruccion_binario.replace("nn",direct)
                    else:
                        instruccion_no_tag = Z80Table.tA10["CALLN"]
                        tagged = "-" + subins[1]
                        instruccion_no_tag = instruccion_no_tag.replace("nn",tagged)
                        contador_loc = hex(int(CL))[2:].zfill(4)
                        instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                        seg_pasada[no_linea] = subins[1]
                        CL = CL + 3
                        if ins_large < 6:
                            ins_large = 6
                elif coma != -1:
                    regs = subins[1].split(",")
                    if regs[0] in Z80Table.tcc and regs[1] in etiquetas:
                        instruccion_binario = Z80Table.tA10["CALLC"]
                        direct = etiquetas[regs[1]]
                        direct = direct.zfill(16)
                        direct = direct[len(direct)//2:] + direct[:len(direct)//2]
                        instruccion_binario = instruccion_binario.replace("cc",Z80Table.tcc[regs[0]])
                        instruccion_binario = instruccion_binario.replace("nn",direct)
                    else:
                        if regs[0] in Z80Table.tcc:
                            instruccion_no_tag = Z80Table.tA10["CALLC"]
                            tagged = "-" + regs[1]
                            instruccion_no_tag = instruccion_no_tag.replace("cc",Z80Table.tcc[regs[0]])
                            instruccion_no_tag = instruccion_no_tag.replace("nn",tagged)
                            contador_loc = hex(int(CL))[2:].zfill(4)
                            instruccion_no_tag = contador_loc +"|"+ instruccion_no_tag
                            seg_pasada[no_linea] = regs[1]
                            CL = CL + 3
                            if ins_large < 6:
                                ins_large = 6
            #RET        
            elif subins[0] == "RET":
                if len(subins) == 1:
                    instruccion_binario = Z80Table.tA10["RET"]
                elif len(subins) == 2:
                    if subins[1] in Z80Table.tcc:
                        instruccion_binario = Z80Table.tA10["RETC"]
                        instruccion_binario = instruccion_binario.replace("cc",Z80Table.tcc[subins[1]])
            
            elif (subins[0] == "RETI" or subins[0] == "RETN") and len(subins) == 1:
                instruccion_binario = Z80Table.tA10[subins[0]]

            elif subins[0] == "RST" and len(subins) == 2:
                if subins[1] in Z80Table.t_tA10:
                    instruccion_binario = Z80Table.tA10["RST"]
                    instruccion_binario = instruccion_binario.replace("t",Z80Table.t_tA10[subins[10]])

            #En caso de encontrar un error indica en que linea y finaliza
            else:
                respuesta_error = "Error en la linea " + str(no_linea)
                eti_respuesta.config(text=respuesta_error)
                ventana.after(3000,resetear_etiqueta)
                bug_flag = True
                break

            if len(instruccion_binario) > 0:
                ins_hex = utils.transformar(instruccion_binario)
                codigo.append(utils.generar_codigo(CL, ins_hex))
                CL = CL + int(len(ins_hex)/2)
                if int(len(ins_hex)) > ins_large:
                    ins_large = int(len(ins_hex))
            elif len(instruccion_no_tag) > 0:
                codigo.append(instruccion_no_tag)
            else:
                bug_flag = True
                break



        #Manejo de etiquetas
        if not bug_flag:
            for line in seg_pasada:
                lineT = codigo[line-1]
                reemplazoP = lineT.find("-")
                reemplazoR = lineT.find("$")
                #JP
                if reemplazoP != -1:
                    separador = lineT.find("|")
                    contador_loca = lineT[:separador]
                    inst_tag = lineT[separador+1:reemplazoP]
                    tag_nm = lineT[reemplazoP+1:]
                    tag_nm = tag_nm.strip()
                    tag_cl = etiquetas[tag_nm]
                    tag_cl = tag_cl.zfill(16)
                    tag_cl = tag_cl[len(tag_cl)//2:] + tag_cl[:len(tag_cl)//2]
                    inst_filled = inst_tag + tag_cl
                    inst_hex = utils.transformar(inst_filled)
                    codigo[line-1] = contador_loca.upper() + "    " + inst_hex.upper()
                #JR
                elif reemplazoR != -1:
                    separador = lineT.find("|")
                    contador_loca = lineT[:separador]
                    inst_tag = lineT[separador+1:reemplazoR]
                    tag_nm = lineT[reemplazoR+1:]
                    tag_nm = tag_nm.strip()
                    tag_cl = etiquetas[tag_nm]
                    dista = int(tag_cl, 2) - int(contador_loca, 16) - 2
                    dista = (str(bin(dista)[2:])).zfill(8)
                    inst_filled = inst_tag + dista              
                    inst_hex = utils.transformar(inst_filled)
                    codigo[line-1] = contador_loca.upper() + "    " + inst_hex.upper()


        #Si el programa no encontro errores finaliza y escribe el codigo
        if not bug_flag:
            arc_lst = open(archivo_lst,'w')
            ins_large = ins_large + 9
            lineas_escribir = len(codigo)
            escritura = ""
            for i in range(0, lineas_escribir, 1):
                cadena_arc = " " + codigo[i].ljust(ins_large) + "    " + instruction[i] + "\n"
                escritura += cadena_arc
            if len(etiquetas) > 0:
                escritura += "\nTabla de simbolos\n"
                for linea in etiquetas:
                    cont_tag = etiquetas[linea]
                    cont_tag = format(int(cont_tag, 2), "x")
                    if len(cont_tag)%2 != 0:
                        cont_tag = "0" + cont_tag
                    cont_tag = cont_tag.zfill(4)
                    writing = cont_tag.upper() + "    "+linea + "\n"
                    escritura += writing

            arc_lst.write(escritura)
            arc_lst.close()
            generar_codigo_hex(codigo, nombre)
            respuesta = "Traduccion exitosa"
            eti_respuesta.config(text=respuesta)
            ventana.after(3000,resetear_etiqueta)


# genera el codigo hex de la forma :llaaaatt[dd...]cc
# donde:
# : es el signo dos puntos que comienza cada registro Intel HEX.
# ll es el campo de longitud de registro que representa el número de bytes de datos (dd) en el registro.
# aaaa es el campo de dirección que representa la dirección de inicio para los datos subsiguientes en el registro.
# tt es el campo que representa el tipo de registro HEX, que puede ser uno de los siguientes:
# 00 - registro de datos
# 01 - registro de fin de archivo
# 02 - registro de dirección de segmento extendido
# 04 - registro de dirección lineal extendida
# 05 - registro de inicio de dirección lineal (solo MDK-ARM)
# dd es un campo de datos que representa un byte de datos. Un registro puede tener varios bytes de datos. El número de bytes de datos en el registro debe coincidir con el número especificado en el campo ll.
# cc es el campo de verificación que representa el código de verificación del registro. El código de verificación se calcula sumando los valores de todos los pares de dígitos hexadecimales en el registro módulo 256 y tomando el complemento a dos.

def generar_codigo_hex(codigo:list, nombre_archivo:str):
    LOCALIDAD_INICIAL = "0000"

    registros_datos = []
    localidad_origen = LOCALIDAD_INICIAL

    data = ""
    for instruccion in codigo:
        data += instruccion.split()[1]
    contador_pares_hex = len(data)//2

    # Se itera en cachos, para tener pares hexagesimales de 16 en 16
    for i in range(0, len(data), 32): 
        registro = data[i:i+32] # cacho de 16 bytes hex porque lo mas que se puede en una linea en el .hex son 16 pares hexadecimales
        contador_pares_hex = len(registro)//2 # entre dos para obtener la cantidad de pares
        contador_pares_hex_str = str(hex(contador_pares_hex)) 
        contador_pares_hex_str = contador_pares_hex_str[2:] # eliminar '0x'
        contador_pares_hex_str_justificado = contador_pares_hex_str.rjust(2, '0') # justificar con 00, por ejemplo hex 8 se convierte en hex 08
        registro = f'{contador_pares_hex_str_justificado}{localidad_origen}00{registro}'
        registro = ':' + registro + checksum(registro)
        registros_datos.append(registro)
        
        localidad_origen = hex(int(localidad_origen, 16) + contador_pares_hex)
        localidad_origen = str(localidad_origen)[2:]
        localidad_origen = localidad_origen.zfill(4).upper()
        

    generar_archivo_hex(registros_datos, nombre_archivo)

def generar_archivo_hex(registros_datos:list, nombre_archivo:str):
    REGISTRO_EOF = ":00000001FF" # esta cadena siempre será el ultimo registro de información en el archivo.hex

    archivo_hex = open(nombre_archivo + ".hex", 'w')

    for registro in registros_datos:
        archivo_hex.write(registro+'\n')
    
    archivo_hex.write(REGISTRO_EOF+'\n')
    archivo_hex.close()

# Ultimo par de cada registro en el archivo.hex es el byte de checksum
def checksum(data:str):
    checksum = 0
    for par_hex in range(0, len(data), 2):
        checksum += int(data[par_hex:par_hex+2], 16) # Se suman todos los pares de la linea
    
    checksum_binary = bin((checksum%256)) # Se saca modulo 256 de la suma
    checksum_binary = checksum_binary[2:] # eliminar '0b'

    return comp_dos(checksum_binary).upper().zfill(2) # Se utiliza el complemento a dos

def comp_dos(binary:str):
    comp_uno = ""
    # intercambiar 1s por 0s y viceversa
    for i in range(len(binary)):
        if binary[i] == '0': comp_uno += '1'
        else: comp_uno += '0'

    # sumar 1
    comp_dos = int(comp_uno, 2) + 1
    comp_dos_hex = hex(comp_dos)
    return comp_dos_hex[2:] # eliminar '0x'

def resetear_etiqueta():
    eti_respuesta.config(text="")

ventana = Tk()
ventana.title("Traductor Mnemonico-Hexadecimal")
ventana.geometry("400x150")
boton = Button(ventana, text="Seleccionar archivo", command=on_button_click)
boton.place(relx=0.5, rely=0.5, anchor=CENTER)
boton.pack()
eti_respuesta = Label(ventana,text="")
eti_respuesta.pack()
ventana.mainloop()