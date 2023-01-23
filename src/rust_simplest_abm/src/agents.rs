use rand::Rng; 

pub struct Rectangle{
  pub id: u32,
  pub width: u32,
  pub height: u32,
}

impl Rectangle{
    pub fn area(&self) ->u32 {
          self.width * self.height
    }

    pub fn change_id(&mut self, new_id : u32){
      self.id = new_id;
    }
}

pub struct Household{
  pub id : u32,
  pub wage : f32,
  pub money : f32, 
  pub cash : f32,
  pub employment : bool,
  pub employer_index : u32,
  pub gross_income : f32,
  pub disposable_income : f32,
  pub good_supplier : u32,
  pub pc_income : f32,
  pub pc_wealth : f32,
  pub real_demand_desired : f32,
  pub demand_desired : f32,
  pub consum_feasible : f32,
  pub real_consum_feasible : f32,
  pub real_income : f32,
  pub real_wealth : f32,
}

impl Household{
  pub fn set_reserve_wage(&mut self, wage : f32){
    self.wage = wage;
  }

  pub fn set_propensity_cosumption(&mut self, pc_income : f32, pc_wealth : f32){
    self.pc_income = pc_income;
    self.pc_wealth = pc_wealth;

  }

  pub fn set_good_suplier(&mut self, n_firms : u32){
    self.good_supplier = rand::thread_rng().gen_range(0, n_firms);
  }

  pub fn get_provider_price(&self, firms : &Vec<Firm>) -> f32{
    firms[self.good_supplier as usize].price
  }

  pub fn set_real_demand(&mut self, firms : &mut Vec<Firm>){

    // Define provider price
    let provider_price = self.get_provider_price(firms);

    // Define Real Income
    self.real_income = self.disposable_income/provider_price;

    // Define Real Wealth
    self.real_wealth =  self.cash/provider_price;

    // Define Real Demand Desired

    let real_demand_desired = (self.pc_income *(self.real_income)) + (self.pc_wealth *(self.real_wealth));
 
    self.real_demand_desired = real_demand_desired.floor() ;

    // Define Demand Desired
    self.demand_desired = (self.real_demand_desired as f32) * provider_price;

    // Define Consumption feasible
    if self.demand_desired >= self.cash{
      self.consum_feasible = self.cash;
    }else{
      self.consum_feasible = self.demand_desired;
    }

    // Define Real Demand Desired
    if self.real_demand_desired >= self.real_wealth{
      self.real_consum_feasible =  self.real_wealth;
    } else{
      self.real_consum_feasible =  self.real_demand_desired;
    }

    // El hogar ordena su pedido a la firma
    firms[self.good_supplier as usize].receive_household_order(self.real_consum_feasible);

    // El hogar paga el pedido a la firma
    self.cash = self.cash -self.consum_feasible;
  }

  pub fn pay_taxes(&mut self, goverment : &mut Goverment, tax_rate : f32){
    if self.employment{
      //println!("Paga impuestos");
      self.disposable_income = (1.0 - tax_rate) * self.gross_income;
      goverment.tax_income+= tax_rate * self.gross_income;
      self.cash-= (tax_rate * self.gross_income);
    }

  }

}


pub fn build_user(id: u32) -> Household{
  Household{
    id,
    wage : 0.0,
    money : 0.0,
    cash : 0.0,
    employment : false,
    employer_index : 0,
    gross_income : 0.0,
    disposable_income : 0.0,
    good_supplier : 0,
    pc_income : 0.0,
    pc_wealth : 0.0,
    real_demand_desired : 0.0,
    demand_desired : 0.0,
    consum_feasible : 0.0,
    real_consum_feasible : 0.0,
    real_income : 0.0,
    real_wealth : 0.0,
  }
}

pub struct Firm{
  pub id : u32,
  pub price : f32,
  pub demand_by_households : f32,
  pub demand_by_goverment : f32,
  pub cash : f32,
  pub cash_by_goverment : f32,
  pub cash_by_households : f32,
  pub employees : Vec<u32>,
  pub wage_bill  : f32,
  pub output  : f32,
  pub inventories : f32,
  pub profits : f32,
  pub total_demand : f32,
}

pub fn build_firm(id : u32) -> Firm{
  Firm{
    id,
    price : 0.0,
    demand_by_households : 0.0,
    demand_by_goverment : 0.0,
    cash : 0.0,
    cash_by_goverment : 0.0,
    cash_by_households : 0.0,
    employees : vec![],
    wage_bill  : 0.0,
    output  : 0.0,
    inventories : 0.0,
    profits : 0.0,
    total_demand : 0.0,
  }
}

impl Firm{

  pub fn set_prices(&mut self, price : f32){
    self.price = price;  
  }

  pub fn receive_goverment_order(&mut self, quantity : f32){
    self.demand_by_goverment +=  quantity;
  }
  

  pub fn receive_household_order(&mut self, quantity : f32){
    self.demand_by_households +=  quantity;
  }
  
  pub fn receive_goverment_pay(&mut self, quantity_cash : f32){
    self.cash_by_goverment +=  quantity_cash;
  }

