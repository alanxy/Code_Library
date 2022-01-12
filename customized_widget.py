from PyQt5.QtWidgets import *

# list widget for the list in the main window
class ListWidget(QListWidget):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def setup(self, list):
        for i in set(list):
            self.addItem(i)

    # create a map from the items in the current list to the sub-items under each of them
    def createMap(self, df):
        item_list = set(self.filter_nan(df.iloc[:, self.idx]))
        self.item2index = {i: df[df.iloc[:,self.idx] == i].index for i in item_list}

    # return the sub-items of this item
    def map(self, current_item):
        return self.item2index[current_item]

    # remove nan
    def filter_nan(self, df):
        return df[df.notna()]

# input dialog for a form, which means different kinds of inputs are required
class MultiInputDialog(QDialog):
    def __init__(self, question_list):
        super().__init__()

        self.question_list = question_list

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        layout = QFormLayout(self)
        self.line_edit_list = [QLineEdit(self) for i in question_list]

        for i in range(len(question_list)):
            layout.addRow(question_list[i], self.line_edit_list[i])

        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return ({self.question_list[i]: self.line_edit_list[i].text() for i in range(len(self.question_list))})

    def setDefault(self, default_list):
        for i in range(len(default_list)):
            self.line_edit_list[i].setText(default_list[i])

# input dialog for a list, which means multiple values of a same category is required
class ListInputDialog(QDialog):

    def __init__(self, title):
        super().__init__()

        self.title = title

        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self);

        main_layout = QFormLayout(self)

        self.list_layout = QVBoxLayout()

        header = QHBoxLayout()
        title_label = QLabel(self.title)
        header.addWidget(title_label)
        add_btn = QPushButton("+")
        add_btn.setFixedWidth(50)
        add_btn.pressed.connect(self.addRow)
        header.addWidget(add_btn)

        main_layout.addRow(header)

        main_layout.addRow(self.list_layout)

        self.list_layout.addLayout(self.inputRow())

        main_layout.addRow(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        return [self.list_layout.itemAt(i).getInput() for i in range(self.list_layout.count())]

    def setDefault(self, default_list):
        if len(default_list) > 0:
            self.list_layout.itemAt(0).setInput(default_list[0])
            for i in range(1, len(default_list)):
                self.addRow()
                self.list_layout.itemAt(i).setInput(default_list[i])
        else:
            self.addRow()

    def addRow(self):
        self.list_layout.addLayout(self.inputRow())

    # Each inputRow is a layout with a input field on the left and a delete button on the right
    class inputRow(QHBoxLayout):
        def __init__(self):
            super().__init__()

            self.input_field = QLineEdit()
            self.addWidget(self.input_field)
            self.del_btn = QPushButton("x")
            self.del_btn.setFixedWidth(50)
            self.del_btn.pressed.connect(self.deleteThisRow)
            self.addWidget(self.del_btn)

        def deleteThisRow(self):
            self.input_field.deleteLater()
            self.del_btn.deleteLater()
            self.deleteLater()
            pass

        def getInput(self):
            return self.input_field.text()

        def setInput(self, s):
            self.input_field.setText(s)

# input dialog for file selection
class FileDialog(QFileDialog):
    def __init__(self):
        super().__init__()

    def getInputs(self):
        return self.selectedFiles()
