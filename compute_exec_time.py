import pandas as pd
import matplotlib.pyplot as plt

colnames = ["id_exper_type", "id_experimento", "houses", "firms", "G", "lenguaje", "real","user","sys", "p"]
resultados = pd.read_csv("output_time.txt", names=colnames)

resultados["id_exper_type"] = resultados["id_exper_type"].apply(lambda x: f"Prueba {x+1}")

## Tiempos promedios por tipo de prueba

agrupa_resultados = resultados[["id_exper_type", "lenguaje", "real"]].groupby(["id_exper_type", "lenguaje"]).mean().reset_index()
pivot_resultados = agrupa_resultados.pivot(index = "id_exper_type", columns ="lenguaje", values="real") 
pivot_resultados.rename(columns = {"rust":"Rust", "python": "Python"}, inplace = True)

razones = pivot_resultados["Python"]/pivot_resultados["Rust"] 

textstr = '\n'.join((
    r'Prueba 1 = $%.2f$' % (razones.loc["Prueba 1"] , ),
    r'Prueba 2 = $%.2f$' % (razones.loc["Prueba 2"] , ),
    r'Prueba 3 = $%.2f$' % (razones.loc["Prueba 3"] , ),
    r'Prueba 4 = $%.2f$' % (razones.loc["Prueba 4"] , )))


ax = pivot_resultados.plot.bar(rot=0)
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

ax.text(0.05, 0.55, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)

plt.xlabel("Prueba")
plt.ylabel("Segundos")
plt.title("Comparación de tiempo de ejecución Rust vs Python\nTiempo promedio de 20 ejecuciones (Segundos)")
plt.savefig("images/tiempo_ejec_rust_python.png")