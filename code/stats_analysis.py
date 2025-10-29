import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import folium
from folium import plugins
import numpy as np

# Configuración de estilo
plt.style.use('seaborn-v0_8')
print("✅ Librerías importadas correctamente")

# PASO 3.1: Cargar y preparar los datos
def load_cloud_data():
    """
    Carga los datos de los proveedores de nube
    Si no existe el archivo CSV, crea datos de ejemplo
    """
    try:
        # Intenta cargar desde archivo
        df = pd.read_csv('cloud_providers_data.csv')
        print("📊 Datos cargados desde archivo CSV")
    except FileNotFoundError:
        # Datos de ejemplo si no existe el archivo
        print("⚠️ Archivo no encontrado. Usando datos de ejemplo...")
        data = {
            'provider': ['AWS', 'AWS', 'Google Cloud', 'Google Cloud', 'Azure', 'Azure', 'AWS', 'Azure'],
            'region': ['us-east-1', 'eu-central-1', 'us-central1', 'europe-west4', 'East US', 'West Europe', 'ap-south-1', 'Central India'],
            'country': ['USA', 'Germany', 'USA', 'Netherlands', 'USA', 'Netherlands', 'India', 'India'],
            'latitude': [39.8283, 51.1657, 41.8781, 52.1326, 37.0902, 52.1326, 20.5937, 20.5937],
            'longitude': [-98.5795, 10.4515, -93.0977, 5.2913, -95.7129, 5.2913, 78.9629, 78.9629],
            'scalability_score': [95, 92, 90, 88, 93, 91, 85, 87],
            'cost_score': [70, 75, 65, 72, 78, 76, 80, 82],
            'availability_zones': [6, 3, 4, 3, 5, 4, 3, 3],
            'service_level': [99.99, 99.95, 99.95, 99.9, 99.99, 99.95, 99.9, 99.9]
        }
        df = pd.DataFrame(data)
        df.to_csv('cloud_providers_data.csv', index=False)
        print("📝 Archivo de ejemplo creado: cloud_providers_data.csv")
    
    return df

# Cargar datos
cloud_df = load_cloud_data()
print(f"📈 Total de regiones cargadas: {len(cloud_df)}")
print(f"🌍 Proveedores únicos: {cloud_df['provider'].unique()}")

# PASO 3.2: Crear mapa estático con geopandas
def create_static_map(df):
    """Crea un mapa estático con las ubicaciones de los proveedores"""
    print("🗺️ Creando mapa estático...")
    
    # Convertir DataFrame a GeoDataFrame
    gdf = gpd.GeoDataFrame(
        df, 
        geometry=gpd.points_from_xy(df.longitude, df.latitude),
        crs="EPSG:4326"
    )
    
    # Crear figura con subplots
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()
    
    # Configurar colores por proveedor
    provider_colors = {'AWS': '#FF9900', 'Google Cloud': '#4285F4', 'Azure': '#0078D4'}
    
    # Mapa 1: Distribución geográfica por proveedor
    for provider, color in provider_colors.items():
        provider_data = gdf[gdf['provider'] == provider]
        if not provider_data.empty:
            axes[0].scatter(provider_data.longitude, provider_data.latitude, 
                           c=color, label=provider, s=100, alpha=0.7, edgecolors='black')
    
    axes[0].set_title('Distribución Global de Proveedores de Cloud', fontsize=14, fontweight='bold')
    axes[0].legend()
    axes[0].set_xlabel('Longitud')
    axes[0].set_ylabel('Latitud')
    axes[0].grid(True, alpha=0.3)
    
    # Mapa 2: Puntuación de escalabilidad (tamaño del punto)
    for provider, color in provider_colors.items():
        provider_data = gdf[gdf['provider'] == provider]
        if not provider_data.empty:
            sizes = provider_data['scalability_score'] * 2
            axes[1].scatter(provider_data.longitude, provider_data.latitude, 
                           c=color, s=sizes, label=provider, alpha=0.6, edgecolors='black')
    
    axes[1].set_title('Escalabilidad por Región (Tamaño = Puntuación)', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].set_xlabel('Longitud')
    axes[1].set_ylabel('Latitud')
    
    # Mapa 3: Relación Costo-Escalabilidad
    scatter = axes[2].scatter(gdf['longitude'], gdf['latitude'], 
                             c=gdf['cost_score'], 
                             s=gdf['scalability_score'] * 2,
                             cmap='viridis', alpha=0.7)
    
    axes[2].set_title('Relación Costo-Escalabilidad', fontsize=14, fontweight='bold')
    axes[2].set_xlabel('Longitud')
    axes[2].set_ylabel('Latitud')
    plt.colorbar(scatter, ax=axes[2], label='Puntuación de Costo')
    
    # Mapa 4: Zonas de disponibilidad
    for provider, color in provider_colors.items():
        provider_data = gdf[gdf['provider'] == provider]
        if not provider_data.empty:
            sizes = provider_data['availability_zones'] * 30
            axes[3].scatter(provider_data.longitude, provider_data.latitude, 
                           c=color, s=sizes, label=provider, alpha=0.6, edgecolors='black')
    
    axes[3].set_title('Zonas de Disponibilidad (Tamaño = Número de Zonas)', fontsize=14, fontweight='bold')
    axes[3].legend()
    axes[3].set_xlabel('Longitud')
    axes[3].set_ylabel('Latitud')
    
    # Ajustar layout
    plt.tight_layout()
    plt.savefig('cloud_providers_analysis.png', dpi=300, bbox_inches='tight')
    print("💾 Mapa estático guardado como 'cloud_providers_analysis.png'")
    plt.show()

