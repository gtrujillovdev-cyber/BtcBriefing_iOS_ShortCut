# Script para colaboradores: Prueba el bot sin desplegar en la nube
import main
import base64
import os

print("🚀 Iniciando prueba local del Briefing Bot...")

try:
    # 1. Ejecutar la función principal directamente
    response = main.briefing()
    
    print("\n✅ RESPUESTA RECIBIDA:")
    print("-" * 30)
    print(response.mensaje)
    print("-" * 30)

    # 2. Decodificar y guardar la imagen para ver si el gráfico está bien
    if response.imagen_base64:
        image_data = base64.b64decode(response.imagen_base64)
        filename = "test_output_grafico.png"
        
        with open(filename, "wb") as f:
            f.write(image_data)
            
        print(f"\n🖼️ Gráfico generado con éxito: {os.path.abspath(filename)}")
        print("👉 Abre ese archivo para verificar que el diseño es correcto.")
    else:
        print("\n⚠️ Alerta: No se ha generado imagen.")

except Exception as e:
    print(f"\n❌ ERROR EN LA PRUEBA:\n{str(e)}")
