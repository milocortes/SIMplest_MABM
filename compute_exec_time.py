import pandas as pd
import matplotlib.pyplot as plt

colnames = ["id_exper_type", "id_experimento", "houses", "firms", "G", "lenguaje", "real","user","sys", "p"]
resultados = pd.read_csv("output_time.txt", names=colnames)

resultados["id_exper_type"] = resultados["id_exper_type"].apply(lambda x: f"Prueba {x+1}")

## Tiempos promedios por tipo de prueba

agrupa_resultados = resultados[["id_exper_type", "lenguaje", "real"]].groupby(["id_exper_type", "lenguaje"]).mean().reset_index()
pivot_resultados = agrupa_resultados.pivot(index = "id_exper_type", columns ="lenguaje", values="real") 
pivot_resultados.rename(columns = {"rust":"Rust", "python": "Python", "cpp" : "C++"}, inplace = True)

"""
razones = pivot_resultados["Python"]/pivot_resultados["Rust"] 

textstr = '\n'.join((
    r'Prueba 1 = $%.2f$' % (razones.loc["Prueba 1"] , ),
    r'Prueba 2 = $%.2f$' % (razones.loc["Prueba 2"] , ),
    r'Prueba 3 = $%.2f$' % (razones.loc["Prueba 3"] , ),
    r'Prueba 4 = $%.2f$' % (razones.loc["Prueba 4"] , )))

props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

ax.text(0.05, 0.55, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
"""
ax = pivot_resultados.plot.bar(rot=0)


plt.xlabel("Prueba")
plt.ylabel("Segundos")
plt.title("Comparación de tiempo de ejecución C++, Python y Rust\nTiempo promedio de 20 ejecuciones (Segundos)")
plt.savefig("images/tiempo_ejec_rust_python.png")


## Imprime valores de tiempo de ejecucion en markdown
print("Markdown table")
print(pivot_resultados.to_markdown())

pivot_resultados_vs_python = pivot_resultados.copy()  
pivot_resultados_vs_python.drop(columns="Python", inplace = True)
pivot_resultados_vs_python["C++"] = pivot_resultados["Python"]/pivot_resultados["C++"]  
pivot_resultados_vs_python["Rust"] = pivot_resultados["Python"]/pivot_resultados["Rust"]

print("Markdown table razones")

print(pivot_resultados_vs_python.to_markdown())

print(pivot_resultados["Rust"]/pivot_resultados["C++"])