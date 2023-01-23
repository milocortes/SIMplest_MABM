import random
import math

class Household(object):
    """docstring for Household."""

    def __init__(self, id):
        self.id = id
        self.wage = 0
        self.cash = 0
        self.employment = False
        self.employer_index = 0
        self.gross_income = 0
        self.disposable_income = 0
        self.good_supplier = 0
        self.pc_income = 0
        self.pc_wealth = 0
        self.real_demand_desired = 0
        self.demand_desired = 0
        self.consum_feasible = 0
        self.real_consum_feasible = 0
        self.real_income = 0
        self.real_wealth = 0

    def set_reserve_wage(self,wage):
        self.wage = wage

    def set_good_supplier(self, firms):
        self.good_supplier = math.ceil(random.uniform(0,len(firms)-1))

    def set_propensity_cosumption(self,pc_income,pc_wealth):
        self.pc_income = pc_income
        self.pc_wealth = pc_wealth

    def set_real_demand(self,firmas):
        provider_price = self.get_provider_price(firmas)
        self.real_income = self.disposable_income/provider_price
        self.real_wealth =  self.cash/provider_price
        self.real_demand_desired= math.floor((self.pc_income *(self.real_income)) + (self.pc_wealth *(self.real_wealth)))
        self.demand_desired = self.real_demand_desired * provider_price
        self.consum_feasible = min(self.demand_desired,self.cash)
        self.real_consum_feasible = min(self.real_demand_desired, math.floor(self.real_wealth))

        # El hogar ordena su pedido a la firma
        self.order_to_firms(firmas,self.real_consum_feasible)

        # El hogar paga el pedido a la firma
        self.pay_consumption()

    def pay_consumption(self):
        self.cash = self.cash -self.consum_feasible

    def get_provider_price(self,firms):

        for firm in firms:
            if firm.id ==self.good_supplier:
                return firm.price

    def order_to_firms(self,firms,quantity):
        for firm in firms:
            if firm.id ==self.good_supplier:
                firm.receive_household_order(quantity)

    def pay_to_firms(self,firms):
        for firm in firms:
            if firm.id ==self.good_supplier:
                firm.receive_household_pay(self.consum_feasible)

    def pay_taxes(self,goverment,tax_rate):
        if self.employment== True:
            self.disposable_income = (1 - tax_rate) * self.gross_income
            goverment.tax_income+= tax_rate * self.gross_income
            self.cash-= (tax_rate * self.gross_income)

class Firm(object):
    """docstring for Firm."""

    def __init__(self,id):
        self.id = id
        self.price = 0
        self.demand_by_households = 0
        self.demand_by_goverment = 0
        self.cash = 0
        self.cash_by_goverment = 0
        self.cash_by_households = 0
        self.employees = []
        self.wage_bill = 0
        self.output = 0
        self.inventories = 0
        self.profits = 0
        self.total_demand = 0

    def set_prices(self,price):
        self.price = price

    def receive_goverment_order(self,quantity):
        self.demand_by_goverment +=  quantity

    def receive_household_order(self,quantity):
        self.demand_by_households +=  quantity

    def receive_goverment_pay(self,quantity_cash):
        self.cash_by_goverment +=  quantity_cash

    def receive_household_pay(self,quantity):
        self.cash_by_households +=  quantity_cash

    def deter_labor_required(self,labor_productivity,households,wage_param):
        # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
        self.total_demand = self.demand_by_goverment + self.demand_by_households
        # Definimos los requerimientos laborales
        labor_required = math.floor(self.total_demand / labor_productivity)
        #print("Necesitamos ",str(self.total_demand)," y tenemos ", str(len(self.employees)))
        # Definimos la demanda laboral para este periodo
        labor_demand = labor_required -len(self.employees)

        # Si hay exceso de mano de obra, se despiden trabajadores
        if labor_demand < 0:
            # Seleccionamos de forma aleatoria los trabajadores a despedir
            while labor_demand!=0:
                id_worker = math.floor(random.uniform(0,len(self.employees)))
                # Cambiamos el estatus a desempleado del trabajador
                self.employees[id_worker].employment=False
                # Eliminamos al trabajador de la lista de empleados
                del self.employees[id_worker]
                labor_demand = labor_required -len(self.employees)
        else:
            # Interactuamos en el mercado laboral para contratar trabajadores
            for worker in households:
                if worker.employment == False:
                    worker.employment = True
                    worker.employer_index = self.id
                    self.employees.append(worker)

                    labor_demand = labor_required -len(self.employees)
                if labor_demand ==0:
                    break

        # Se pagan salarios
        for worker in self.employees:
            # wage_param es un parámetro exógeno
            worker.wage = wage_param
            worker.gross_income = worker.wage
            worker.cash += worker.wage
            self.wage_bill += worker.wage
            self.cash -= worker.wage

    def produce(self,labor_productivity):

        self.output = labor_productivity * len(self.employees)

        # Temporalmente el producto se guarda como inventarios
        self.inventories = self.output

        ### El producto se entrega a los demandantes

        if self.inventories>= self.total_demand:
            self.inventories-= self.total_demand
            #print("se cumple la demanda")
            self.demand_by_goverment=0
            self.demand_by_households=0
        else:
            #print("No se cumple la demanda")
            self.demand_by_goverment=0
            self.demand_by_households=0

    def computed_gross_profits(self):
        # Definimos la demanda total (real) al sumar las demandas del gobierno y de los hogares
        self.profits = self.total_demand * self.price

    def computed_net_profits(self,goverment,tax_rate):
        tax_amount = tax_rate*self.profits
        self.profits-=max(tax_amount,0)
        # Se pagan impuestos al gobierno
        goverment.tax_profits+= tax_amount


class Goverment(object):
    """docstring for Goverment."""

    def __init__(self):
        self.real_expenditure = 0
        self.nominal_expenditure = 0
        self.tax_profits = 0
        self.tax_income = 0
        self.balance = 0

    def set_real_expenditure(self,expenditure):
        self.real_expenditure = expenditure

    def set_nominal_expenditure(self,expenditure):
        self.nominal_expenditure = expenditure

    def define_demand_to_firms(self,firms):
        demand_by_firm = self.real_expenditure/len(firms)

        # El gobierno ordena su pedido a las firmas
        self.order_to_firms(firms,demand_by_firm)

        nominal_demand = 0

        for firm in firms:
            nominal_demand += demand_by_firm * firm.price

            ## El gobierno paga a las firmas
            firm.receive_goverment_pay(demand_by_firm * firm.price)

        self.set_nominal_expenditure(nominal_demand)

    def order_to_firms(self,firms,demand_by_firm):
        for firm in firms:
            firm.receive_goverment_order(demand_by_firm)

    def pay_consumption(self):
        self.balance = self.balance -self.nominal_expenditure

    def compute_deficit(self):
        self.balance += self.tax_profits + self.tax_income
