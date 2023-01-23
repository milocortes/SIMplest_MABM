from agents import Household, Firm, Goverment
import pandas as pd
import os
import sys 

## Define directori para guardar los resultados

dir_path = os.path.dirname(os.path.realpath(__file__))
path_to_save = os.path.abspath(os.path.join(dir_path, "..", "..", "output", "python"))


## Definimos los parámetros estructurales
id_exec = int(sys.argv[1])
# Periodos de simulación
time = 300
# Número de hogares
n = int(sys.argv[2])
# Número de firmas
nf = int(sys.argv[3])
# Productividad laboral
phi = 1
# Propensión a consumir sobre el ingreso
cy = 0.8
# Propensión a consumir sobre la riqueza
ch = 0.2
# Tasa de impuestos
tau = 0.2
# Gasto real del gobierno
gExogenous = int(sys.argv[4])
# Salarios
wageExogenous=10
# Precios
priceExogenous=10

# Definimos una lista que contendrá los hogares
households= [Household(x) for x in range(n)]

# Definimos una lista que contendrá las empresas
empresas = [Firm(x) for x in range(nf)]

# Instanciamos al gobierno
goverment= Goverment()

tasa_desempleo = []
output_y = []

for i in range(time):
    print("###############################")
    print("Iteración ", str(i))
    ##### Comenzamos los tiks
    ## Tick 0 --> El gobierno define su gasto real
    goverment.set_real_expenditure(gExogenous)

    ## Tick 1 --> Las empresas definen sus precios
    for empresa in empresas:
        empresa.set_prices(priceExogenous)

    ## Tick 2 --> Los trabajadores definen su salario de reserva y sus propensiones a consumir
    for household in households:
        household.set_reserve_wage(wageExogenous)
        household.set_propensity_cosumption(cy,ch)

    ## Tick 3 --> El gobierno comunica sus pedidos a las empresas
    goverment.define_demand_to_firms(empresas)
    demanda_gob =0
    for empresa in empresas:
        demanda_gob+=empresa.demand_by_goverment
    print("El gob solicitó ",str(demanda_gob))
    ## Tick 4 --> Los hogares definen su provedor de bienes
    for household in households:
        household.set_good_supplier(empresas)

    ## Tick 5 --> Los hogares definen su demanda en términos reales y pagan su consumo
    for household in households:
        household.set_real_demand(empresas)
    ingreso_hogares = 0
    riqueza = 0

    for hogar in households:
        riqueza += hogar.cash
    print("riqueza hogares: ",str(riqueza))
    for hogar in households:
        ingreso_hogares += hogar.real_consum_feasible
    print("demanda hogares: ",str(ingreso_hogares))

    ## Tick 6 --> Las empresas definen su requerimientos de trabajo, contratan trabajadores y pagan salarios
    for empresa in empresas:
        empresa.deter_labor_required(phi,households,wageExogenous)

    demanda_trabajo=0
    for empresa in empresas:
        demanda_trabajo+=len(empresa.employees)
    print("demanda trabajo: ",str(demanda_trabajo))

    ## Tick 7 --> La producción toma lugar
    for empresa in empresas:
        empresa.produce(phi)
    producto=0
    for empresa in empresas:
        producto+=empresa.output
    print("El producto fue ",str(producto))
    ## Tick 8 --> Se calculan las ganancias de las empresas
    for empresa in empresas:
        empresa.computed_gross_profits()

    ## Tick 9   ---> Se pagan impuestos
    ## Tick 9.a ---> Los hogares pagan impuestos
    for household in households:
        household.pay_taxes(goverment,tau)
    ## Tick 9.b ---> Las empresas pagan impuestos
    for empresa in empresas:
        empresa.computed_net_profits(goverment,tau)
    ## Tick 10 ---> El gobierno calcula su déficit
    goverment.compute_deficit()


    ### Validamos lo resultados

    desempleados=0

    for hogares in households:
        if hogares.employment==False:
            desempleados+=1
    print("Desempleados ", str(desempleados))
    tasa_desempleo.append(desempleados/len(households))

    producto = 0
    for firm in empresas:
        producto+=firm.output

    output_y.append(producto)

df_output = pd.DataFrame({"id" : [id_exec]*time, "time" : range(time), "tasa_desempleo" : tasa_desempleo, "gdp" : output_y})

file_name = os.path.join(path_to_save, f"exp_{id_exec}_n_{n}_nf_{nf}_gExogenous_{gExogenous}.csv")

df_output.to_csv(file_name, index = False)

"""
plt.plot(tasa_desempleo)
plt.ylabel('Tasa de desempleo')
plt.show()

plt.plot(output_y)
plt.ylabel('Producto')
plt.show()
"""