#!/bin/bash

# Definimos arreglos de los parámetros
n_houses=(1000 4000 8000 16000)
n_firms=(10 25 50 100)
g_pub=(150 750 1250 2050)

n_experimentos=3
n_corridas=20

for i in  $(seq 0 $n_experimentos); do
    for n in $(seq 0 $n_corridas); do

    echo "Tipo de experimento $i"
    echo "Corrida $n . Houses ${n_houses[$i]}. Firms ${n_firms[$i]} . G ${g_pub[$i]}"

    ## Ejecuta modelo en Python y guarda el tiempo de ejecución
    echo "Python"
    output_time_python="$( TIMEFORMAT='%R,%U,%S,%P';time (python src/python_simplest_abm/main_simplest_abm.py $n ${n_houses[$i]} ${n_firms[$i]} ${g_pub[$i]}) 2>&1 1>/dev/null)"
    echo $output_time_python 

    ## Ejecuta modelo en Rust y guarda el tiempo de ejecución
    echo "Rust"
    output_time_rust="$( TIMEFORMAT='%R,%U,%S,%P';time ( ./src/rust_simplest_abm/target/debug/rust_simplest_abm $n ${n_houses[$i]} ${n_firms[$i]} ${g_pub[$i]}) 2>&1 1>/dev/null )"

    echo $output_time_rust

    ### Guardaremos la salida id_exper_type,id_experimento, houses, firms, G, lenguaje, exec_time

    echo "$i,$n,${n_houses[$i]},${n_firms[$i]},${g_pub[$i]},python,$output_time_python">>output_time.txt 
    echo "$i,$n,${n_houses[$i]},${n_firms[$i]},${g_pub[$i]},rust,$output_time_rust">>output_time.txt 

    done
done

## Calcula tiempos promedios
python compute_exec_time.py
## Calcula valores promedios
python compute_average_values.py