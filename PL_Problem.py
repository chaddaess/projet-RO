import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout
from gurobipy import GRB

from GurobiSolver import GurobiSolverBuilder
# GUI styles
style_sheet = """
    QWidget {
        background-color: #2b2b2b;
    }
    QPushButton {
        background-color: #33a6cc;
        color: white;
        font-size: 16px;
        padding: 5px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background-color: #80d7ff;
    }
    QPushButton:pressed {
        background-color: #258399;
    }
"""

# GUI definition
class ToyFactoryGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Toy Factory Profit Maximization')
        # arrange widgets vertically
        self.layout = QVBoxLayout()

        # input field for maximum work hours per day
        self.max_hours_per_worker_label=QLabel('Maximum  hours of work (per worker) per day')
        self.max_hours_per_worker_input = QLineEdit()
        self.layout.addWidget(self.max_hours_per_worker_label)
        self.layout.addWidget(self.max_hours_per_worker_input)

        #input field for maximum hours of machine work per day
        self.max_hours_machine_label=QLabel('Maximum  hours of machine work per day')
        self.max_hours_machine_input = QLineEdit()
        self.layout.addWidget(self.max_hours_machine_label)
        self.layout.addWidget(self.max_hours_machine_input)

        # input field for maximum kilos of wood per day
        self.max_wood_label=QLabel('Maximum  kilos of wood  per day')
        self.max_wood_input = QLineEdit()
        self.layout.addWidget(self.max_wood_label)
        self.layout.addWidget(self.max_wood_input)

        # input field for number of workers per day
        self.max_workers_label=QLabel('Number of workers available per day')
        self.max_workers_input=QLineEdit()
        self.layout.addWidget(self.max_workers_label)
        self.layout.addWidget(self.max_workers_input)

        # input field for salary/hour
        self.salary_label=QLabel('Salary of one worker per hour')
        self.salary_input = QLineEdit()
        self.layout.addWidget(self.salary_label)
        self.layout.addWidget(self.salary_input)

        # input field for price of one kilo of wood
        self.wood_price_label=QLabel('Price of one kilo of wood')
        self.wood_price_input = QLineEdit()
        self.layout.addWidget(self.wood_price_label)
        self.layout.addWidget(self.wood_price_input)

        # button to add toy
        self.add_toy_btn = QPushButton('Add Toy')
        self.add_toy_btn.clicked.connect(self.add_toy)
        self.layout.addWidget(self.add_toy_btn)

        # create a grid layout for toy inputs
        self.input_grid_layout = QGridLayout()
        self.toy_inputs = []
        self.add_toy()
        self.layout.addLayout(self.input_grid_layout)

        self.solve_btn = QPushButton('Solve')
        self.solve_btn.clicked.connect(self.solve)
        self.layout.addWidget(self.solve_btn)

        self.setLayout(self.layout)

    def add_toy(self):
        # Create a new tuple for the inputs of the current toy
        toy_inputs = (QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit(),QLineEdit())
        labels = ['Hours of manual work', 'Hours of machine work', 'Kilos of wood', 'Selling price', 'Maximum sold']

        # Add the QLineEdit objects to the grid layout
        row = len(self.toy_inputs)+1  # Add 1 to account for the labels row
        for col, toy_input in enumerate(toy_inputs):
            toy_input.setPlaceholderText(labels[col])
            self.input_grid_layout.addWidget(toy_input, row, col)

        # Add a remove button for each toy except the first
        if row !=1:
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda: self.remove_toy(row))
            self.input_grid_layout.addWidget(remove_btn, row, 5)
            self.toy_inputs.append(toy_inputs)
        else:
            self.toy_inputs.append(toy_inputs)

    def remove_toy(self, row):
        for i in range(6):
            # get input at coordinates (row,i)
            item = self.input_grid_layout.itemAtPosition(row, i)
            if item:
                # retrieve widget(cell) corresponding to item
                widget = item.widget()
                if widget:
                    # safely delete cell
                    widget.deleteLater()
        self.toy_inputs.pop(row-1)

    def solve(self):
        #data extraction from GUI
        nb_toys = len(self.toy_inputs)
        max_hours_per_worker = float(self.max_hours_per_worker_input.text())
        max_machine_hours = float(self.max_hours_machine_input.text())
        max_wood = float(self.max_wood_input.text())
        wood_price = float(self.wood_price_input.text())
        max_nb_workers = float(self.max_workers_input.text())
        salary_hour = float(self.salary_input.text())
        max_hours_manual_work = max_hours_per_worker*max_nb_workers
        availability_resources = [max_hours_manual_work, max_machine_hours, max_wood, max_nb_workers]
        benefits = []
        consumption_resources = []
        demand_constraints = []
         # Extract data for each toy
        for toy_input in self.toy_inputs:
            hours = float(toy_input[0].text())
            machine_hours = float(toy_input[1].text())
            wood = float(toy_input[2].text())
            price = float(toy_input[3].text())
            demand = float(toy_input[4].text())
            # Calculate benefit for the toy
            toy_benefit = price - wood * wood_price - hours * salary_hour
            # Collect consumption resources for the toy
            toy_consumption_resources = [hours, machine_hours, wood]
            benefits.append(toy_benefit)
            consumption_resources.append(toy_consumption_resources)
             # Collect demand constraints for the toy
            demand_constraints.append(demand)
        print("consumption resources:", consumption_resources)
        print("demand constraints:", demand_constraints)
        print("benefits", benefits)
        print("availabilty resources",availability_resources)

        builder = GurobiSolverBuilder()
        solver = (builder
                    .add_variables(nb_toys, names=[f"Toy_{i+1}" for i in range(nb_toys)])  
                    .add_constraints(consumption_resources, availability_resources)  
                    .set_coeff_decision_variables(benefits)  
                    .set_objective(GRB.MAXIMIZE)  # Maximizing profit
                    .build()
                )
        solver.solve()
        solution=solver.get_variables()
        print("Solution:")
        for var_name, var_value in solution.items():
            print(f"{var_name} = {var_value}")
        print("Optimal Objective Value:", solver.get_objective_value())

# instantiate and display the GUI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    #apply styles
    # app.setStyleSheet(style_sheet)
    window = ToyFactoryGUI()
    window.show()
    sys.exit(app.exec_())


