# SIMplest_MABM

## Introducción

Rust es un lenguaje de programación creado en 2010 por Mozilla. El lenguaje brinda seguridad de la memoria sin la necesidad de incorpora un recolector de basura. Esto es producto de la introducción del concepto de *borrow checker* que verifica que los accesos a datos son legales, lo que le permite a Rust prevenir problemas de seguridad sin imponer costos durante el tiempo de ejecución [(McNara, 2021)](https://www.manning.com/books/rust-in-action). A su vez, *borrow checker* se basa en tres conceptos interrelacionados : *lifetimes*, *ownership* y *borrowing*.  En septiembre de 2022, la versión 6.1 del kernel de Linux incorporó a Rust para escribir componentes del kernel.

Si bien Rust es utilizado principalmente para System Programming, en la academia comienza a utilizarse el lenguaje como alternativa a C y C++ ([ver](https://www.nature.com/articles/d41586-020-03382-2)).

En esta implementación se realiza un comparativo entre tiempos de ejecución de un Modelo Macroeconómico Basado en Agentes propuesto por [Alessandro Caiani](https://sites.google.com/view/alessandro-caiani/teaching#h.p_NCwo3LmKcTZs) ("the SIMplest model"). Dicho modelo es desarrollado en Python, C++ y Rust. Se evaluan los tiempos de ejecución de las implementaciones con distintas cargas de trabajo.

## Modelo

### Supuestos

El modelo propuesto por [Alessandro Caiani](https://sites.google.com/view/alessandro-caiani/teaching#h.p_NCwo3LmKcTZs) supone lo siguiente:

* No hay dinero privado:
	- No hay bancos ni créditos ni pagos de interés.
* Economía cerrada:
	- No hay importaciones ni exportaciones.
	- No hay flujos de capital.
* Economía con sólo trabajo como factor de la producción.
	- No hay capital. 
	- No hay costos intermedios.
	
### Sectores

* Hogares:
	- Compran bienes de consumo y pagan impuestos.
	- Obtienen salario.
	- Acumulan activos.
	
* Productores:
	- Venden bienes y servicios a los hogares y gobierno.
	- Pagan salarios e impuestos.
	
* Gobierno:
	- Compran bienes y servicios a los productores.
	- Recaudan impuestos.

El activo del modelo es el dinero (*high powered money*).

Las interrelaciones entre sectores queda expresada en las matrices de flujos y acervos.
![Flujos](images/flujos.png)

![Acervos](images/acervos.png)

### Parámetros exógenos

* Número de hogares.
* Número de firmas.
* Productividad laboral.
* Propensión a consumir sobre el ingreso.
* Propensión a consumir sobre la riqueza.
* Tasa de impuestos.
* Gasto real del gobierno.
* Salarios.
* Precios.

## Definición de las ejecuciones de prueba

Comparamos las ejecuciones de modelo en Python y Rust para las siguientes cuatro pruebas:

![Experimentos](images/experimentos.png)

## Resultados 

Para las 4 pruebas realizadas, la implementación en Rust es entre 14 y 16 veces más rápida que la implementación en Python, mientras que C++ es entre 1.9 y 2.6 veces más rápido que Rust.

![](images/tiempo_ejec_rust_python.png)

La siguiente tabla presenta el tiempo en segundos de cada implementación.

| Tipo de experimento   |       C++ |   Python |     Rust |
|:----------------|----------:|---------:|---------:|
| Prueba 1        | 0.0573333 |  1.60367 | 0.110238 |
| Prueba 2        | 0.292381  |  7.60152 | 0.451762 |
| Prueba 3        | 0.659905  | 19.9071  | 1.17271  |
| Prueba 4        | 1.48205   | 60.2753  | 3.88514  |


Por su parte, la siguiente tabla presenta la razón de tiempo de ejecución de C++ y Rust vs Python.

| Tipo de Experimento   |     C++ |    Rust |
|:----------------|--------:|--------:|
| Prueba 1        | 27.9709 | 14.5473 |
| Prueba 2        | 25.9987 | 16.8264 |
| Prueba 3        | 30.1666 | 16.9752 |
| Prueba 4        | 40.6703 | 15.5143 |


Las siguientes figuras muestran la tasa de desempleo estimada para cada implementación.

![](images/Prueba_1_tasa_desempleo.png)
![](images/Prueba_2_tasa_desempleo.png)
![](images/Prueba_3_tasa_desempleo.png)
![](images/Prueba_4_tasa_desempleo.png)