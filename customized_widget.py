from PyQt5.QtWidgets import *

class ListWidget(QListWidget):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def setup(self, list):
        for i in set(list):
            self.addItem(i)

    def createMap(self, df):
        item_list = set(self.filter_nan(df.iloc[:, self.idx]))
        self.item2index = {i: df[df.iloc[:,self.idx] == i].index for i in item_list}

    def map(self, current_item):
        return self.item2index[current_item]

    def filter_nan(self, df):
        return df[df.notna()]

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
