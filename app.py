# app.py
# ============================================================
#  LA EVOLUCIÓN DEL SONIDO — Dashboard interactivo (beta 2.1.0)
#  Taller de Visualización de la Información · UDD
#  Dataset: Spotify 1921-2020 (muestra limpia del Certamen 2)
#  Ejecutar en local:  streamlit run app.py
#
#  Igual que en tips_app.py: Streamlit ejecuta este archivo de
#  ARRIBA A ABAJO cada vez que el usuario mueve un filtro.
# ============================================================

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from sklearn.cluster import KMeans

# ── 1. CONFIGURACIÓN DE LA PÁGINA ────────────────────────────
# Debe ser la primera instrucción de Streamlit del script.
st.set_page_config(
    page_title="La evolución del sonido",
    page_icon="🎵",
    layout="wide",
)

# ── 2. COLORES Y ESTILO COMPARTIDO ───────────────────────────
# Cada perfil de canciones tiene siempre el mismo color en todos
# los gráficos (consistencia visual).
PERFILES = ["Bailables y alegres", "Energéticas", "Acústicas y tranquilas",
            "Instrumentales", "Habladas"]
COLOR_PERFIL = dict(zip(PERFILES, ["#1DB954", "#E4572E", "#378ADD", "#7F77DD", "#BA7517"]))

# Variables sonoras usadas para segmentar (las mismas del Certamen 2)
VARS_SONORAS = ["danceability", "energy", "loudness", "speechiness", "acousticness",
                "instrumentalness", "liveness", "valence", "tempo"]

# Nombres legibles (con unidad) para ejes y tooltips
ETIQUETAS = {
    "danceability": "Bailabilidad (0-1)",
    "energy": "Energía (0-1)",
    "loudness": "Volumen (dB)",
    "speechiness": "Presencia de habla (0-1)",
    "acousticness": "Acústica (0-1)",
    "instrumentalness": "Instrumentalidad (0-1)",
    "liveness": "En vivo (0-1)",
    "valence": "Positividad (0-1)",
    "tempo": "Tempo (BPM)",
    "popularity": "Popularidad (0-100)",
    "duracion_min": "Duración (min)",
    "anio": "Año de lanzamiento",
}

LAYOUT = dict(
    plot_bgcolor="white", paper_bgcolor="white",
    font=dict(family="Inter,Arial,sans-serif", size=12),
    margin=dict(t=40, b=40, l=50, r=20),
    legend=dict(orientation="h", y=-0.25),
)

# ── 3. CARGA DE DATOS Y SEGMENTACIÓN ─────────────────────────
# @st.cache_data: Streamlit ejecuta la función UNA vez y guarda el
# resultado en memoria. Sin esto, cada vez que se mueve un filtro
# se volvería a leer el CSV y a correr K-Means (lento).
@st.cache_data
def cargar_datos():
    ruta = Path(__file__).parent / "data" / "canciones_limpias.csv"
    df = pd.read_csv(ruta)
    df["artista_principal"] = df["artista_principal"].fillna("Sin dato")
    df["explicito"] = df["explicit"].map({0: "No", 1: "Sí"})

    # Segmentación K-Means (misma lógica del Bloque 4 del Certamen 2):
    # 1) estandarizar, 2) K-Means con k=5, 3) nombrar cada grupo.
    X = df[VARS_SONORAS]
    X_esc = (X - X.mean()) / X.std()
    df["cluster"] = KMeans(n_clusters=5, random_state=2025).fit_predict(X_esc)

    # El número que asigna K-Means es arbitrario, así que se nombra
    # cada grupo según su perfil (el que más habla, el más instrumental...)
    medias = df.groupby("cluster")[VARS_SONORAS].mean()
    nombres = {}
    nombres[medias["speechiness"].idxmax()] = "Habladas"
    resto = medias.drop(index=list(nombres))
    nombres[resto["instrumentalness"].idxmax()] = "Instrumentales"
    resto = medias.drop(index=list(nombres))
    nombres[resto["energy"].idxmax()] = "Energéticas"
    resto = medias.drop(index=list(nombres))
    nombres[resto["danceability"].idxmax()] = "Bailables y alegres"
    resto = medias.drop(index=list(nombres))
    nombres[resto.index[0]] = "Acústicas y tranquilas"
    df["perfil"] = df["cluster"].map(nombres)
    return df


