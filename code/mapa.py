import pandas as pd
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
# from cartopy.mpl.geoaxes import GeoAxesSubplot
import numpy as np

# Configuración de la gráfica
plt.style.use('default')
plt.rcParams['figure.figsize'] = [15, 10]
plt.rcParams['font.size'] = 10

print("✅ Librerías importadas correctamente")

# PASO 1: Datos de ubicaciones de proveedores cloud
def crear_datos_cloud():
    """Crea el dataset con ubicaciones reales de data centers"""
    
    datos_cloud = {
        'provider': [
            'AWS', 'AWS', 'AWS', 'AWS', 'AWS', 'AWS', 'AWS', 'AWS',
            'Google Cloud', 'Google Cloud', 'Google Cloud', 'Google Cloud', 'Google Cloud', 'Google Cloud',
            'Azure', 'Azure', 'Azure', 'Azure', 'Azure', 'Azure', 'Azure'
        ],
        'region': [
            'N. Virginia', 'Oregón', 'California', 'Irlanda', 'Fráncfort', 'Tokio', 'Sídney', 'São Paulo',
            'Iowa', 'Carolina Sur', 'Bélgica', 'Londres', 'Tokio', 'Singapur',
            'Este de EE. UU.', 'Oeste de EE. UU.', 'Europa Norte', 'Europa Oeste', 'Japón Este', 'Este de Australia', 'Sur de Brasil'
        ],
        'country': [
            'USA', 'USA', 'USA', 'Ireland', 'Germany', 'Japan', 'Australia', 'Brazil',
            'USA', 'USA', 'Belgium', 'UK', 'Japan', 'Singapore',
            'USA', 'USA', 'Ireland', 'Netherlands', 'Japan', 'Australia', 'Brazil'
        ],
        'latitude': [
            38.13, 45.52, 36.77, 53.14, 50.11, 35.68, -33.86, -23.55,
            41.88, 33.84, 50.50, 51.51, 35.68, 1.35,
            37.09, 37.77, 53.14, 52.13, 35.68, -33.86, -23.55
        ],
        'longitude': [
            -78.45, -122.67, -119.42, -7.69, 8.68, 139.77, 151.21, -46.63,
            -93.10, -81.04, 4.47, -0.13, 139.77, 103.82,
            -95.71, -122.42, -7.69, 5.29, 139.77, 151.21, -46.63
        ],
        'market_share': [
            33, 33, 33, 33, 33, 33, 33, 33,
            11, 11, 11, 11, 11, 11,
            22, 22, 22, 22, 22, 22, 22
        ]
    }
    
    df = pd.DataFrame(datos_cloud)
    print(f"📊 Datos creados: {len(df)} ubicaciones de data centers")
    return df

# Cargar datos
cloud_df = crear_datos_cloud()

def crear_mapa_mundial(df):
    """Crea un solo mapa mundial con los puntos de todas las tecnologías"""
    
    # Configurar el mapa
    fig = plt.figure(figsize=(20, 12))
    ax = plt.axes(projection=ccrs.PlateCarree())
    # Asegurarse de que ax es un GeoAxes de Cartopy
    
    # Agregar características del mapa
    ax.add_feature(cfeature.COASTLINE, linewidth=0.8, alpha=0.8)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5, alpha=0.5)
    ax.add_feature(cfeature.LAND, facecolor='lightgray', alpha=0.4)
    ax.add_feature(cfeature.LAND, color='lightgray', alpha=0.4)
    
    # Definir colores y marcadores para cada proveedor
    proveedores_config = {
        'AWS': {'color': '#FF9900', 'marker': 'o', 'label': 'AWS (33% mercado)'},
        'Google Cloud': {'color': '#4285F4', 'marker': 's', 'label': 'Google Cloud (11% mercado)'},
        'Azure': {'color': '#0078D4', 'marker': '^', 'label': 'Azure (22% mercado)'}
    }
    
    # Graficar puntos para cada proveedor
    for proveedor, config in proveedores_config.items():
        datos_proveedor = df[df['provider'] == proveedor]
        
        ax.scatter(
            datos_proveedor['longitude'],
            datos_proveedor['latitude'],
            c=config['color'],
            marker=config['marker'],
            s=80,  # Tamaño fijo para todos los puntos
            label=config['label'],
            alpha=0.8,
            edgecolors='black',
            linewidth=0.5,
            transform=ccrs.PlateCarree()
        )
    
    # Configurar los límites del mapa (vista mundial)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())
    
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.5,
        color='gray',
        alpha=0.3,
        linestyle='--'
    )
    # Para Cartopy >=0.18, los atributos de etiquetas se acceden así:
    try:
        gl.top_labels = False
        gl.right_labels = False
    except AttributeError:
        gl.xlabel_style = {'size': 10, 'color': 'gray'}
        gl.ylabel_style = {'size': 10, 'color': 'gray'}
    gl.right_labels = False
    
    # Título y leyenda
    plt.title(
        'Distribución Global de Data Centers por Proveedor de Cloud\n',
        fontsize=16,
        fontweight='bold',
        pad=20
    )
    
    # Leyenda mejorada
    legend = plt.legend(
        loc='lower left',
        frameon=True,
        fancybox=True,
        shadow=True,
        framealpha=0.9,
        fontsize=12
    )
    legend.get_frame().set_facecolor('white')
    
    # Añadir texto informativo
    plt.figtext(
        0.02, 0.02,
        '• Los puntos representan regiones/zonas de disponibilidad principales\n• Tamaño del mercado basado en datos de 2024',
        fontsize=10,
        style='italic',
        color='gray'
    )
    
    # Ajustar layout
    plt.tight_layout()
    
    # Guardar la imagen
    plt.savefig('mapa_mundial_cloud.png', dpi=300, bbox_inches='tight', facecolor='white')
    print("💾 Mapa mundial guardado como 'mapa_mundial_cloud.png'")
    
    plt.show()
    
    return fig

# PASO 3: Mostrar información resumida
def mostrar_resumen(df):
    """Muestra un resumen de los datos en el mapa"""
    print("\n" + "="*60)
    print("📋 RESUMEN DE UBICACIONES EN EL MAPA")
    print("="*60)
    
    for proveedor in df['provider'].unique():
        datos_proveedor = df[df['provider'] == proveedor]
        print(f"\n🔹 {proveedor}:")
        print(f"   • Regiones: {len(datos_proveedor)}")
        print(f"   • Países: {', '.join(datos_proveedor['country'].unique())}")
        print(f"   • Cuota de mercado: {datos_proveedor['market_share'].iloc[0]}%")
    
    print(f"\n🌍 Total de ubicaciones en el mapa: {len(df)}")
    print("📍 Los puntos muestran las regiones principales de cada proveedor")

# PASO 4: Ejecutar el programa
def main():
    """Función principal"""
    print("🚀 Creando mapa mundial de proveedores cloud...")
    
    # Cargar datos
    df = crear_datos_cloud()
    
    # Mostrar resumen
    mostrar_resumen(df)
    
    # Crear y mostrar el mapa
    print("\n🎨 Generando visualización...")
    mapa = crear_mapa_mundial(df)
    
    print("\n✅ ¡Mapa mundial creado exitosamente!")
    print("📁 Archivo generado: 'mapa_mundial_cloud.png'")

# Ejecutar el programa
if __name__ == "__main__":
    main()