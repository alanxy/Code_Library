from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import pandas as pd
import math
import importlib.util
import subprocess
from customized_widget import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # read database from csv on shared drive
        self.db = pd.read_csv("S:/AlanXie/code.csv")
        # calculate number of levels
        self.LEVEL = self.db.shape[1] - (len(self.db.columns) - [i for i, word in enumerate(self.db.columns) if word.startswith('Unnamed:')][0])

        self.setWindowTitle("Code Library")

        pagelayout = QVBoxLayout()
        menu_layout = QHBoxLayout()

        main_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        # create des_layout on the right side
        des_label_title = QLabel("Description:")
        self.des_label = QLabel("")
        self.des_label.setWordWrap(True)
        dir_label_title = QLabel("Source file:")
        self.dir_label = QLabel("")
        des_layout = QVBoxLayout()
        des_layout.addWidget(des_label_title, 1)
        des_layout.addWidget(self.des_label, 7)
        des_layout.addWidget(dir_label_title, 1)
        des_layout.addWidget(self.dir_label, 1)
        des_layout.setAlignment(Qt.AlignTop)
        self.des_label.setAlignment(Qt.AlignTop)
        self.dir_label.setAlignment(Qt.AlignTop)

        # add main_layout on the left side
        main_layout.addLayout(self.stacklayout, 5)
        main_layout.addLayout(des_layout, 5)

        # add run_layout at the buttom
        run_layout = QHBoxLayout()
        pagelayout.addLayout(menu_layout)
        pagelayout.addLayout(main_layout)
        pagelayout.addLayout(run_layout)

        self.list = [ListWidget(i) for i in range(self.LEVEL)]
        for i in self.list:
            i.itemClicked.connect(self.listClick)
            i.setSortingEnabled(True)

        # set up the first list
        self.list[0].setup(sorted(set(self.db.iloc[:,0])))
        self.list[0].createMap(self.db.iloc[self.getCurrentSelectedRows()])

        # add back button at the top left corner (in menu)
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedWidth(50)
        self.back_btn.pressed.connect(self.goBack)
        self.back_btn.setEnabled(False)
        self.path_label = QLabel("")
        menu_layout.addWidget(self.back_btn)
        menu_layout.addWidget(self.path_label)

        # add run button at the bottom
        self.run_btn = QPushButton("run")
        self.run_btn.setEnabled(False)
        self.run_btn.index = -1
        self.run_btn.pressed.connect(self.openFile)
        run_layout.addWidget(self.run_btn)

        # Testing!!!
        # uncomment the below lines and add test function in test()
        # remember to also uncomment the test() function below
        self.test_btn = QPushButton("test")
        self.test_btn.pressed.connect(self.test)
        run_layout.addWidget(self.test_btn)
        # Testing!!!

        # add empty list to list
        for i in self.list:
            self.stacklayout.addWidget(i)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    # called when items in the list is clicked
    def listClick(self):
        # get the current level
        idx = self.stacklayout.currentIndex()
        # if the last level is reached
        # if you have more levels, it is recommended to add level columns in the csv
        if idx >= self.LEVEL - 1:
            self.fileClick()
        else:
            selected = self.list[idx].currentItem().text()
            if len(self.db.iloc[self.list[idx].map(selected)]) == 1:
                row = self.db.iloc[self.list[idx].map(selected)].index
                if (not isinstance(self.db.iloc[row, idx+1].values[0], str)) and math.isnan(self.db.iloc[row, idx+1]):
                    self.fileClick()
                    return

            # item clicked is not a file, enter the next level, set up the list for next level
            self.list[idx+1].clear()
            self.list[idx+1].setup(sorted(self.db.iloc[self.list[idx].map(selected)].iloc[:,idx+1].values))
            self.stacklayout.setCurrentIndex(idx+1)
            self.list[idx+1].createMap(self.db.iloc[self.getCurrentSelectedRows(), :])

            self.back_btn.setEnabled(True)
            self.run_btn.setEnabled(False)
            self.run_btn.index = -1

        # update the path in the menu
        self.updatePath(idx)

    # called when the item in the list clicked is a file
    # update the description on the right and enable the run button at the bottom
    def fileClick(self):
        self.run_btn.setEnabled(True)
        idx = self.stacklayout.currentIndex()
        current_item = self.list[idx].currentItem().text()
        self.run_btn.index = self.list[idx].map(current_item)[0]
        try:
            self.dir_label.setText(self.db['directory'].values[self.list[idx].map(current_item)][0])
        except:
            self.dir_label.setText("")
            self.run_btn.setEnabled(False)
            self.run_btn.index = -1
        try:
            self.des_label.setText(self.db['description'].values[self.list[idx].map(current_item)][0])
        except:
            self.des_label.setText("")

    # called when the back button at the top left corner is clicked, going back to the previous level
    def goBack(self):
        self.des_label.setText("")
        self.dir_label.setText("")
        idx = self.stacklayout.currentIndex()
        self.list[idx].clear()
        self.stacklayout.setCurrentIndex(idx-1)
        self.run_btn.setEnabled(False)
        self.run_btn.index = -1
        if idx - 1 <= 0:
            self.back_btn.setEnabled(False)
            self.path_label.setText("")
        else:
            self.updatePath(idx-2)

    # update the path in the menu
    def updatePath(self, idx):
        path_list = []
        for i in range(idx+1):
            path_list.append(self.list[i].currentItem().text())
        self.path_label.setText(" > ".join(path_list))

    # called when the run button in clicked, run the file
    def openFile(self):
        file = self.dir_label.text()
        extension = file.split(".")[-1]
        # simply open the excel file
        if extension == "csv" or extension == "xlsm":
            os.system("start " + file)
            print("open " + file)
            # MACOS: os.system("open " + filename)
            # Windows: os.system("start " + filename)
        # run python script
        elif extension == "py":
            print("run " + file)
            # if input is required for the python file
            if isinstance(self.db['require_input'].values[self.run_btn.index], str):
                input = self.db['require_input'].values[self.run_btn.index]

                # if the input required is a form
                if self.db['input_type'].values[self.run_btn.index] == "form":
                    dialog = MultiInputDialog(input.split(";"))
                # if the input required is a list
                elif self.db['input_type'].values[self.run_btn.index] == "list":
                    dialog = ListInputDialog(input)

                # if default text is needed
                if self.db['default'].values[self.run_btn.index] == 'Y':
                    spec = importlib.util.spec_from_file_location("module", file)
                    foo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(foo)
                    try:
                        default_list = foo.setup()
                    except:
                        print("Error on setup")
                        return
                    dialog.setDefault(default_list)

                # pop up the input dialog and wait for user input
                if dialog.exec():
                    retval = dialog.getInputs()

                    spec = importlib.util.spec_from_file_location("module", file)
                    foo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(foo)

                    # pop up the confirm dialog, python won't be executed if user chooses no
                    confirm_msg = foo.confirm(retval)
                    reply = QMessageBox.question(self, 'Confirm', confirm_msg, QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.Yes:
                        try:
                            ret_msg = foo.function(retval)
                        except:
                            # error message if the python fucntion is buggy
                            print("The source function is buggy.")

                        # python file executed unsuccessfully
                        if ret_msg is not None and ret_msg["status"] == 0:
                            msg = QMessageBox()
                            msg.setText("Error: " + ret_msg["msg"])
                            msg.setWindowTitle("Fail")
                            retval = msg.exec_()
                        # python file executed successfully
                        elif ret_msg is not None and ret_msg["status"] == 1:
                            msg = QMessageBox()
                            msg.setText(ret_msg["msg"])
                            msg.setWindowTitle("Successful")
                            retval = msg.exec_()

                            if "type" in ret_msg:
                                if ret_msg["type"] == "dir":
                                    os.startfile(ret_msg["value"])

            # run python that doesn't need input, python is required on the user's computer
            # but no customization is reuiqred on the python scirpt
            # all printed lines will be shown in a pop up window after execution
            else:
                ret = subprocess.Popen("python " + file, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                ret_msg = ""
                for line in ret.stdout.readlines():
                    ret_msg += line.decode("utf-8")
                    ret_msg += "\n"
                if ret_msg != "":
                    msg = QMessageBox()
                    msg.setText(ret_msg)
                    msg.setWindowTitle("Message")
                    retval = msg.exec_()
                ret.stdout.close()

    # get indices of items in the database which are under items in the currently list
    def getCurrentSelectedRows(self):
        idx = self.stacklayout.currentIndex()
        if idx <= 0:
            return range(len(self.db))
        else:
            prev_selected = self.list[idx-1].currentItem().text()
            return self.list[idx-1].map(prev_selected)

    # Testing!!!
    # uncomment this and add your test function here
    # rememeber to also uncomment the button creation codes above
    def test(self):
        dialog = ListInputDialog("RTL")
        if dialog.exec():
            print("hahaha")
    # Testing!!!

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(600, 400)
    win.show()
    sys.exit(app.exec_())