df = cargar_datos()

# ── 4. SIDEBAR — FILTROS GLOBALES ────────────────────────────
# Estos filtros afectan a TODOS los KPIs y gráficos.
with st.sidebar:
    st.title("🎵 Filtros")
    st.caption("Filtros globales: afectan todo el dashboard")

    anio_min, anio_max = st.slider(
        "Año de lanzamiento",
        min_value=int(df["anio"].min()),
        max_value=int(df["anio"].max()),
        value=(int(df["anio"].min()), int(df["anio"].max())),
    )

    perfiles_sel = st.multiselect(
        "Perfil de canción", options=PERFILES, default=PERFILES,
    )

    explicito = st.radio("Contenido explícito", ["Todos", "Sí", "No"])

    st.divider()
    st.caption(f"Muestra del dataset: {len(df):,} canciones")

# ── 5. APLICAR LOS FILTROS (pandas puro) ─────────────────────
mask = df["anio"].between(anio_min, anio_max) & df["perfil"].isin(perfiles_sel)
if explicito != "Todos":
    mask &= df["explicito"] == explicito
dff = df[mask]  # dff = dataframe filtrado

# ── 6. ENCABEZADO Y NARRATIVA ────────────────────────────────
st.title("La evolución del sonido")
st.markdown(
    "**Pregunta que responde este dashboard:** ¿cómo cambió el sonido de la música "
    "en Spotify entre 1921 y 2020 y qué perfiles de canciones se forman según "
    "sus características sonoras?"
)
st.caption(f"Mostrando {len(dff):,} de {len(df):,} canciones con los filtros aplicados")

# Si los filtros dejan la tabla vacía, se avisa y se detiene la app
# (así no fallan los promedios ni los gráficos).
if dff.empty:
    st.warning("No hay canciones con los filtros seleccionados. Ajusta el panel lateral.")
    st.stop()

# ── 7. KPIs ──────────────────────────────────────────────────
# El delta compara el valor filtrado contra el total SIN filtros.
k1, k2, k3, k4 = st.columns(4)
k1.metric("Canciones", f"{len(dff):,}",
          delta=f"{len(dff) / len(df) * 100:.0f}% de la muestra", delta_color="off")
k2.metric("Energía promedio", f"{dff['energy'].mean():.2f}",
          delta=f"{dff['energy'].mean() - df['energy'].mean():+.2f} vs total")
k3.metric("Popularidad promedio", f"{dff['popularity'].mean():.1f}",
          delta=f"{dff['popularity'].mean() - df['popularity'].mean():+.1f} vs total")
k4.metric("Duración promedio", f"{dff['duracion_min'].mean():.1f} min",
          delta=f"{dff['duracion_min'].mean() - df['duracion_min'].mean():+.1f} min vs total")

st.divider()

# ── 8. PESTAÑAS ──────────────────────────────────────────────
tab1, tab2 = st.tabs(["📈 Panorama y evolución", "🧩 Segmentación (beta)"])

# ----- Pestaña 1: univariado + temporal -----
with tab1:
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Distribución de una variable sonora")
        # CONTROL LOCAL: este selectbox solo afecta a este gráfico
        var_hist = st.selectbox(
            "Variable", VARS_SONORAS, index=1, key="sel_hist",
            format_func=lambda v: ETIQUETAS[v],
        )
        fig = px.histogram(
            dff, x=var_hist, nbins=30, color_discrete_sequence=["#1DB954"],
            labels={var_hist: ETIQUETAS[var_hist], "count": "Canciones"},
            title=f"Distribución de {ETIQUETAS[var_hist]}",
        )
        fig.update_layout(**LAYOUT, yaxis_title="Canciones")
        st.plotly_chart(fig, width="stretch")

    with col2:
        st.subheader("Evolución en el tiempo")
        # CONTROL LOCAL: elige qué variable se muestra en el eje Y
        var_tiempo = st.selectbox(
            "Variable", VARS_SONORAS + ["popularity"], index=1, key="sel_tiempo",
            format_func=lambda v: ETIQUETAS[v],
        )
        por_anio = (dff.groupby("anio")
                       .agg(promedio=(var_tiempo, "mean"), canciones=("id", "count"))
                       .reset_index())
        fig = px.line(
            por_anio, x="anio", y="promedio", markers=True,
            color_discrete_sequence=["#1DB954"],
            hover_data={"canciones": True, "promedio": ":.2f"},
            labels={"anio": "Año de lanzamiento", "promedio": ETIQUETAS[var_tiempo],
                    "canciones": "Canciones"},
            title=f"{ETIQUETAS[var_tiempo]}: promedio por año",
        )
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, width="stretch")
        st.caption("Los años antiguos tienen pocas canciones en la muestra (ver tooltip).")

