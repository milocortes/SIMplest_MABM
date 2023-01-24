#include<vector>
#include <math.h>       


using namespace std;


// Generamos una estructura para los Hogares
struct Household{
  unsigned int id;
  float wage;
  float money; 
  float cash;
  bool employment;
  unsigned int employer_index;
  float gross_income;
  float disposable_income;
  unsigned int good_supplier;
  float pc_income;
  float pc_wealth;
  float real_demand_desired;
  float demand_desired;
  float consum_feasible;
  float real_consum_feasible;
  float real_income;
  float real_wealth;


  // Métodos
  void set_reserve_wage(float set_wage) {
    wage = set_wage;
  }

  void set_propensity_cosumption(float set_pc_income, float set_pc_wealth){
    pc_income = set_pc_income;
    pc_wealth = set_pc_wealth;
  }

  void set_good_suplier(unsigned int id_good_suplier){
    good_supplier = id_good_suplier;
  }




  float set_real_demand(float provider_price){
     
    // Define Real Income
    //std::cout << "Hogar " << id << endl;
    real_income = disposable_income/provider_price;
    //std::cout << "real_income " << real_income <<endl; 
    // Define Real Wealth
    //std::cout << "Cash " << cash <<endl; 

    real_wealth = cash/provider_price;
    //std::cout << "real_wealth " << real_wealth <<endl; 

    // Define Real Demand Desired

    float real_demand_desired = (pc_income *(real_income)) + (pc_wealth *(real_wealth));
    real_demand_desired = floor(real_demand_desired) ;
    //std::cout << "real_demand_desired " << real_demand_desired <<endl; 

    // Define Demand Desired
    demand_desired = real_demand_desired * provider_price;
    //std::cout << "demand_desired " << demand_desired <<endl; 

    // Define Consumption feasible
    consum_feasible = std::min(demand_desired, cash);
    //std::cout << "consum_feasible " << consum_feasible <<endl; 

    // Define Real Demand Desired
    real_consum_feasible = std::min(real_demand_desired, floor(real_wealth));
    //std::cout << "real_consum_feasible " << real_consum_feasible <<endl; 

    // El hogar ordena su pedido a la firma
    //firms[good_supplier].receive_household_order(real_consum_feasible);

    // El hogar paga el pedido a la firma

    if ((cash - consum_feasible) > 0){
      cash = cash - consum_feasible;
    }
    

    return real_consum_feasible;
  }

};




// Generamos una estructura para las Empresas
struct Firm{
  unsigned int id;
  float price;
  float demand_by_households;
  float demand_by_goverment;
  float cash;
  float cash_by_goverment;
  float cash_by_households;
  vector< int> employees;
  float wage_bill ;
  float output ;
  float inventories;
  float profits;
  float total_demand;

  // Métodos


  void set_prices(float set_price){
    price = set_price;  
  }

  void receive_goverment_order(float set_quantity){
    demand_by_goverment +=  set_quantity;
  }
  

  void receive_household_order(float set_quantity){
    demand_by_households +=  set_quantity;
  }
  
  void receive_goverment_pay(float set_quantity_cash){
    cash_by_goverment +=  set_quantity_cash;
  }

  void receive_household_pay(float set_quantity){
    cash_by_households +=  set_quantity;
  }


  void computed_gross_profits(){
    // Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
    profits = total_demand * price;
  } 




    /*
  void computed_net_profits(Goverment goverment, float tax_rate){
    float tax_amount = tax_rate*profits;

    if (tax_amount >= 0.0) {
      profits -= tax_amount;
      //Se pagan impuestos al gobierno
      goverment.tax_profits+= tax_amount;
    }
    
  }*/

