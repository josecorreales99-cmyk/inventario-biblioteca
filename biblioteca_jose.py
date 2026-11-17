PLAZO_DIAS = 7
TARIFA_DIARIA = 1000
LIMITE_LIBROS = 3


catalogo = {}

socios = {}

registro_prestamos = []


control = {
    "dia_hoy": 1,
    "proximo_codigo_libro": 1,
    "proximo_num_prestamo": 1,
}



def leer_cadena(pregunta):
    """Pide un texto al usuario. Si se cierra la entrada (Ctrl+C / Ctrl+D)
    el programa termina de forma ordenada, sin mostrar errores rojos."""
    try:
        return input(pregunta).strip()
    except (EOFError, KeyboardInterrupt):
        print("\n\nSe interrumpió la entrada. Cerrando el programa. ¡Hasta pronto!")
        raise SystemExit


def leer_cadena_obligatoria(pregunta):
    """Repite la pregunta hasta que el usuario escriba algo."""
    while True:
        entrada = leer_cadena(pregunta)
        if entrada != "":
            return entrada
        print("  [!] Este dato no puede quedar vacío. Intente de nuevo.")


def leer_numero(pregunta, limite_inferior, limite_superior):
    """Pide un número entero entre minimo y maximo (inclusive).
    Repite hasta que el usuario escriba un valor válido."""
    while True:
        entrada = leer_cadena(pregunta)
        try:
            valor_ingresado = int(entrada)
        except ValueError:
            print("  [!] Debe escribir un número entero (por ejemplo: 3).")
            continue
        if valor_ingresado < limite_inferior or valor_ingresado > limite_superior:
            print(f"  [!] El número debe estar entre {limite_inferior} y {limite_superior}.")
            continue
        return valor_ingresado


def leer_nombre(pregunta):
    """Pide un nombre que contenga solo letras y espacios."""
    while True:
        nombre_completo = leer_cadena_obligatoria(pregunta)
        if nombre_completo.replace(" ", "").isalpha():
            return nombre_completo.title()
        print("  [!] El nombre solo puede tener letras y espacios.")


def leer_cedula(pregunta):
    """Pide un documento: solo dígitos, entre 5 y 12 caracteres."""
    while True:
        cedula = leer_cadena_obligatoria(pregunta)
        if cedula.isdigit() and 5 <= len(cedula) <= 12:
            return cedula
        print("  [!] El documento debe tener solo números (entre 5 y 12 dígitos).")


def preguntar_si_no(pregunta):
    """Pregunta sí/no. Devuelve True si el usuario responde que sí."""
    while True:
        contestacion = leer_cadena(pregunta + " (s/n): ").lower()
        if contestacion in ("s", "si", "sí"):
            return True
        if contestacion in ("n", "no"):
            return False
        print("  [!] Responda con 's' para sí o 'n' para no.")


def obtener_recargo(registro):
    """Calcula la multa de un préstamo activo según el día actual.
    Si no hay retraso, la multa es 0."""
    dias_tarde = control["dia_hoy"] - registro["dia_tope"]
    if dias_tarde > 0:
        return dias_tarde * TARIFA_DIARIA
    return 0


def prestamos_pendientes_de(cedula):
    """Devuelve la lista de préstamos sin devolver de un usuario."""
    pendientes = []
    for registro in registro_prestamos:
        if registro["cedula"] == cedula and not registro["entregado"]:
            pendientes.append(registro)
    return pendientes


def dar_formato_pesos(importe):
    """Da formato a un valor en pesos: 12000 -> $12.000"""
    return "$" + f"{importe:,}".replace(",", ".")


