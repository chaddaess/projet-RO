import gurobipy as gp
from gurobipy import GRB

class GurobiMultiObjectiveSolver:
    def __init__(self):
        self.decision_variables = []
        self.coeff_decision_variables = []
        self.constraints_LHS = []
        self.constraints_RHS = []
        self.model = gp.Model()

    def add_variable(self, name, vtype=GRB.BINARY):
        self.decision_variables.append(self.model.addVar(name=name, vtype=vtype))
        return self

    def set_coeff_decision_variables(self, coefficients):
        self.coeff_decision_variables = coefficients
        return self

    def set_objectives(self, objectives, senses):
        if len(objectives) != len(senses):
            raise ValueError("Number of objectives must match number of senses.")
        expr = gp.LinExpr()
        for i in range(len(self.decision_variables)):
            expr += self.coeff_decision_variables[i] * self.decision_variables[i]
        for obj, sense in zip(objectives, senses):
            self.model.setObjective(expr, sense=obj)
        return self

    def add_constraint(self, expr, sense, rhs):
        self.model.addConstr(expr, sense, rhs)
        return self

    def add_constraints(self, expressions, senses, rhs):
        for expr, sense, rhs_val in zip(expressions, senses, rhs):
            self.model.addConstr(expr, sense, rhs_val)
        return self

    def build(self):
        self.model.update()
        return self

    def solve(self):
        self.model.optimize()

    def get_solution_status(self):
        return self.model.status

    def get_variable_value(self, name):
        return self.model.getVarByName(name).x

    def get_all_variable_values(self):
        return {var.varName: var.x for var in self.model.getVars()}

    def add_mutual_exclusion_constraint(self, problem_relationships):
        for celeb, problems in problem_relationships.items():
            celeb_index = None
            related_indices = []
            for i, var in enumerate(self.decision_variables):
                if var.varName == celeb:
                    celeb_index = i
                if var.varName in problems:
                    related_indices.append(i)
            if celeb_index is not None and related_indices:
                expr = gp.LinExpr()
                expr.addTerms(1, self.decision_variables[celeb_index])
                expr.addTerms(1, [self.decision_variables[idx] for idx in related_indices])
                self.model.addConstr(expr, GRB.LESS_EQUAL, 1)
        return self


# Example usage to solve the celebrity selection problem
if __name__ == "__main__":
    builder = GurobiMultiObjectiveSolver()

    # Define decision variables (binary variables for celebrity selection)
    num_celebrities = 5  # Example: Number of celebrities
    for i in range(num_celebrities):
        builder.add_variable(f"x_{i}")

    # Set coefficients for the decision variables (e.g., popularity index, salaries)
    popularity_coefficients = [0.7, 0.9, 0.6, 0.8, 0.5]  # Example: Popularity index coefficients
    salary_coefficients = [900, 1100, 800, 1000, 700]  # Example: Salary coefficients

    # Set objectives (maximize popularity, minimize total salaries)
    builder.set_coeff_decision_variables(popularity_coefficients)
    builder.set_objectives([GRB.MAXIMIZE, GRB.MINIMIZE], [1, 1])

    # Define constraints
    budget = 3000  # Example: Budget constraint
    ship_capacity = 2000  # Example: Ship's mass capacity

    # Salary constraint: Total salaries must be less than or equal to budget
    builder.add_constraint(gp.quicksum(salary_coefficients[i] * builder.decision_variables[i] for i in range(num_celebrities)), GRB.LESS_EQUAL, budget)

    # Mass constraint: Total mass of selected celebrities must be within ship's capacity
    celebrity_masses = [300, 400, 250, 350, 200]  # Example: Masses of celebrities
    builder.add_constraint(gp.quicksum(celebrity_masses[i] * builder.decision_variables[i] for i in range(num_celebrities)), GRB.LESS_EQUAL, ship_capacity)

    # At least one VIP constraint: At least one VIP celebrity must be selected
    is_vip = [False, True, False, True, False]  # Example: VIP status of celebrities
    builder.add_constraint(gp.quicksum(builder.decision_variables[i] for i in range(num_celebrities) if is_vip[i]), GRB.GREATER_EQUAL, 1)

    # Problem relationships (mutual exclusion constraints)
    problem_relationships = {
        "x_0": ["x_1"],  # Example: Celeb 0 has problems with Celeb 1
        "x_2": ["x_3", "x_4"]  # Example: Celeb 2 has problems with Celeb 3 and Celeb 4
    }

    # Add mutual exclusion constraints
    builder.add_mutual_exclusion_constraint(problem_relationships)

    # Build and solve the model
    builder.build()
    builder.solve()

    # Retrieve and print solution
    solution_status = builder.get_solution_status()
    if solution_status == GRB.OPTIMAL:
        solution_values = builder.get_all_variable_values()
        print("Optimal Solution:")
        for var_name, value in solution_values.items():
            print(f"{var_name}: {value}")
    else:
        print("No optimal solution found.")
