import pandas as pd
import matplotlib.pyplot as plt
import os
import glob

# Define directorios
dir_path = os.getcwd()

# Source paths
python_source_path = os.path.join(dir_path, "output", "python")
rust_source_path = os.path.join(dir_path, "output", "rust")
cpp_source_path = os.path.join(dir_path, "output", "cpp")

# Lee los csv de cada lenguaje
# Agrupa por grupo de prueba

pruebas_dict = {"Prueba 1" : "_n_1000_nf_10_gExogenous_150",
                "Prueba 2" : "_n_4000_nf_25_gExogenous_750",
                "Prueba 3" : "_n_8000_nf_50_gExogenous_1250",
               "Prueba 4" : "_n_16000_nf_100_gExogenous_2050"}

dict_df_pruebas = {p:{"python" : None, "rust" : None, "cpp" : None} for p in pruebas_dict}

for p,patt in pruebas_dict.items():

    df_python = pd.concat([pd.read_csv(i) for i in glob.glob(python_source_path+"/*.csv") if patt in i ])
    df_rust = pd.concat([pd.read_csv(i, names = ["id", "time", "tasa_desempleo", "gdp"]) for i in glob.glob(rust_source_path+"/*.csv") if patt in i])
    df_cpp = pd.concat([pd.read_csv(i, names = ["id", "time", "tasa_desempleo", "gdp"]) for i in glob.glob(cpp_source_path+"/*.csv") if patt in i])

    dict_df_pruebas[p]["python"] = df_python[["time" ,"tasa_desempleo", "gdp"]].groupby("time").mean().reset_index()
    dict_df_pruebas[p]["rust"] = df_rust[["time" ,"tasa_desempleo", "gdp"]].groupby("time").mean().reset_index()
    dict_df_pruebas[p]["cpp"] = df_cpp[["time" ,"tasa_desempleo", "gdp"]].groupby("time").mean().reset_index()


## Grafica tasa desempleo por prueba y lenguaje

for prueba in pruebas_dict:

    plt.plot(dict_df_pruebas[prueba]["python"]["tasa_desempleo"], label = f"Python")
    plt.plot(dict_df_pruebas[prueba]["rust"]["tasa_desempleo"], label = f"Rust")
    plt.plot(dict_df_pruebas[prueba]["cpp"]["tasa_desempleo"], label = f"C++")
    plt.title(f"Tasa de desempleo en las implementaciones\n{prueba}")
    plt.ylabel("Porcentaje")
    plt.legend()
    fig_name = prueba.replace(" ","_")
    plt.savefig(f"images/{fig_name}_tasa_desempleo.png")
    plt.close()
