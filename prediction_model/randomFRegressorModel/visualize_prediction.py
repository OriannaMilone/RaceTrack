import matplotlib.pyplot as plt

def visualizar_orden_real_vs_predicho(df_pred):
    fig, ax = plt.subplots(figsize=(10, 6))

    pilotos = df_pred["Driver"]
    orden_real = df_pred["Position_curr"]
    orden_pred = df_pred["PredictedRank"]

    # Gráfico de líneas entre ambas posiciones
    for i in range(len(pilotos)):
        ax.plot([0, 1], [orden_real.iloc[i], orden_pred.iloc[i]], marker='o', label=pilotos.iloc[i])

    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Vuelta actual", "Predicción próxima vuelta"])
    ax.invert_yaxis()  # 1 es mejor posición
    ax.set_title("Comparativa de Posición Real vs Predicha")
    ax.set_ylabel("Posición en carrera")
    ax.grid(True)
    plt.legend(loc="center left", bbox_to_anchor=(1, 0.5))
    plt.tight_layout()
    plt.show()
