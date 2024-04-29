import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QListWidget, QListWidgetItem, QCheckBox, QMessageBox, QDialog, QDialogButtonBox
from testGurobi import GurobiMultiObjectiveSolver
from gurobipy import GRB
import gurobipy as gp

class CelebrityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.problem_relationships = {}  # Dictionary to store problem relationships

    def initUI(self):
        self.setWindowTitle('Who will be your celebrity guests?')
        self.resize(800, 500)

        # Widgets for ship weight and budget input
        self.weight_label = QLabel('Total ship weight (Kg):')
        self.weight_edit = QLineEdit()

        self.budget_label = QLabel('Maximum budget ($):')
        self.budget_edit = QLineEdit()

        self.add_celebrity_button = QPushButton('Add Celebrity')
        self.add_celebrity_button.clicked.connect(self.addCelebrity)

        self.find_celebrity_list_button = QPushButton('Find the optimal guest list')
        self.find_celebrity_list_button.clicked.connect(self.findCelebrityList)

        # Summary label widgets
        self.summary_label = QLabel('Optimal guest list and statistics:')
        self.summary_text = QListWidget()
        self.summary_label.setVisible(False)
        self.summary_text.setVisible(False)

        # Celebrity list widget
        self.celebrity_list_label = QLabel('List of all celebrities')
        self.celebrity_list = QListWidget()
        self.celebrity_list.setSelectionMode(QListWidget.MultiSelection)  # Enable multiple selection

        # Layout for ship weight input
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.weight_label)
        input_layout.addWidget(self.weight_edit)

        # Layout for budget input
        input_layout.addWidget(self.budget_label)
        input_layout.addWidget(self.budget_edit)

        # Layout for adding celebrities and finding the optimal list
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_celebrity_button)
        button_layout.addWidget(self.find_celebrity_list_button)

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.summary_label)
        main_layout.addWidget(self.summary_text)
        main_layout.addWidget(self.celebrity_list_label)
        main_layout.addWidget(self.celebrity_list)

        self.setLayout(main_layout)

    def addCelebrity(self):
        celebrity_dialog = CelebrityDialog(self)
        existing_celebrities = [self.celebrity_list.item(i).text().split(' - ')[0] for i in range(self.celebrity_list.count())]
        celebrity_dialog.updateProblemsWithList(existing_celebrities)

        if celebrity_dialog.exec_() == QDialog.Accepted:
            name = celebrity_dialog.name_edit.text()
            salary = float(celebrity_dialog.salary_edit.text())
            mass = float(celebrity_dialog.mass_edit.text())
            popularity = float(celebrity_dialog.value_added_edit.text())
            is_vip = celebrity_dialog.vip_checkbox.isChecked()
            problems_with_items = celebrity_dialog.problems_with_list.selectedItems()
            problems_with = [item.text() for item in problems_with_items] if problems_with_items else None
            self.addCelebrityToList(name, salary, mass, popularity, is_vip, problems_with)

    def addCelebrityToList(self, name, salary, mass, popularity, is_vip, problems_with):
        item_text = f'{name} - Salary: {salary} - Mass: {mass} - Popularity Index: {popularity} - VIP: {is_vip}'
        if problems_with:
            problems_with_str = ' - Problems with: ' + ', '.join(problems_with)
            item_text += problems_with_str
            # Update problem relationships dictionary
            self.problem_relationships[name] = problems_with
        item = QListWidgetItem(item_text)
        item.setData(1000, (name, salary, mass, popularity, is_vip, problems_with))
        self.celebrity_list.addItem(item)

    def findCelebrityList(self):
        total_celebrities = self.celebrity_list.count()
        if total_celebrities == 0:
            QMessageBox.warning(self, 'Warning', 'Please add at least one celebrity.')
            return

        # Check if ship weight is valid
        if not self.weight_edit.text() or not self.weight_edit.text().replace('.', '', 1).isdigit() or float(self.weight_edit.text()) <= 0:
            QMessageBox.warning(self, 'Invalid Value', 'Ship weight must be given a positive value.')
            return

        # Check if budget is valid
        if not self.budget_edit.text() or not self.budget_edit.text().replace('.', '', 1).isdigit() or float(self.budget_edit.text()) <= 0:
            QMessageBox.warning(self, 'Invalid Value', 'Maximum budget must be given a positive value.')
            return

        ship_weight = float(self.weight_edit.text())
        budget = float(self.budget_edit.text())

        solver = GurobiMultiObjectiveSolver()

        # Decision variables for celebrity selection
        for i in range(total_celebrities):
            solver.add_variable(f"x_{i}")

        # Coefficients for objectives (popularity index, negative salary, number of selected celebrities)
        popularity_coefficients = [float(self.celebrity_list.item(i).text().split(' - ')[3].split(': ')[1]) for i in range(total_celebrities)]
        salary_coefficients = [-float(self.celebrity_list.item(i).text().split(' - ')[1].split(': ')[1]) for i in range(total_celebrities)]

        # Set objectives: maximize popularity, minimize total salaries, maximize number of selected celebrities
        solver.set_coeff_decision_variables(popularity_coefficients)
        solver.set_objectives([GRB.MAXIMIZE, GRB.MINIMIZE, GRB.MAXIMIZE], [1, 1, 1])

        # Constraints
        solver.add_constraint(gp.quicksum(float(self.celebrity_list.item(i).text().split(' - ')[1].split(': ')[1]) * solver.decision_variables[i] for i in range(total_celebrities)), GRB.LESS_EQUAL, budget)
        solver.add_constraint(gp.quicksum(float(self.celebrity_list.item(i).text().split(' - ')[2].split(': ')[1]) * solver.decision_variables[i] for i in range(total_celebrities)), GRB.LESS_EQUAL, ship_weight)
        # Ensure at least one VIP celebrity is selected
        solver.add_constraint(gp.quicksum(solver.decision_variables[i] for i in range(total_celebrities) if self.celebrity_list.item(i).text().split(' - ')[4].split(': ')[1] == 'True'), GRB.GREATER_EQUAL, 1)

        # Mutual exclusion constraint based on problem relationships
        for celeb, problems in self.problem_relationships.items():
            celeb_index = next((i for i in range(total_celebrities) if self.celebrity_list.item(i).text().startswith(celeb)), None)
            if celeb_index is not None:
                related_indices = [i for i in range(total_celebrities) if any(self.celebrity_list.item(i).text().startswith(p) for p in problems)]
                if related_indices:
                    # If celeb is selected, none of the related_indices should be selected
                    expr = gp.LinExpr()
                    
                    # Add the celebrity variable (xi) with its coefficient as the number of related problems
                    expr.add(solver.decision_variables[celeb_index], len(related_indices))  
                    
                    # Add related variables (xj) with a coefficient of 1 each
                    for idx in related_indices:
                        expr.add(solver.decision_variables[idx], 1)
                    print(expr)
                    # Add the constraint that ensures the total count is less than or equal to the number of related problems
                    solver.add_constraint(expr, GRB.LESS_EQUAL, len(related_indices))


        # Solve the model
        solver.build()
        solver.solve()

        # Display results
        solution_status = solver.get_solution_status()
        if solution_status == GRB.OPTIMAL:
            solution_values = solver.get_all_variable_values()
            self.displayOptimalGuestList(solution_values)
        else:
            QMessageBox.warning(self, 'Warning', 'No optimal solution found.')

            
        
    def displayOptimalGuestList(self, solution_values):
        self.summary_text.clear()
        self.summary_label.setVisible(True)
        self.summary_text.setVisible(True)

        selected_celebrities = []
        total_people = 0
        total_popularity = 0.0
        total_mass = 0.0
        total_salary = 0.0
        vip_celebrities = []
        non_vip_celebrities = []

        # Iterate over the decision variables and gather statistics for selected celebrities
        for i in range(self.celebrity_list.count()):
            item = self.celebrity_list.item(i)
            if not item:
                continue
            
            celebrity_name = item.text().split(' - ')[0]
            if f'x_{i}' in solution_values and solution_values[f'x_{i}'] > 0.5:
                selected_celebrities.append(celebrity_name)

                # Retrieve celebrity attributes
                salary_str = item.text().split(' - ')[1].split(': ')[1]
                mass_str = item.text().split(' - ')[2].split(': ')[1]
                popularity_str = item.text().split(' - ')[3].split(': ')[1]
                vip_status = item.text().split(' - ')[4].split(': ')[1]

                try:
                    salary_value = float(salary_str)
                    mass_value = float(mass_str)
                    popularity_value = float(popularity_str)
                    is_vip = vip_status == 'True'

                    # Calculate totals
                    total_people += 1
                    total_salary += salary_value
                    total_mass += mass_value
                    total_popularity += popularity_value

                    # Categorize celebrities
                    if is_vip:
                        vip_celebrities.append(celebrity_name)
                    else:
                        non_vip_celebrities.append(celebrity_name)

                except ValueError as e:
                    print(f"Error processing celebrity item: {item.text()}. Error: {e}")

        if selected_celebrities:
            # Display total statistics based on selected celebrities
            self.summary_text.addItem(f"Total Number of People: {total_people}")
            self.summary_text.addItem(f"Average Popularity Index: {total_popularity / total_people if total_people > 0 else 0.0}%")
            self.summary_text.addItem(f"Total Mass: {total_mass} Kg")
            self.summary_text.addItem(f"Total Salary: ${total_salary}")
            self.summary_text.addItem(f"------------------------------------------------------")
            if vip_celebrities:
                self.summary_text.addItem("VIP Celebrities:")
                for vip in vip_celebrities:
                    self.summary_text.addItem(vip)
                self.summary_text.addItem(f"------------------------------------------------------")
            if non_vip_celebrities:
                self.summary_text.addItem("Non-VIP Celebrities:")
                for non_vip in non_vip_celebrities:
                    self.summary_text.addItem(non_vip)
                self.summary_text.addItem(f"------------------------------------------------------")
            self.summary_text.addItem("Selected Celebrities:")
            for celebrity in selected_celebrities:
                self.summary_text.addItem(celebrity)
        else:
            self.summary_text.addItem("No celebrities selected.")

        print(self.problem_relationships)

class CelebrityDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Add a Celebrity')
        layout = QVBoxLayout()

        self.name_edit = QLineEdit()
        self.salary_edit = QLineEdit()
        self.mass_edit = QLineEdit()
        self.value_added_edit = QLineEdit()
        self.vip_checkbox = QCheckBox('VIP')
        self.problems_with_label = QLabel('Problems with:')
        self.problems_with_list = QListWidget()
        self.problems_with_list.setSelectionMode(QListWidget.MultiSelection)  # Enable multiple selection
        layout.addWidget(QLabel('Celebrity Name:'))
        layout.addWidget(self.name_edit)
        layout.addWidget(QLabel('Requested Salary ($):'))
        layout.addWidget(self.salary_edit)
        layout.addWidget(QLabel('Celebrity Mass (Kg):'))
        layout.addWidget(self.mass_edit)
        layout.addWidget(QLabel('Popularity Index (/100):'))
        layout.addWidget(self.value_added_edit)
        layout.addWidget(self.vip_checkbox)
        layout.addWidget(self.problems_with_label)
        layout.addWidget(self.problems_with_list)

        # Create button box with OK and Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def updateProblemsWithList(self, existing_celebrities):
        self.problems_with_list.clear()
        self.problems_with_list.addItems(existing_celebrities)

    def accept(self):
        if self.name_edit.text() == '':
            QMessageBox.critical(self, 'Error', 'Please enter the celebrity name.')
        elif self.salary_edit.text() == '' or not self.salary_edit.text().replace('.', '', 1).isdigit():
            QMessageBox.critical(self, 'Error', 'Please enter a valid salary (decimal number).')
        elif self.mass_edit.text() == '' or not self.mass_edit.text().replace('.', '', 1).isdigit():
            QMessageBox.critical(self, 'Error', 'Please enter a valid mass (decimal number).')
        elif self.value_added_edit.text() == '' or not self.value_added_edit.text().replace('.', '', 1).isdigit() or int(self.value_added_edit.text()) > 100:
            QMessageBox.critical(self, 'Error', 'Please enter a valid popularity index (decimal number <= 100).')
        else:
            super().accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CelebrityWidget()
    window.show()
    sys.exit(app.exec_())