# ----- Pestaña 2: primera versión de la segmentación -----
with tab2:
    st.markdown(
        "Las canciones se agruparon con **K-Means (k = 5)** sobre 9 variables sonoras "
        "estandarizadas (mismo método del Certamen 2)."
    )
    col3, col4 = st.columns([3, 2])

    with col3:
        st.subheader("Perfiles en un gráfico de dispersión")
        c1, c2 = st.columns(2)
        eje_x = c1.selectbox("Eje X", VARS_SONORAS, index=4, key="sel_x",
                             format_func=lambda v: ETIQUETAS[v])
        eje_y = c2.selectbox("Eje Y", VARS_SONORAS, index=1, key="sel_y",
                             format_func=lambda v: ETIQUETAS[v])
        # Se grafica una submuestra para que el gráfico sea fluido
        graf = dff.sample(min(len(dff), 6000), random_state=42)
        fig = px.scatter(
            graf, x=eje_x, y=eje_y, color="perfil",
            color_discrete_map=COLOR_PERFIL, category_orders={"perfil": PERFILES},
            opacity=0.6,
            hover_name="name",
            hover_data={"artista_principal": True, "anio": True, "perfil": False},
            labels={eje_x: ETIQUETAS[eje_x], eje_y: ETIQUETAS[eje_y],
                    "artista_principal": "Artista", "anio": "Año", "perfil": "Perfil"},
            title="Canciones por perfil",
        )
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, width="stretch")
        st.caption(f"Se muestran {len(graf):,} canciones al azar (random_state=42) para que el gráfico sea fluido.")

    with col4:
        st.subheader("Perfil sonoro de cada grupo")
        # Radar: promedio de cada variable escalada de 0 a 1 (min-max)
        esc = (df[VARS_SONORAS] - df[VARS_SONORAS].min()) / (df[VARS_SONORAS].max() - df[VARS_SONORAS].min())
        esc["perfil"] = df["perfil"]
        radar = (esc[esc.index.isin(dff.index)]
                 .groupby("perfil")[VARS_SONORAS].mean()
                 .reset_index()
                 .melt(id_vars="perfil", var_name="variable", value_name="promedio"))
        radar["variable"] = radar["variable"].map(lambda v: ETIQUETAS[v].split(" (")[0])
        fig = px.line_polar(
            radar, r="promedio", theta="variable", color="perfil", line_close=True,
            color_discrete_map=COLOR_PERFIL, category_orders={"perfil": PERFILES},
            hover_data={"promedio": ":.2f"},
            labels={"promedio": "Promedio (0-1)", "perfil": "Perfil", "variable": "Variable"},
            title="Promedios escalados (0 a 1)",
        )
        fig.update_layout(**LAYOUT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Tabla de perfiles")
    tabla = (dff.groupby("perfil")
                .agg(canciones=("id", "count"),
                     popularidad=("popularity", "mean"),
                     energia=("energy", "mean"),
                     bailabilidad=("danceability", "mean"),
                     acustica=("acousticness", "mean"),
                     anio_promedio=("anio", "mean"))
                .round(2).reset_index())
    tabla["% del total"] = (tabla["canciones"] / len(dff) * 100).round(1)
    st.dataframe(tabla, width="stretch", hide_index=True)

# ── 9. TABLA DE DATOS (DESPLEGABLE) ──────────────────────────
with st.expander("Ver datos filtrados"):
    columnas = ["name", "artista_principal", "anio", "perfil", "popularity",
                "energy", "danceability", "acousticness", "valence", "tempo"]
    st.dataframe(dff[columnas].head(1000), width="stretch", hide_index=True)
    st.caption("Se muestran las primeras 1.000 filas.")

st.caption("Versión beta 2.1.0 · Datos: Spotify Dataset 1921-2020 (Kaggle), muestra de 40.000 canciones.")