def agregar_libro():
    print("\n--- REGISTRAR LIBRO ---")
    nombre_libro = leer_cadena_obligatoria("Título del libro: ").title()
    escritor = leer_nombre("Autor del libro: ")

   
    for codigo_libro, info in catalogo.items():
        if info["nombre_libro"].lower() == nombre_libro.lower() and info["escritor"].lower() == escritor.lower():
            print(f"  Ese libro ya existe (código {codigo_libro}).")
            if preguntar_si_no("¿Desea agregar más copias?"):
                unidades = leer_numero("¿Cuántas copias nuevas? (1-50): ", 1, 50)
                info["ejemplares_totales"] += unidades
                info["ejemplares_libres"] += unidades
                print(f"  ✔ Copias agregadas. Total: {info['ejemplares_totales']}.")
            return

    ejemplares = leer_numero("Número de copias (1-50): ", 1, 50)
    codigo_libro = control["proximo_codigo_libro"]
    catalogo[codigo_libro] = {
        "nombre_libro": nombre_libro,
        "escritor": escritor,
        "ejemplares_totales": ejemplares,
        "ejemplares_libres": ejemplares,
    }
    control["proximo_codigo_libro"] += 1
    print(f"  ✔ Libro registrado con el código {codigo_libro}.")


def agregar_socio():
    print("\n--- REGISTRAR USUARIO ---")
    cedula = leer_cedula("Documento del usuario (solo números): ")
    if cedula in socios:
        print(f"  [!] Ya existe un usuario con ese documento: {socios[cedula]['nombre_completo']}.")
        return
    nombre_completo = leer_nombre("Nombre completo: ")
    socios[cedula] = {"nombre_completo": nombre_completo, "saldo_pendiente": 0}
    print(f"  ✔ Usuario {nombre_completo} registrado correctamente.")


def mostrar_catalogo():
    print("\n--- LISTA DE LIBROS ---")
    if len(catalogo) == 0:
        print("  Aún no hay libros registrados.")
        return
    print(f"  {'Cód':<5}{'Título':<32}{'Autor':<22}{'Disponibles'}")
    print("  " + "-" * 70)
    for codigo_libro, info in catalogo.items():
        libres = f"{info['ejemplares_libres']}/{info['ejemplares_totales']}"
        print(f"  {codigo_libro:<5}{info['nombre_libro'][:30]:<32}{info['escritor'][:20]:<22}{libres}")


def mostrar_socios():
    print("\n--- LISTA DE USUARIOS ---")
    if len(socios) == 0:
        print("  Aún no hay usuarios registrados.")
        return
    print(f"  {'Documento':<15}{'Nombre':<28}{'Libros':<8}{'Deuda'}")
    print("  " + "-" * 62)
    for cedula, info in socios.items():
        unidades = len(prestamos_pendientes_de(cedula))
        print(f"  {cedula:<15}{info['nombre_completo'][:26]:<28}{unidades:<8}{dar_formato_pesos(info['saldo_pendiente'])}")


def mostrar_pendientes():
    print(f"\n--- PRÉSTAMOS ACTIVOS (hoy es el día {control['dia_hoy']}) ---")
    existen_pendientes = False
    for registro in registro_prestamos:
        if registro["entregado"]:
            continue
        existen_pendientes = True
        nombre_libro = catalogo[registro["codigo_libro"]]["nombre_libro"]
        nombre_completo = socios[registro["cedula"]]["nombre_completo"]
        recargo = obtener_recargo(registro)
        if recargo > 0:
            situacion = f"ATRASADO - multa actual {dar_formato_pesos(recargo)}"
        else:
            dias_restantes = registro["dia_tope"] - control["dia_hoy"]
            situacion = f"a tiempo (faltan {dias_restantes} día(s))"
        print(f"  Préstamo #{registro['num_prestamo']}: '{nombre_libro}' -> {nombre_completo}")
        print(f"      Entrega límite: día {registro['dia_tope']} | {situacion}")
    if not existen_pendientes:
        print("  No hay préstamos activos.")