# PASO 3.3: Crear mapa interactivo con Folium
def create_interactive_map(df):
    """Crea un mapa interactivo con Folium"""
    print("🔄 Creando mapa interactivo...")
    
    # Centro del mapa (posición promedio)
    center_lat = df['latitude'].mean()
    center_lon = df['longitude'].mean()
    
    # Crear mapa base
    m = folium.Map(location=[center_lat, center_lon], zoom_start=2)
    
    # Configurar colores
    provider_colors = {'AWS': 'orange', 'Google Cloud': 'blue', 'Azure': 'lightblue'}
    
    # Añadir marcadores para cada región
    for idx, row in df.iterrows():
        # Calcular métricas combinadas
        value_score = (row['scalability_score'] + (100 - row['cost_score'])) / 2
        
        # Crear popup informativo
        popup_text = f"""
        <b>{row['provider']} - {row['region']}</b><br>
        <b>País:</b> {row['country']}<br>
        <b>Escalabilidad:</b> {row['scalability_score']}/100<br>
        <b>Costo:</b> {row['cost_score']}/100<br>
        <b>Zonas Disponibilidad:</b> {row['availability_zones']}<br>
        <b>Nivel Servicio:</b> {row['service_level']}%<br>
        <b>Puntuación Valor:</b> {value_score:.1f}/100
        """
        
        # Añadir marcador
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['availability_zones'] * 3,
            popup=folium.Popup(popup_text, max_width=300),
            tooltip=f"{row['provider']} - {row['region']}",
            color=provider_colors[row['provider']],
            fillColor=provider_colors[row['provider']],
            fillOpacity=0.6,
            weight=1
        ).add_to(m)
    
    # Añadir control de capas
    feature_groups = {}
    for provider in df['provider'].unique():
        feature_groups[provider] = folium.FeatureGroup(name=provider, show=True)
        m.add_child(feature_groups[provider])
    
    # Re-asignar marcadores a grupos
    for idx, row in df.iterrows():
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=row['availability_zones'] * 3,
            popup=folium.Popup(f"<b>{row['provider']}</b><br>{row['region']}", max_width=200),
            color=provider_colors[row['provider']],
            fillColor=provider_colors[row['provider']],
            fillOpacity=0.6
        ).add_to(feature_groups[row['provider']])
    
    # Añadir control de capas
    folium.LayerControl().add_to(m)
    
    # Guardar mapa interactivo
    m.save('cloud_providers_interactive_map.html')
    print("💾 Mapa interactivo guardado como 'cloud_providers_interactive_map.html'")
    
    return m

# PASO 3.4: Análisis y métricas
def generate_analysis_report(df):
    """Genera un reporte analítico de los datos"""
    print("\n" + "="*50)
    print("📊 REPORTE ANALÍTICO - PROVEEDORES DE CLOUD")
    print("="*50)
    
    # Métricas por proveedor
    for provider in df['provider'].unique():
        provider_data = df[df['provider'] == provider]
        print(f"\n🔹 {provider}:")
        print(f"   Regiones: {len(provider_data)}")
        print(f"   Escalabilidad promedio: {provider_data['scalability_score'].mean():.1f}")
        print(f"   Costo promedio: {provider_data['cost_score'].mean():.1f}")
        print(f"   Zonas disponibilidad promedio: {provider_data['availability_zones'].mean():.1f}")
        
        # Calcular score de valor (escalabilidad + relación costo)
        value_score = (provider_data['scalability_score'].mean() + 
                      (100 - provider_data['cost_score'].mean())) / 2
        print(f"   Puntuación de valor: {value_score:.1f}/100")
    
    # Análisis global
    print(f"\n🌍 MÉTRICAS GLOBALES:")
    print(f"   Total regiones analizadas: {len(df)}")
    print(f"   Escalabilidad global promedio: {df['scalability_score'].mean():.1f}")
    print(f"   Costo global promedio: {df['cost_score'].mean():.1f}")

# PASO 3.5: Ejecutar todo el pipeline
def main():
    """Función principal que ejecuta todo el pipeline"""
    print("🚀 Iniciando análisis de proveedores de cloud...")
    
    # Cargar datos
    df = load_cloud_data()
    
    # Mostrar preview de datos
    print("\n📋 Vista previa de datos:")
    print(df.head())
    
    # Generar mapas
    create_static_map(df)
    interactive_map = create_interactive_map(df)
    
    # Generar reporte analítico
    generate_analysis_report(df)
    
    print("\n✅ Análisis completado!")
    print("📁 Archivos generados:")
    print("   - cloud_providers_analysis.png (Mapa estático)")
    print("   - cloud_providers_interactive_map.html (Mapa interactivo)")
    print("   - cloud_providers_data.csv (Datos utilizados)")

# Ejecutar el análisis
if __name__ == "__main__":
    main()