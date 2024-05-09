import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from gurobipy import GRB
from GurobiSolver import GurobiSolverBuilder
from PyQt5.QtWidgets import QPlainTextEdit, QSizePolicy

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
class SolveButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

class DeleteButton(QPushButton):
    def __init__(self, title, parent=None):
        super().__init__(title, parent)

# GUI definition
class ToyFactoryGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Production Problem')
        # arrange widgets vertically
        self.layout = QVBoxLayout()
        button1 = QPushButton('Go back to Home Page')
        button1.setStyleSheet("font-size: 16px; font-family: 'Arial'; color: #233154 ; padding: 10px;font-weight: bold;")
        button1.clicked.connect(self.open_homepage)
        self.layout.addWidget(button1)

        # input field for maximum work hours per day
        self.max_hours_per_worker_label = QLabel(
            'Maximum  hours of work (per worker) per day')
        self.max_hours_per_worker_input = QLineEdit()
        self.layout.addWidget(self.max_hours_per_worker_label)
        self.layout.addWidget(self.max_hours_per_worker_input)

        # input field for maximum hours of machine work per day
        self.max_hours_machine_label = QLabel(
            'Maximum  hours of machine work per day')
        self.max_hours_machine_input = QLineEdit()
        self.layout.addWidget(self.max_hours_machine_label)
        self.layout.addWidget(self.max_hours_machine_input)

        # input field for maximum kilos of wood per day
        self.max_wood_label = QLabel('Maximum  raw materials  per day')
        self.max_wood_input = QLineEdit()
        self.layout.addWidget(self.max_wood_label)
        self.layout.addWidget(self.max_wood_input)

        # input field for number of workers per day
        self.max_workers_label = QLabel('Number of workers available per day')
        self.max_workers_input = QLineEdit()
        self.layout.addWidget(self.max_workers_label)
        self.layout.addWidget(self.max_workers_input)

        # input field for salary/hour
        self.salary_label = QLabel('Salary of one worker per hour')
        self.salary_input = QLineEdit()
        self.layout.addWidget(self.salary_label)
        self.layout.addWidget(self.salary_input)

        # input field for price of one kilo of wood
        self.wood_price_label = QLabel('Cost of one unit of raw materials')
        self.wood_price_input = QLineEdit()
        self.layout.addWidget(self.wood_price_label)
        self.layout.addWidget(self.wood_price_input)

        # button to add toy
        self.add_toy_btn = QPushButton('Add item')
        self.add_toy_btn.clicked.connect(self.add_toy)
        self.layout.addWidget(self.add_toy_btn)

        # create a grid layout for toy inputs
        self.input_grid_layout = QGridLayout()
        self.toy_inputs = []
        self.add_toy()
        self.layout.addLayout(self.input_grid_layout)

        self.solve_btn = SolveButton('Solve')
        self.solve_btn.clicked.connect(self.solve)
        self.layout.addWidget(self.solve_btn)
        self.setLayout(self.layout)

        #  display the solution
        self.solution_display = QPlainTextEdit()
        self.solution_display.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.solution_display.setReadOnly(True)  # Make the text read-only
        self.solution_display.setHidden(True)  # Initially hidden
        self.layout.addWidget(self.solution_display)

    def add_toy(self):
        # Create a new tuple for the inputs of the current toy
        toy_inputs = (QLineEdit(), QLineEdit(),
                      QLineEdit(), QLineEdit(), QLineEdit())
        labels = ['Hours of manual work', 'Hours of machine work',
                  'Matière Première', 'Selling price', 'Maximum sold']

        # Add the QLineEdit objects to the grid layout
        row = len(self.toy_inputs) + 1  # Add 1 to account for the labels row
        for col, toy_input in enumerate(toy_inputs):
            toy_input.setPlaceholderText(labels[col])
            self.input_grid_layout.addWidget(toy_input, row, col)

        # Add a remove button for each toy except the first
        if row != 1:
            remove_btn = DeleteButton('Remove')
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
        self.toy_inputs.pop(row - 1)

    def solve(self):
        # Check for negative inputs and empty fields in the main input fields
        input_labels = {
        self.max_hours_per_worker_input: "Maximum hours per worker",
        self.max_hours_machine_input: "Maximum hours of machine work",
        self.max_wood_input: "Maximum kilos of wood",
        self.max_workers_input: "Number of workers available",
        self.salary_input: "Salary of one worker per hour",
        self.wood_price_input: "Price of matiere première"
        }

        for input_field, label in input_labels.items():
            if input_field.text() == '' or not input_field.text().replace('.', '', 1).isdigit():
                error_message = f"Error: Please enter a valid number for {label}"
                QMessageBox.critical(self, 'Error', error_message)
                return
       
        # data extraction from GUI
        nb_toys = len(self.toy_inputs)
        max_hours_per_worker = float(self.max_hours_per_worker_input.text())
        max_machine_hours = float(self.max_hours_machine_input.text())
        max_wood = float(self.max_wood_input.text())
        wood_price = float(self.wood_price_input.text())
        max_nb_workers = float(self.max_workers_input.text())
        salary_hour = float(self.salary_input.text())
        max_hours_manual_work = max_hours_per_worker * max_nb_workers
        availability_resources = [
            max_hours_manual_work, max_machine_hours, max_wood]
        benefits = []
        consumption_resources = []
        demand_constraints = []
        # Extract data for each toy
        for toy_input in self.toy_inputs:
            
            for field_index in range(5):  
                # Check if the text is empty
                if toy_input[field_index].text() == '':
                    QMessageBox.critical(
                        self, 'Error', 'Error: Please enter ' + toy_input[field_index].placeholderText())
                    return  
                
                # Check if the text contains a valid number
                if not toy_input[field_index].text().replace('.', '', 1).isdigit():
                    QMessageBox.critical(
                        self, 'Error', 'Error: Please enter a valid number for ' + toy_input[field_index].placeholderText())
                    return  
            
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

        # add 1s and 0s to consumption resources (left hand of constraint expression)
        for i in range(nb_toys):
            extra_columns = []
            for j in range(nb_toys):
                extra_columns.append(1 if i == j else 0)
            consumption_resources[i].extend(extra_columns)
        # add demand constraint of each toy to availabity_resources (right hand expression)
        for i in range(nb_toys):
            availability_resources.append(demand_constraints[i])
        print("consumption resources:", consumption_resources)
        print("demand constraints:", demand_constraints)
        print("benefits", benefits)
        print("availabilty resources", availability_resources)

        # unhide solution display
        self.solution_display.setHidden(False)

        builder = GurobiSolverBuilder()
        solver = (builder
                  .add_variables(nb_toys, names=[f"Item_{i+1}" for i in range(nb_toys)])
                  .set_constraints_LHS(consumption_resources)
                  .set_constraints_RHS(availability_resources)
                  .add_constraints(name="my_constraints")
                  .set_objective(benefits, GRB.MAXIMIZE)  # Maximizing profit
                  .build()
                  )
        solver.solve()

        if (solver.get_objective_value()!=0):
        # Extract the solution
            solution = solver.get_variables()
            solution_text = "Solution:\n"
            for var_name, var_value in solution.items():
                solution_text += f"{var_name} = {var_value}\n"
            solution_text += f"Optimal Objective Value: {solver.get_objective_value()}\n"
            font = self.solution_display.font()
            font.setPointSize(12)  
            self.solution_display.setFont(font)
            # Update the QPlainTextEdit with the solution
            self.solution_display.setPlainText(solution_text)
        else:
            self.solution_display.setPlainText("No solution found")
        
    def open_homepage(self):
        # Import inside the function to avoid circular import
        from HomePage import HomePage
        
        self.hide()  # Hide the page
        if not hasattr(self, 'homepage') or not self.homepage:  # Check if homepage is already created
            self.homepage = HomePage()
        self.homepage.show()

# instantiate and display the GUI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # apply styles
    # app.setStyleSheet(style_sheet)
    window = ToyFactoryGUI()
    window.show()
    sys.exit(app.exec_())