def realizar_prestamo():
    print("\n--- PRESTAR LIBRO ---")
    if len(catalogo) == 0 or len(socios) == 0:
        print("  [!] Primero debe registrar al menos un libro y un usuario.")
        return

    cedula = leer_cedula("Documento del usuario: ")
    if cedula not in socios:
        print("  [!] No existe un usuario con ese documento. Regístrelo primero (opción 2).")
        return
    socio = socios[cedula]

   
    if socio["saldo_pendiente"] > 0:
        print(f"  [!] {socio['nombre_completo']} debe {dar_formato_pesos(socio['saldo_pendiente'])} de multas.")
        print("      Debe pagarlas antes de pedir otro libro (opción 8).")
        return
    pendientes = prestamos_pendientes_de(cedula)
    if len(pendientes) >= LIMITE_LIBROS:
        print(f"  [!] {socio['nombre_completo']} ya tiene {LIMITE_LIBROS} libros prestados (el máximo).")
        return

    mostrar_catalogo()
    codigo_libro = leer_numero("Código del libro a prestar: ", 1, 999999)
    if codigo_libro not in catalogo:
        print("  [!] Ese código de libro no existe.")
        return
    ejemplar = catalogo[codigo_libro]
    if ejemplar["ejemplares_libres"] <= 0:
        print(f"  [!] No quedan copias disponibles de '{ejemplar['nombre_libro']}'.")
        return
    for registro in pendientes:
        if registro["codigo_libro"] == codigo_libro:
            print("  [!] Este usuario ya tiene prestado ese mismo libro.")
            return

    nuevo_prestamo = {
        "num_prestamo": control["proximo_num_prestamo"],
        "codigo_libro": codigo_libro,
        "cedula": cedula,
        "dia_salida": control["dia_hoy"],
        "dia_tope": control["dia_hoy"] + PLAZO_DIAS,
        "entregado": False,
        "recargo": 0,
    }
    registro_prestamos.append(nuevo_prestamo)
    control["proximo_num_prestamo"] += 1
    ejemplar["ejemplares_libres"] -= 1
    print(f"  ✔ Préstamo #{nuevo_prestamo['num_prestamo']} registrado: '{ejemplar['nombre_libro']}' para {socio['nombre_completo']}.")
    print(f"    Debe devolverlo a más tardar el día {nuevo_prestamo['dia_tope']}.")


def recibir_devolucion():
    print("\n--- DEVOLVER LIBRO ---")
    cedula = leer_cedula("Documento del usuario: ")
    if cedula not in socios:
        print("  [!] No existe un usuario con ese documento.")
        return
    pendientes = prestamos_pendientes_de(cedula)
    if len(pendientes) == 0:
        print("  Este usuario no tiene libros prestados.")
        return

    print(f"  Libros prestados a {socios[cedula]['nombre_completo']}:")
    numeros_permitidos = []
    for registro in pendientes:
        nombre_libro = catalogo[registro["codigo_libro"]]["nombre_libro"]
        print(f"    Préstamo #{registro['num_prestamo']}: '{nombre_libro}' (límite: día {registro['dia_tope']})")
        numeros_permitidos.append(registro["num_prestamo"])

    valor_ingresado = leer_numero("Número del préstamo a devolver: ", 1, 999999)
    if valor_ingresado not in numeros_permitidos:
        print("  [!] Ese número de préstamo no corresponde a este usuario.")
        return

   
    seleccionado = None
    for registro in pendientes:
        if registro["num_prestamo"] == valor_ingresado:
            seleccionado = registro
            break

    recargo = obtener_recargo(seleccionado)
    seleccionado["entregado"] = True
    seleccionado["recargo"] = recargo
    seleccionado["dia_entrega"] = control["dia_hoy"]
    catalogo[seleccionado["codigo_libro"]]["ejemplares_libres"] += 1
    print("  ✔ Libro devuelto correctamente.")
    if recargo > 0:
        socios[cedula]["saldo_pendiente"] += recargo
        cantidad_dias = recargo // TARIFA_DIARIA
        print(f"  [!] Devolución tardía: {cantidad_dias} día(s) de retraso. Multa: {dar_formato_pesos(recargo)}.")
        print(f"      Deuda total del usuario: {dar_formato_pesos(socios[cedula]['saldo_pendiente'])}.")
    else:
        print("  Devuelto a tiempo, sin multa. ¡Gracias!")


