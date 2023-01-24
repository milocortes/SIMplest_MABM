#include<vector>
#include<algorithm>
#include <iostream>
#include <numeric>
#include <random>
#include <filesystem> 

#include "agents.h"
#include <fstream>


using namespace std;

// main del programa
int main(int argc, char const *argv[]) {

    // Definimos los parámetros estructurales
    int id_exec = atoi(argv[1]);;
    // Periodos de simulación
    int time = 300;
    // Número de hogares
    int n = atoi(argv[2]);;

    // Número de firmas
    int nf = atoi(argv[3]);;

    // Productividad laboral
    float phi = 1.0;
    // Propensión a consumir sobre el ingreso
    float cy = 0.8;
    // Propensión a consumir sobre la riqueza
    float ch = 0.2;
    // Tasa de impuestos
    float tau = 0.2;
    // Gasto real del gobierno
    float gExogenous = atof(argv[4]);
    // Salarios
    float wageExogenous = 10.0;
    // Precios
    float priceExogenous = 10.0;

    // Necesitaremos genera números aleatorios. 

    std::random_device rd; 
    std::mt19937 gen(rd()); 
    std::uniform_int_distribution<> distr(0, nf -1); // Define el rango

    // Definimos una lista que contendrá los hogares
    unsigned int households_range[n];
 
    unsigned int start = 1;
    std::iota(households_range, households_range + n, start);
    
    vector<Household> households;

    for (unsigned int &i: households_range) {
        households.push_back(Household {i});
    }

    // Definimos una lista que contendrá las empresas
    unsigned int empresas_range[nf];
    std::iota(empresas_range, empresas_range + nf, start);

    vector<Firm> empresas;

    for (unsigned int &i: empresas_range) {
        empresas.push_back(Firm {i});
    }

    // Instanciamos al gobierno
    Goverment goverment{};

    // Definimos vectores para almacenar resultados de 
    // la tasa de desempleo y el producto total
    vector<float> tasa_desempleo;
    vector<float> output_y;


    for (int i = 0; i <= time; ++i) {

        std::cout << "###############################"<<endl;
        std::cout << "Iteración " << i << endl;   
        //##### Comenzamos los tiks
        //## Tick 0 --> El gobierno define su gasto real
        goverment.set_real_expenditure(gExogenous);

        //## Tick 1 --> Las empresas definen sus precios
        for (Firm &empresa : empresas){
            empresa.set_prices(priceExogenous);
        }
        std::cout << "Precio de empresa " << priceExogenous << endl; 
        
        //## Tick 2 --> Los trabajadores definen su salario de reserva y sus propensiones a consumir
        for (Household &household : households){
            household.set_reserve_wage(wageExogenous);
            household.set_propensity_cosumption(cy,ch);
        }
        //## Tick 3 --> El gobierno comunica sus pedidos a las empresas
        goverment.define_demand_to_firms(empresas);
        float demanda_gob = 0.0 ; 
        
        for (Firm &empresa : empresas){        
            demanda_gob += empresa.demand_by_goverment;
        }
        
        std::cout << "El gob solicitó " << demanda_gob << endl; 

        //# Tick 4 --> Los hogares definen su demanda en términos reales y pagan su consumo
        // 4.1 Primero seleccionamos aleatoriamente el provedor
        for (Household &household : households){
            int id_good_suplier = distr(gen);
            //float provider_price = empresas[id_good_suplier].price; 
            float real_consum_feasible = household.set_real_demand(priceExogenous);
            empresas[id_good_suplier].receive_household_order(real_consum_feasible);
        }

        float ingreso_hogares = 0.0;
        float riqueza = 0.0;

        for (Household &hogar : households){
            riqueza += hogar.cash;
        }
        std::cout << "riqueza hogares: " << riqueza << endl;    

        for (Household &hogar : households){
            ingreso_hogares += hogar.real_consum_feasible;      
        }
        std::cout <<"demanda hogares: "<< ingreso_hogares<<endl;

        //## Tick 5 --> Las empresas definen su requerimientos de trabajo, contratan trabajadores y pagan salarios
        for (Firm &empresa : empresas){
            empresa.deter_labor_required(phi, households, wageExogenous, gen);
        }

        unsigned int demanda_trabajo = 0;
        for (Firm empresa : empresas){
            demanda_trabajo += empresa.employees.size();
        }
        std::cout << "demanda trabajo: " << demanda_trabajo << endl;

        //## Tick 6 --> La producción toma lugar
        for (Firm &empresa : empresas){
            empresa.produce(phi);
        }
        
        float producto = 0.0;

        for (Firm &empresa : empresas){
            producto+=empresa.output;
        }

        std::cout << "El producto fue " << producto<<endl;

        //## Tick 7 --> Se calculan las ganancias de las empresas
        for (Firm &empresa : empresas){
            empresa.computed_gross_profits();
        }

        //## Tick 8   ---> Se pagan impuestos
        //## Tick 8.a ---> Los hogares pagan impuestos

        for (Household &household : households){
            if (household.employment==true){

                household.disposable_income = (1.0 - tau) * household.gross_income;
                goverment.tax_income+= tau * household.gross_income;

                if( (household.cash - (tau * household.gross_income)) > 0){
                    household.cash-= (tau * household.gross_income);
                }
                
            }
        }

        //## Tick 8.b ---> Las empresas pagan impuestos
        for (Firm &empresa : empresas){
            float tax_amount = tau * empresa.profits;

            if (tax_amount >= 0.0) {
                empresa.profits -= tax_amount;
                //Se pagan impuestos al gobierno
                goverment.tax_profits+= tax_amount;
            }
        }

        //## Tick 9 ---> El gobierno calcula su déficit
        goverment.compute_deficit();

        //### Validamos lo resultados con la tasa de desempleo y el producto

        // Calcula desempleados
        int empleados = 0; 

        for (Firm &empresa : empresas){
            empleados+= empresa.employees.size();
            
        }
        int desempleados = n - empleados;

        std::cout << "Desempleados " << desempleados <<endl;
        tasa_desempleo.push_back((float) desempleados/ (float) n);


        // Calcula producto
        float producto_total = 0.0;
        for (Firm &firm : empresas){
            producto_total+=firm.output;
        }


        output_y.push_back(producto_total);
        }

    // Guardamos los resultados 

    string path_root = "output/cpp/";
    string file_name = "exp_"+to_string(id_exec)+"_n_"+to_string(n)+"_nf_" + to_string(nf) + "_gExogenous_" + to_string(static_cast<int>(gExogenous)) +".csv";
    string file_path = path_root + file_name;

    ofstream file_to_save (file_path);

    for(int i = 0; i<=time; ++i){
        file_to_save<< id_exec<<"," << i << "," << tasa_desempleo[i] << "," << output_y[i] <<endl;
    }
    file_to_save.close();

}