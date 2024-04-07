import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QGridLayout
#%%

class ToyFactoryGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Toy Factory Profit Maximization')
        # arrange widgets vertically
        self.layout = QVBoxLayout()

        # input field for maximum work hours per day
        self.max_hours_input = QLineEdit()
        self.max_hours_input.setPlaceholderText('Maximum work hours per day')
        self.layout.addWidget(self.max_hours_input)

        # input field for maximum kilos of wood per day
        self.max_wood_input = QLineEdit()
        self.max_wood_input.setPlaceholderText('Maximum kilos of wood per day')
        self.layout.addWidget(self.max_wood_input)

        # input field for salary/hour
        self.salary_input = QLineEdit()
        self.salary_input.setPlaceholderText('Salary per hour')
        self.layout.addWidget(self.salary_input)

        # input field for price of one kilo of wood
        self.wood_price_input = QLineEdit()
        self.wood_price_input.setPlaceholderText('Price of 1kg of wood')
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
        # Create labels for each column
        labels = ['Hours of work', 'Kilos of wood', 'Selling price', 'Maximum sold']
        for col, label_text in enumerate(labels):
            label = QLabel(label_text)
            self.input_grid_layout.addWidget(label, 0, col)

        # Create a new tuple for the inputs of the current toy
        toy_inputs = (QLineEdit(), QLineEdit(), QLineEdit(), QLineEdit())

        # Add the QLineEdit objects to the grid layout
        row = len(self.toy_inputs) + 1  # Add 1 to account for the labels row
        for col, toy_input in enumerate(toy_inputs):
            self.input_grid_layout.addWidget(toy_input, row, col)

        # Add a remove button for each toy except the first
        if row != 1:
            remove_btn = QPushButton('Remove')
            remove_btn.clicked.connect(lambda: self.remove_toy(row))
            self.input_grid_layout.addWidget(remove_btn, row, 4)
            self.toy_inputs.append(toy_inputs)
        else:
            self.toy_inputs.append(toy_inputs)

    def remove_toy(self, row):
        for i in range(5):
            # get input at coordinates (row,i)
            item = self.input_grid_layout.itemAtPosition(row, i)
            if item:
                # retrieve widget(cell) corresponding to item
                widget = item.widget()
                if widget:
                    # safely delete cell
                    widget.deleteLater()
        self.toy_inputs.pop(row)
        self.rearrange_rows()

    def rearrange_rows(self):
        """ rearrange grid after deleting a row """
        for row in range(len(self.toy_inputs)):
            for col in range(5):
                item = self.input_grid_layout.itemAtPosition(row, col)
                if item:
                    widget = item.widget()
                    if widget:
                        # re-insert cells in the correct row
                        self.input_grid_layout.addWidget(widget, row, col)

    def solve(self):
        #data extraction from GUI
        nb_toys = len(self.toy_inputs)
        max_hours = float(self.max_hours_input.text())
        max_wood = float(self.max_wood_input.text())
        wood_price = float(self.wood_price_input.text())
        salary_hour = float(self.salary_input.text())
        availability_resources = [max_hours, max_wood]
        benefits = []
        consumption_resources = []
        demand_constraints = []
        for toy_input in self.toy_inputs:
            hours = float(toy_input[0].text())
            wood = float(toy_input[1].text())
            price = float(toy_input[2].text())
            demand = float(toy_input[3].text())
            toy_benefit = price - wood * wood_price - hours * salary_hour
            toy_consumption_resources = [hours, wood]
            benefits.append(toy_benefit)
            consumption_resources.append(toy_consumption_resources)
            demand_constraints.append(demand)
        print("consumption resources:", consumption_resources)
        print("demand constraints:", demand_constraints)
        print("benefits", benefits)
        print("availabilty resources",availability_resources)

#%%
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToyFactoryGUI()
    window.show()
    sys.exit(app.exec_())