  pub fn receive_household_pay(&mut self, quantity : f32){
    self.cash_by_households +=  quantity;
  }


  pub fn computed_gross_profits(&mut self){
  // Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
  self.profits = self.total_demand * self.price;
  } 

  pub fn computed_net_profits(&mut self, goverment : &mut Goverment, tax_rate : f32){
    let tax_amount = tax_rate*self.profits;

    if tax_amount >= 0.0 {
      self.profits -= tax_amount;
      //Se pagan impuestos al gobierno
      goverment.tax_profits+= tax_amount
    }


  }
  
  pub fn deter_labor_required(&mut self, labor_productivity : f32, households : &mut Vec<Household>  ,wage_param : f32){
    // # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
    self.total_demand = self.demand_by_goverment + self.demand_by_households;

    // # Definimos los requerimientos laborales
    let mut labor_required = (self.total_demand / labor_productivity).floor();

    // # Definimos la demanda laboral para este periodo
    let mut labor_demand = labor_required - (self.employees.len() as f32);

    // # Si hay exceso de mano de obra, se despiden trabajadores
    if labor_demand < 0.0{
      //println!("Despide trabajadores");

      while labor_demand < 0.0{
        let mut id_worker = rand::thread_rng().gen_range(0, self.employees.len() );
        //println!("Vamos a despedir a {}", id_worker);
  
        //# Cambiamos el estatus a desempleado del trabajador

        let id_worker_labor_market = self.employees[(id_worker as usize)] as usize;
        households[id_worker_labor_market].employment = false ;

        //# Eliminamos al trabajador de la lista de empleados
        self.employees.remove(id_worker);
        labor_demand = labor_required - (self.employees.len() as f32);
      }
    }else{
      // # Interactuamos en el mercado laboral para contratar trabajadores
      //println!("Contrata trabajadores");
      for worker in households.iter_mut(){
        if worker.employment == false{
          worker.employment = true;
          worker.employer_index = self.id;
          self.employees.push(worker.id);
          labor_demand = labor_required - (self.employees.len() as f32);
        }
        if labor_demand == 0.0{
          break;
        }
      }
    }

    //# Se pagan salarios
    for worker_id in self.employees.iter(){

      //# wage_param es un parámetro exógeno
      households[*worker_id as usize].wage = wage_param;
      households[*worker_id as usize].gross_income = wage_param;
      households[*worker_id as usize].cash += wage_param;

      //println!("Household id {}, wage{}, gross_income {}, cash {}", households[*worker_id as usize].id, households[*worker_id as usize].wage, households[*worker_id as usize].gross_income, households[*worker_id as usize].cash);
      self.wage_bill += wage_param;
      self.cash -= wage_param;
    }
  }
  
  pub fn produce(&mut self, labor_productivity : f32){
    self.output = labor_productivity * (self.employees.len() as f32);

    // Temporalmente el producto se guarda como inventarios
    self.inventories = self.output;

    // El producto se entrega a los demandantes
    if self.inventories>= self.total_demand{
      self.inventories-= self.total_demand;
      self.demand_by_goverment = 0.0 ;
      self.demand_by_households = 0.0 ; 

    }else{
      self.demand_by_goverment = 0.0 ;
      self.demand_by_households = 0.0 ; 
    }
  }

  
}


pub struct Goverment{
  pub real_expenditure : f32,
  pub nominal_expenditure : f32,
  pub tax_profits : f32,
  pub tax_income : f32,
  pub balance : f32,
}

pub fn build_goverment() -> Goverment{
  Goverment{
    real_expenditure : 0.0,
    nominal_expenditure : 0.0,
    tax_profits : 0.0,
    tax_income : 0.0,
    balance : 0.0,
  }
}

impl Goverment{
  pub fn set_real_expenditure(&mut self, expenditure : f32){
    self.real_expenditure = expenditure;
  }

  pub fn set_nominal_expenditure(&mut self,expenditure: f32){
    self.nominal_expenditure = expenditure;
  }

  pub fn order_to_firms(&mut self, firms : &mut Vec<Firm> , demand_by_firm : f32){
    for firm in firms.iter_mut(){
      firm.receive_goverment_order(demand_by_firm)
    }
  }

  pub fn pay_consumption(&mut self){
    self.balance = self.balance -self.nominal_expenditure;
  }
      
  pub fn compute_deficit(&mut self){
    self.balance += self.tax_profits + self.tax_income;
  }   

  pub fn define_demand_to_firms(&mut self, firms : &mut Vec<Firm> ){
    let demand_by_firm = self.real_expenditure/(firms.len() as f32);
    
    // # El gobierno ordena su pedido a las firmas
    self.order_to_firms(firms,demand_by_firm);

    let mut nominal_demand = 0.0;

    for firm in firms.iter_mut(){
      nominal_demand += demand_by_firm * firm.price;

      // El gobierno paga a las firmas
      firm.receive_goverment_pay(demand_by_firm * firm.price);

    }

    self.set_nominal_expenditure(nominal_demand);
    
  } 

  

  
}