import gurobipy as gp
from gurobipy import GRB

class GurobiSolverBuilder:
    def __init__(self):
        self.decision_variables=[]
        self.coeff_decision_variables=[]
        self.constraints_left=[]
        self.constraints_right=[]
        self.model = gp.Model()

    def add_variable(self, name, lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS):
        self.decision_variables.append(self.model.addVar(name=name, lb=lb, ub=ub, vtype=vtype))
        return self

    def add_constraint(self, expr, sense, rhs, name=""):
        self.model.addConstr(expr, sense, rhs, name=name)
        return self

    def set_objective(self, sense=GRB.MINIMIZE):
        self.model.setObjective(gp.quicksum(self.coeff_decision_variables[i]*self.decision_variables[i] for i in range(len(self.decision_variables))), sense)
        return self

    def set_coeff_decision_variables(self, list=[]):
        self.coeff_decision_variables=list
        return self

    def add_constraints(self,left, right,name=""):
        self.model.addConstrs((gp.quicksum(left[j][i]*self.decision_variables[i] for i in range(len(self.decision_variables)))<= right[j] for j in range(len(right))),name=name)
        return self
    def add_variables(self,number_of_variables, names=None, lbs=None,ubs=None,vtypes=None):
        if names is None:
            names = [("x " + str(i)) for i in range(number_of_variables)]
        if lbs is None:
            lbs = [ 0 for i in range(number_of_variables)]
        if ubs is None:
            ubs = [GRB.INFINITY for i in range(number_of_variables)]
        if vtypes is None:
            names = [GRB.CONTINUOUS for i in range(number_of_variables)]
        for i in range( number_of_variables):
            self.model=self.add_variable(self,names[i],lbs[i],ubs[i],vtypes[i])
        return self

    def build(self):
        return GurobiSolver(self.model)

class GurobiSolver:
    def __init__(self, model):
        self.model = model

    def solve(self):
        self.model.optimize()

    def get_variable(self, name):
        return self.model.getVarByName(name).x

    def get_objective_value(self):
        return self.model.objVal

# Example Usage:
# if __name__ == "__main__":
#     builder = GurobiSolverBuilder()

#     # Build the optimization model
#     solver = (
#         builder
#         .add_variable("x")
#         .add_variable("y")
#         .add_constraint("x + y <= 10", GRB.LESS_EQUAL, 20)
#         .add_constraint("2*x - y >= 0")
#         .set_objective("x + 2*y")
#         .build()
#     )

#     # Solve the optimization problem
#     solver.solve()

#     # Print solution
#     print("Objective value:", solver.get_objective_value())
#     print("x value:", solver.get_variable("x"))
#     print("y value:", solver.get_variable("y"))