def gestionar_recargos():
    print("\n--- MULTAS ---")
    cedula = leer_cedula("Documento del usuario: ")
    if cedula not in socios:
        print("  [!] No existe un usuario con ese documento.")
        return
    socio = socios[cedula]

    
    acumulado_actual = 0
    for registro in prestamos_pendientes_de(cedula):
        acumulado_actual += obtener_recargo(registro)
    print(f"  Usuario: {socio['nombre_completo']}")
    print(f"  Deuda por libros ya devueltos: {dar_formato_pesos(socio['saldo_pendiente'])}")
    print(f"  Multa que va corriendo por libros atrasados: {dar_formato_pesos(acumulado_actual)}")

    if socio["saldo_pendiente"] > 0 and preguntar_si_no("¿Desea registrar el pago de la deuda?"):
        abono = leer_numero(
            f"Valor a pagar (máximo {socio['saldo_pendiente']}): ", 1, socio["saldo_pendiente"]
        )
        socio["saldo_pendiente"] -= abono
        print(f"  ✔ Pago registrado. Deuda restante: {dar_formato_pesos(socio['saldo_pendiente'])}.")


def pasar_dias():
    print("\n--- AVANZAR DÍAS ---")
    print(f"  Hoy es el día {control['dia_hoy']}.")
    cantidad_dias = leer_numero("¿Cuántos días desea avanzar? (1-365): ", 1, 365)
    control["dia_hoy"] += cantidad_dias
    print(f"  ✔ Ahora es el día {control['dia_hoy']}.")



def precargar_datos():
    """Carga algunos libros y usuarios para que el programa no arranque vacío."""
    muestras = [
        ("Cien Años De Soledad", "Gabriel Garcia Marquez", 2),
        ("El Coronel No Tiene Quien Le Escriba", "Gabriel Garcia Marquez", 1),
        ("Rayuela", "Julio Cortazar", 3),
    ]
    for nombre_libro, escritor, ejemplares in muestras:
        codigo_libro = control["proximo_codigo_libro"]
        catalogo[codigo_libro] = {
            "nombre_libro": nombre_libro,
            "escritor": escritor,
            "ejemplares_totales": ejemplares,
            "ejemplares_libres": ejemplares,
        }
        control["proximo_codigo_libro"] += 1
    socios["1001234567"] = {"nombre_completo": "Maria Lopez", "saldo_pendiente": 0}
    socios["1007654321"] = {"nombre_completo": "Carlos Perez", "saldo_pendiente": 0}


def imprimir_menu():
    print("\n" + "=" * 46)
    print("   BIBLIOTECA DEL BARRIO  -  Día actual:", control["dia_hoy"])
    print("=" * 46)
    print(" 1. Registrar libro")
    print(" 2. Registrar usuario")
    print(" 3. Ver libros")
    print(" 4. Ver usuarios")
    print(" 5. Prestar libro")
    print(" 6. Devolver libro")
    print(" 7. Ver préstamos activos")
    print(" 8. Consultar / pagar multas")
    print(" 9. Avanzar días (simulación)")
    print(" 0. Salir")


def iniciar():
    precargar_datos()
    print("¡Bienvenido al sistema de la Biblioteca del Barrio!")
    while True:
        imprimir_menu()
        eleccion = leer_numero("Elija una opción (0-9): ", 0, 9)
        
        try:
            if eleccion == 1:
                agregar_libro()
            elif eleccion == 2:
                agregar_socio()
            elif eleccion == 3:
                mostrar_catalogo()
            elif eleccion == 4:
                mostrar_socios()
            elif eleccion == 5:
                realizar_prestamo()
            elif eleccion == 6:
                recibir_devolucion()
            elif eleccion == 7:
                mostrar_pendientes()
            elif eleccion == 8:
                gestionar_recargos()
            elif eleccion == 9:
                pasar_dias()
            elif eleccion == 0:
                if preguntar_si_no("¿Seguro que desea salir?"):
                    print("Gracias por usar el sistema. ¡Hasta pronto!")
                    break
        except Exception:
            print("  [!] Ocurrió un problema inesperado con esa opción. Intente de nuevo.")


iniciar()