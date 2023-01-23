mod agents;

use agents::{Rectangle,Household,build_user, build_firm, build_goverment};
use rand::Rng; 
use std::env;
use std::fs::{File, canonicalize};
use std::io::prelude::*;

use std::path::{PathBuf, Path};

fn main() {

    let args: Vec<_> = env::args().collect();

    let id_exec = args[1].parse::<u32>().unwrap();

    // Definimos los parámetros estructurales
    // Periodos de simulación
    let time = 300;
    // Número de hogares
    let n = args[2].parse::<u32>().unwrap();
    // Número de firmas
    let nf = args[3].parse::<u32>().unwrap();
    // Productividad laboral
    let phi = 1.0;
    // Propensión a consumir sobre el ingreso
    let cy = 0.8;
    // Propensión a consumir sobre la riqueza
    let ch = 0.2;
    // Tasa de impuestos
    let tau = 0.2;
    // Gasto real del gobierno
    let gExogenous = args[4].parse::<f32>().unwrap();
    // Salarios
    let wageExogenous = 10.0;
    // Precios
    let priceExogenous = 10.0;

    // Definimos una lista que contendrá los hogares
    let mut households_range = 0..n;
    let mut households : Vec<_>  = households_range.map(|x| build_user(x)).collect();

    // Definimos una lista que contendrá las empresas
    let mut empresas_range = 0..nf;
    let mut empresas : Vec<_>  = empresas_range.map(|x| build_firm(x)).collect();

    // Instanciamos al gobierno
    let mut goverment = build_goverment();

    // Definimos vectores para almacenar resultados de 
    // la tasa de desempleo y el producto total
    let mut tasa_desempleo: Vec<f32> = Vec::new();
    let mut output_y: Vec<f32> = Vec::new();


    for it in 0..time{

      println!("###############################");
      println!("Iteración {}", it);      
      //##### Comenzamos los tiks
      //## Tick 0 --> El gobierno define su gasto real
      goverment.set_real_expenditure(gExogenous);
      //## Tick 1 --> Las empresas definen sus precios
      for empresa in empresas.iter_mut(){
        empresa.set_prices(priceExogenous);
      }
      //## Tick 2 --> Los trabajadores definen su salario de reserva y sus propensiones a consumir
      for household in households.iter_mut(){
        household.set_reserve_wage(wageExogenous);
        household.set_propensity_cosumption(cy,ch);
      }

      //## Tick 3 --> El gobierno comunica sus pedidos a las empresas
      goverment.define_demand_to_firms(&mut empresas);
      let mut demanda_gob = 0.0 ; 
      for empresa in empresas.iter_mut(){
        demanda_gob+=empresa.demand_by_goverment;
      }
      println!("El gob solicitó {}",demanda_gob);

      //# Tick 4 --> Los hogares definen su demanda en términos reales y pagan su consumo
      for household in households.iter_mut(){
        household.set_real_demand(&mut empresas);
      }

      let mut ingreso_hogares = 0.0;
      let mut riqueza = 0.0;

      for hogar in households.iter_mut(){
        riqueza += hogar.cash;
      }
      println!("riqueza hogares: {}",riqueza);

      for hogar in households.iter_mut(){
        ingreso_hogares += hogar.real_consum_feasible;      
      }
      println!("demanda hogares: {}",ingreso_hogares);


      //## Tick 5 --> Las empresas definen su requerimientos de trabajo, contratan trabajadores y pagan salarios
      for empresa in empresas.iter_mut(){
        empresa.deter_labor_required(phi,&mut households,wageExogenous);
      }

      let mut demanda_trabajo = 0;
      for empresa in empresas.iter_mut(){
        demanda_trabajo += empresa.employees.len();
      }
      println!("demanda trabajo: {}", demanda_trabajo);

      //## Tick 6 --> La producción toma lugar
      for empresa in empresas.iter_mut(){
        empresa.produce(phi);
      }
      let mut producto = 0.0;

      for empresa in empresas.iter_mut(){
        producto+=empresa.output;
      }

      println!("El producto fue {}", producto);

      //## Tick 7 --> Se calculan las ganancias de las empresas
      for empresa in empresas.iter_mut(){
        empresa.computed_gross_profits();
      }

      //## Tick 8   ---> Se pagan impuestos
      //## Tick 8.a ---> Los hogares pagan impuestos
      for household in households.iter_mut(){
        household.pay_taxes(&mut goverment,tau);
      }
      //## Tick 8.b ---> Las empresas pagan impuestos
      for empresa in empresas.iter_mut(){
        empresa.computed_net_profits(&mut goverment,tau);
      }

      //## Tick 9 ---> El gobierno calcula su déficit
      goverment.compute_deficit();


      //### Validamos lo resultados con la tasa de desempleo y el producto

      // Calcula desempleados
      let mut desempleados = 0.0; 

      for hogares in households.iter_mut(){
        if hogares.employment==false{
          desempleados+=1.0;
        }
      }
              
      println!("Desempleados {}", desempleados);

      tasa_desempleo.push(desempleados/(households.len() as f32));

      // Calcula producto
      let mut producto = 0.0;
      for firm in empresas.iter_mut(){
        producto+=firm.output;
      }
          

      output_y.push(producto);
    }


    // Guardamos los resultados

    let vector_to_save = tasa_desempleo.iter().zip(output_y.iter());

    let file_name = format!("exp_{}_n_{}_nf_{}_gExogenous_{}.csv", id_exec.to_string(), n.to_string(), nf.to_string(), gExogenous.to_string());

    let mut file_path_to_save = Path::new("./output/rust/.").join(file_name);

    let mut file_to_save = File::create(file_path_to_save).expect("Could not create"); 

    for (i, (td, out)) in vector_to_save.enumerate(){
      let mut value_to_save = format!("{},{},{},{}\n",id_exec, i, td, out);
      file_to_save.write_all(value_to_save.as_bytes()).expect("Fallo");
    }
    
}

