import gurobipy as gp
from gurobipy import GRB


class GurobiSolverBuilder:
    def __init__(self):
        self.decision_variables = []
        self.coeff_decision_variables = []

        self.model = gp.Model()

    def add_variable(self, name, lb=0, ub=GRB.INFINITY, vtype=GRB.CONTINUOUS):
        self.decision_variables.append(self.model.addVar(
            name=name, lb=lb, ub=ub, vtype=vtype))
        return self

    def add_constraint(self, expr, sense, rhs, name=""):
        self.model.addConstr(expr, sense, rhs, name=name)
        return self

    def set_objective(self, sense=GRB.MINIMIZE):
        self.model.setObjective(gp.quicksum(
            self.coeff_decision_variables[i]*self.decision_variables[i] for i in range(len(self.decision_variables))), sense)
        return self

    def set_coeff_decision_variables(self, list=[]):
        self.coeff_decision_variables = list
        return self

    def add_constraints(self, left, right, name=""):
        self.model.addConstrs((gp.quicksum(left[j][i]*self.decision_variables[i] for i in range(
            len(self.decision_variables))) <= right[j] for j in range(len(right))), name=name)
        return self

    def add_variables(self, number_of_variables, names=None, lbs=None, ubs=None, vtypes=None):
        if names is None:
            names = [("x " + str(i)) for i in range(number_of_variables)]
        if lbs is None:
            lbs = [0 for i in range(number_of_variables)]
        if ubs is None:
            ubs = [GRB.INFINITY for i in range(number_of_variables)]
        if vtypes is None:
            vtypes = [GRB.CONTINUOUS for i in range(number_of_variables)]
        for i in range(number_of_variables):
            self = self.add_variable(names[i], lbs[i], ubs[i], vtypes[i])
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

    def get_variables(self):
        vars = {}
        for var in self.model.getVars():
            print(var.varName, '=', var.x)
            vars[var.varName] = var.x
        return vars

    def get_objective_value(self):
        return self.model.objVal


# Example Usage:
# if __name__ == "__main__":
#     builder = GurobiSolverBuilder()
#     prix = [700, 900]
#     ressources_consommations = [[3, 5], [1, 2], [50, 20]]
#     ressources_disponibilité = [3600, 1600, 48000]
#     solver = (builder
#               .add_variables(2)
#               .add_constraints(
#                   ressources_consommations, ressources_disponibilité)
#               .set_coeff_decision_variables(prix)
#               .set_objective(GRB.MAXIMIZE)
#               .build()
#               )
#     solver.solve()
#     print(solver.get_variables())

