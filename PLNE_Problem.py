import sys
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, \
    QListWidget, QListWidgetItem, QCheckBox, QMessageBox, QDialog, QDialogButtonBox

from GurobiSolver import GurobiSolverBuilder
from gurobipy import GRB


class CelebrityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

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

        self.find_celebrity_list_button = QPushButton(
            'Find the optimal guest list')
        self.find_celebrity_list_button.clicked.connect(self.findCelebrityList)

        # Summary label widgets
        self.summary_label = QLabel('Optimal guest list and statistics:')
        self.summary_text = QListWidget()
        self.summary_label.setVisible(False)
        self.summary_text.setVisible(False)

        # Celebrity list widget
        self.celebrity_list_label = QLabel('List of all celebrities')
        self.celebrity_list = QListWidget()
        self.celebrity_list.setSelectionMode(
            QListWidget.MultiSelection)  # Enable multiple selection

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
        existing_celebrities = [self.celebrity_list.item(i).text().split(
            ' - ')[0] for i in range(self.celebrity_list.count())]
        celebrity_dialog.updateProblemsWithList(existing_celebrities)

        if celebrity_dialog.exec_() == QDialog.Accepted:
            name = celebrity_dialog.name_edit.text()
            salary = float(celebrity_dialog.salary_edit.text())
            mass = float(celebrity_dialog.mass_edit.text())
            popularity = float(celebrity_dialog.value_added_edit.text())
            is_vip = celebrity_dialog.vip_checkbox.isChecked()
            problems_with_items = celebrity_dialog.problems_with_list.selectedItems()
            problems_with = [
                item.text() for item in problems_with_items] if problems_with_items else None
            self.addCelebrityToList(
                name, salary, mass, popularity, is_vip, problems_with)

    def addCelebrityToList(self, name, salary, mass, popularity, is_vip, problems_with):
        item_text = f'{name} - Salary: {salary} - Mass: {mass} - Popularity Index: {popularity} - VIP: {is_vip}'
        if problems_with:
            problems_with_str = ' - Problems with: ' + ', '.join(problems_with)
            item_text += problems_with_str
        item = QListWidgetItem(item_text)
        item.setData(1000, (name, salary, mass,
                     popularity, is_vip, problems_with))
        self.celebrity_list.addItem(item)

    def findCelebrityList(self):
        total_celebrities = self.celebrity_list.count()
        if total_celebrities == 0:
            QMessageBox.warning(
                self, 'Warning', 'Please add at least one celebrity.')
            return
        # Check if ship weight is valid
        if not (self.weight_edit.text()) or not (self.weight_edit.text().replace('.', '', 1).isdigit()) or (float(self.weight_edit.text()) <= 0):
            QMessageBox.warning(self, 'Invalid Value',
                                'Ship weight must be given a positive value.')
            return
        # Check if budget is valid
        if not (self.budget_edit.text()) or not (self.budget_edit.text().replace('.', '', 1).isdigit()) or (float(self.budget_edit.text()) <= 0):
            QMessageBox.warning(self, 'Invalid Value',
                                'Maximum budget must be given a positive value.')
            return
        ship_weight = float(self.weight_edit.text())
        budget = float(self.budget_edit.text())
        variable_names = [f'x_{i}' for i in range(total_celebrities)]

        constraints_LHS = []
        popularities = []
        negative_salaries = []
        exists_in_boat = []
        for i in range(total_celebrities):
            item_text = self.celebrity_list.item(i).text()
            salary = item_text.split(' - ')[1]
            mass = item_text.split(' - ')[2]
            popularity = item_text.split(' - ')[3]
            vip_status = item_text.split(' - ')[4]
            salary = float(salary.split(': ')[1])
            mass = float(mass.split(': ')[1])
            popularity = float(popularity.split(': ')[1])
            item_list = [mass, salary, -
                         int(vip_status.split(': ')[1] == "True")]
            # try:
            #     problems_with = item_text.split(' - ')[5]
            #     problems_with = problems_with.split(': ')[1]
            #     problems_with = problems_with.split(', ')
            # except:
            #     problems_with = []
            # for item in problems_with:

            #     for j in range(total_celebrities):
            #         name= self.celebrity_list.item(j).text().split(' - ')[0].split(': ')[1]
            #         if(item==name):
            #             item_list.append(1)

            constraints_LHS.append(item_list)
            negative_salaries.append(-salary)
            popularities.append(popularity)
            exists_in_boat.append(1)
        objectives = [
            (popularities, GRB.MAXIMIZE), (negative_salaries, GRB.MAXIMIZE), (exists_in_boat, GRB.MAXIMIZE)]
        constraints_RHS = [ship_weight, budget, -1]

        builder = GurobiSolverBuilder()
        solver = (builder.add_variables(
            total_celebrities, names=variable_names, vtypes=[GRB.BINARY for i in range(total_celebrities)])
            .set_objectives(objectives)
            .set_constraints_LHS(constraints_LHS)
            .set_constraints_RHS(constraints_RHS)
            .build())
        solver.solve()
        solution_status = solver.get_solution_status()
        if solution_status == GRB.OPTIMAL:
            solution_values = solver.get_variables()
            self.displayOptimalGuestList(solution_values)
        else:
            QMessageBox.warning(self, 'Warning', 'No optimal solution found.')

    def displayOptimalGuestList(self, solution_values):
        self.summary_text.clear()
        self.summary_label.setVisible(True)
        self.summary_text.setVisible(True)

        # Map solution values to celebrity names and attributes
        selected_celebrities = []
        total_people = 0
        total_popularity = 0.0
        total_mass = 0.0
        total_salary = 0.0
        vip_celebrities = []
        non_vip_celebrities = []

        for i in range(self.celebrity_list.count()):
            item = self.celebrity_list.item(i)
            if not item:
                continue

            item_text = item.text()
            celebrity_name = item_text.split(' - ')[0]
            variable_key = f'x_{i}'

            if variable_key in solution_values and solution_values[variable_key] > 0.5:
                selected_celebrities.append(celebrity_name)
                _, salary, mass, popularity, vip_status = item_text.split(
                    ' - ')
                try:
                    salary_value = float(salary.split(': ')[1])
                    mass_value = float(mass.split(': ')[1])
                    popularity_value = float(popularity.split(': ')[1])
                    is_vip = vip_status.split(': ')[1] == "True"
                    print(
                        f"{celebrity_name}: {salary_value}, {mass_value}, {popularity_value}, {is_vip}")

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
                    print(
                        f"Error processing celebrity item: {item_text}. Error: {e}")

        if selected_celebrities:

            # Display total statistics
            self.summary_text.addItem(
                f"Total Number of People: {total_people}")
            self.summary_text.addItem(
                f"Average Popularity Index: {total_popularity / total_people if total_people > 0 else 0.0}%")
            self.summary_text.addItem(f"Total Mass: {total_mass} Kg")
            self.summary_text.addItem(f"Total Salary: ${total_salary}")
            self.summary_text.addItem(
                f"------------------------------------------------------")
            if vip_celebrities:
                self.summary_text.addItem("VIP Celebrities:")
                for vip in vip_celebrities:
                    self.summary_text.addItem(vip)
                self.summary_text.addItem(
                    f"------------------------------------------------------")
            if non_vip_celebrities:
                self.summary_text.addItem("Non-VIP Celebrities:")
                for non_vip in non_vip_celebrities:
                    self.summary_text.addItem(non_vip)
                self.summary_text.addItem(
                    f"------------------------------------------------------")
            self.summary_text.addItem("Selected Celebrities:")
            for celebrity in selected_celebrities:
                self.summary_text.addItem(celebrity)
        else:
            self.summary_text.addItem("No celebrities selected.")


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
        self.problems_with_list.setSelectionMode(
            QListWidget.MultiSelection)  # Enable multiple selection

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
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def updateProblemsWithList(self, existing_celebrities):
        self.problems_with_list.clear()
        self.problems_with_list.addItems(existing_celebrities)

    def accept(self):
        if self.name_edit.text() == '':
            QMessageBox.critical(
                self, 'Error', 'Please enter the celebrity name.')
        elif self.salary_edit.text() == '' or not self.salary_edit.text().replace('.', '', 1).isdigit():
            QMessageBox.critical(
                self, 'Error', 'Please enter a valid salary (decimal number).')
        elif self.mass_edit.text() == '' or not self.mass_edit.text().replace('.', '', 1).isdigit():
            QMessageBox.critical(
                self, 'Error', 'Please enter a valid mass (decimal number).')
        elif self.value_added_edit.text() == '' or not self.value_added_edit.text().replace('.', '', 1).isdigit() or int(self.value_added_edit.text()) > 100:
            QMessageBox.critical(
                self, 'Error', 'Please enter a valid popularity index (decimal number <= 100).')
        else:
            super().accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CelebrityWidget()
    window.show()
    sys.exit(app.exec_())