  void deter_labor_required(float labor_productivity, vector<Household> &households, float wage_param, mt19937 &gen){
    // # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares

    //std::cout << "Demanda del gobierno "<< demand_by_goverment <<endl;
    //std::cout << "Demanda de hogares "<< demand_by_households <<endl;
    total_demand = demand_by_goverment + demand_by_households;

    // # Definimos los requerimientos laborales
    float labor_required = floor((total_demand / labor_productivity));
    //std::cout <<"La empresa " <<id <<" calcula labor requiered " << labor_required << endl;

    // # Definimos la demanda laboral para este periodo
    int labor_demand = labor_required - employees.size();
    //std::cout <<"La empresa " <<id <<" tiene " << employees.size() << " trabajadores" << endl;

    // # Si hay exceso de mano de obra, se despiden trabajadores
    //std::cout <<"Labor demand " << labor_demand <<endl;

    if (labor_demand < 0){
      //std::cout <<"Despide trabajadores"<<endl;

      while (labor_demand < 0){
        //std::cout << "Employees "<<employees.size() << endl;
        std::uniform_int_distribution<> distr(0, employees.size() -1); // define the range
         
        auto id_worker = distr(gen);

        //std::cout << "Vamos a despedir a " << id_worker<<endl;
  
        //# Cambiamos el estatus a desempleado del trabajador

        auto id_worker_labor_market = employees[id_worker] ;

        households[id_worker_labor_market].employment = false ;

        //# Eliminamos al trabajador de la lista de empleados
        //std::cout<< "Cantidad total de empleados" << employees.size()<<endl;
        employees.erase(employees.begin() + id_worker);
        //std::cout<< "Cantidad total de empleados (despues)" << employees.size()<<endl;

        labor_demand = labor_required - employees.size();

        //std::cout <<"Labor demand " << labor_demand <<endl;
      }
    }else{
      // # Interactuamos en el mercado laboral para contratar trabajadores
      //std::cout <<"Contrata trabajadores" <<endl;
      for (Household &worker: households){
        if (worker.employment == false){
          worker.employment = true;
          worker.employer_index = id;
          employees.push_back(worker.id);
          labor_demand = labor_required - employees.size();
        }
        if (labor_demand == 0){
          break;
        }
      }
    }
    //std::cout <<"Labor demand " << labor_demand <<endl;
    //std::cout <<"Empleados al final " << employees.size() <<endl;

    //# Se pagan salarios
    for (int &worker_id: employees){

      //# wage_param es un parámetro exógeno
      households[worker_id].wage = wage_param;
      households[worker_id].gross_income = wage_param;
      households[worker_id].cash += wage_param;
      
      //std::cout << "Household id " << households[worker_id].id << "wage "<< households[worker_id].wage << "gross_income " <<households[worker_id].gross_income <<  "cash " <<households[worker_id].cash <<endl; 
      //println!("Household id {}, wage{}, gross_income {}, cash {}", households[*worker_id as usize].id, households[*worker_id as usize].wage, households[*worker_id as usize].gross_income, households[*worker_id as usize].cash);
      wage_bill += wage_param;
      cash -= wage_param;
    }

  }

     
  void produce(float labor_productivity){
    output = labor_productivity * employees.size();
    //std::cout << "La empresa " << id << " Empleados" << employees.size() << " Produccion "<< output << endl;
    // Temporalmente el producto se guarda como inventarios
    inventories = output;

    // El producto se entrega a los demandantes
    if (inventories>= total_demand){
      inventories -= total_demand;
      demand_by_goverment = 0.0 ;
      demand_by_households = 0.0 ; 

    }else{
      demand_by_goverment = 0.0 ;
      demand_by_households = 0.0 ; 
    }
  }    

};


// Generamos una estructura para el Gobierno

struct Goverment{
  float real_expenditure;
  float nominal_expenditure;
  float tax_profits;
  float tax_income;
  float balance;

  // Métodos

  void set_real_expenditure(float set_expenditure){
    real_expenditure = set_expenditure;
  }

  void set_nominal_expenditure(float set_expenditure){
    nominal_expenditure = set_expenditure;
  }

  void order_to_firms(vector<Firm> &firms , float demand_by_firm){

    for (Firm &firm: firms){
        firm.receive_goverment_order(demand_by_firm);

    }

  }

  void pay_consumption(){
    balance = balance - nominal_expenditure;
  }
      
  void compute_deficit(){
    balance += tax_profits + tax_income;
  }   

  void define_demand_to_firms(vector<Firm> &firms){
    auto demand_by_firm = real_expenditure/firms.size() ;
    
    // # El gobierno ordena su pedido a las firmas
    order_to_firms(firms,demand_by_firm);

    float nominal_demand = 0.0;

    for (Firm &firm: firms){

      nominal_demand += demand_by_firm * firm.price;

      // El gobierno paga a las firmas
      firm.receive_goverment_pay(demand_by_firm * firm.price);

    }

    set_nominal_expenditure(nominal_demand);
    
  } 

};