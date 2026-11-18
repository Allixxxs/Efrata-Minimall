def main():
    from inicializar_datos import inicializar_datos
    inicializar_datos()
    from frontend.app import ejecutar_interfaz
    ejecutar_interfaz()

if __name__ == "__main__":
    main()
