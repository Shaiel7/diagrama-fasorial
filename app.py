import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import streamlit as st

# Logo más arriba, alineado a la izquierda
st.image("logo.png", width=150)  # Ajusta el width a tu gusto

# Espacio opcional entre logo y título
st.markdown("<br>", unsafe_allow_html=True)

# Título centrado en una sola línea
st.markdown(
    """
    <h1 style="
        text-align:center; 
        color:#1F618D; 
        font-family:Arial, sans-serif; 
        font-weight:bold; 
        white-space:nowrap;
        margin:0;
        font-size:38px;  /* Ajusta el tamaño aquí */
    ">
        ⚡ Diagrama Fasorial desde HTML ⚡
    </h1>
    """,
    unsafe_allow_html=True
)

# Subir archivo HTML
archivo = st.file_uploader("📂 Sube tu archivo HTML", type=["html", "htm"])

if archivo:
    try:
        # Leer todas las tablas del HTML
        tablas = pd.read_html(archivo)
        st.info(f"{len(tablas)} tablas encontradas en el HTML.")

        # Buscar tabla que contenga "Ángulo de fase de voltaje"
        df = None
        for tabla in tablas:
            if tabla.astype(str).apply(lambda x: x.str.contains("Ángulo de fase de voltaje", case=False, na=False)).any().any():
                df = tabla
                break

        if df is None:
            st.error("No se encontró la tabla de Phasor Diagram en el HTML.")
        else:
            st.success("Tabla relevante encontrada.")
            st.write("Vista previa de la tabla:", df.head(12))

            # --- Extraer ángulos ---
            # Ajustar nombres de columnas si es necesario
            fases = ["A", "B", "C"]

            ang_v = df.loc[df.iloc[:,0].str.contains("Ángulo de fase de voltaje", case=False, na=False)].iloc[0,1:4].astype(float).values
            ang_i_raw = df.loc[df.iloc[:,0].str.contains("Ángulo de fase de corriente", case=False, na=False)].iloc[0,1:4].astype(float).values

            # --- Graficar ---
            fig, ax = plt.subplots(figsize=(8,8), subplot_kw={'polar': True})
            ax.set_theta_zero_location("E")
            ax.set_theta_direction(-1)
            ax.grid(True, linestyle=":", alpha=0.5)

            # Flecha de referencia
            ax.arrow(0,0,1,0, head_width=0.04, head_length=0.04, fc="gray", ec="gray", linestyle="--", lw=1.5)
            ax.text(0,1.05,"Referencia (0°)", color="gray", fontsize=9, ha="center", va="bottom")

            # Voltajes
            for i,fase in enumerate(fases):
                ang_rad_v = np.deg2rad(ang_v[i])
                ax.arrow(ang_rad_v,0,0,1, head_width=0.05, head_length=0.08, fc="#007bff", ec="#004c99", lw=2)
                ax.text(ang_rad_v,1.12,f"V{fase}", color="#004c99", ha="center", va="bottom", fontsize=11, fontweight="bold")

            # Corrientes y desfases
            for i,fase in enumerate(fases):
                ang_rad_i = np.deg2rad(ang_i_raw[i])
                ax.arrow(ang_rad_i,0,0,0.9, head_width=0.05, head_length=0.08, fc="#00cc66", ec="#008040", lw=2)
                ax.text(ang_rad_i,1.0,f"I{fase}", color="#006633", ha="center", va="bottom", fontsize=11, fontweight="bold")

                # Ángulo de desfase
                angle_v_deg = ang_v[i] % 360
                angle_i_deg = ang_i_raw[i] % 360
                angle_diff = (angle_v_deg - angle_i_deg + 360) % 360
                if angle_diff > 180:
                    angle_diff -= 360
                start_angle_rad = np.deg2rad(angle_i_deg)
                end_angle_rad = np.deg2rad(angle_v_deg)
                if angle_diff != 0:
                    if (angle_diff < 0 and end_angle_rad > start_angle_rad) or (angle_diff > 0 and end_angle_rad < start_angle_rad):
                        end_angle_rad += np.sign(angle_diff)*2*np.pi
                    theta_vals = np.linspace(start_angle_rad,end_angle_rad,40)
                    r_vals = np.ones_like(theta_vals)*0.4
                    ax.plot(theta_vals,r_vals,color="red", lw=2)
                    mid_angle = np.mean([theta_vals[0], theta_vals[-1]]) % (2*np.pi)
                    if angle_diff>0:
                        ax.text(mid_angle,0.45,f"Θ{fase}", color="red", ha="center", va="center", fontsize=11, fontweight="bold")
                    else:
                        text_rot = np.rad2deg(mid_angle)
                        if 90<text_rot<270:
                            text_rot+=180
                        text_rot%=360
                        ax.text(mid_angle,0.45,f"Θ{fase}", color="red", ha="center", va="center", fontsize=11, fontweight="bold", rotation=text_rot)

            # Etiquetas de referencia
            reference_angles = np.arange(0,360,30)
            ax.set_xticks(np.deg2rad(reference_angles))
            ax.set_xticklabels([f"{deg}°" for deg in reference_angles])
            ax.set_rticks([])
            ax.set_title("⚡ Diagrama Fasorial ⚡", fontsize=14, fontweight='bold', pad=20)
            ax.set_facecolor("#fafafa")

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error al procesar el HTML: {e}")
