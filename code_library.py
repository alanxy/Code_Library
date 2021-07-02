from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import pandas as pd
import math
import importlib.util
from customized_widget import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = pd.read_csv("code.csv")
        self.LEVEL = self.db.shape[1] - (len(self.db.columns) - [i for i, word in enumerate(self.db.columns) if word.startswith('Unnamed:')][0])

        self.setWindowTitle("Code Library")

        pagelayout = QVBoxLayout()
        menu_layout = QHBoxLayout()

        main_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

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

        main_layout.addLayout(self.stacklayout, 5)
        main_layout.addLayout(des_layout, 5)

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

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedWidth(50)
        self.back_btn.pressed.connect(self.goBack)
        self.back_btn.setEnabled(False)
        self.path_label = QLabel("")
        menu_layout.addWidget(self.back_btn)
        menu_layout.addWidget(self.path_label)

        self.run_btn = QPushButton("run")
        self.run_btn.setEnabled(False)
        self.run_btn.index = -1
        self.run_btn.pressed.connect(self.openFile)
        run_layout.addWidget(self.run_btn)

        # self.test_btn = QPushButton("run")
        # self.test_btn.pressed.connect(self.test)
        # run_layout.addWidget(self.test_btn)

        for i in self.list:
            self.stacklayout.addWidget(i)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def listClick(self):
        idx = self.stacklayout.currentIndex()
        # print("clicked list " + str(idx))
        if idx >= self.LEVEL - 1:
            # print("ready to run")
            self.fileClick()
        else:
            # print(self.list[0].currentItem().text())
            selected = self.list[idx].currentItem().text()
            # print("length is " + str(len(self.db.iloc[self.list[idx].map(selected)])))
            # print(str(self.db.iloc[self.list[idx].map(selected)]))
            if len(self.db.iloc[self.list[idx].map(selected)]) == 1:
                row = self.db.iloc[self.list[idx].map(selected)].index
                # print(row)
                # print(idx)
                # print(self.db.iloc[row, idx+1].values[0])
                # print(type(self.db.iloc[row, idx+1].values[0]))
                if (not isinstance(self.db.iloc[row, idx+1].values[0], str)) and math.isnan(self.db.iloc[row, idx+1]):
                    self.fileClick()
                    return

            # print(self.db[self.db.iloc[:,0] == self.list[0].currentItem().text()].iloc[:,1].values)
            self.list[idx+1].clear()
            self.list[idx+1].setup(sorted(self.db.iloc[self.list[idx].map(selected)].iloc[:,idx+1].values))
            self.stacklayout.setCurrentIndex(idx+1)
            self.list[idx+1].createMap(self.db.iloc[self.getCurrentSelectedRows(), :])

            self.back_btn.setEnabled(True)
            self.run_btn.setEnabled(False)
            self.run_btn.index = -1

        self.updatePath(idx)

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

    def updatePath(self, idx):
        path_list = []
        for i in range(idx+1):
            path_list.append(self.list[i].currentItem().text())
        self.path_label.setText(" > ".join(path_list))

    def openFile(self):
        file = self.dir_label.text()
        extension = file.split(".")[-1]
        if extension == "csv" or extension == "xlsm":
            os.system("start " + file)
            # MACOS: os.system("open " + filename)
            # Windows: os.system("start " + filename)
        elif extension == "py":
            if isinstance(self.db['require_input'].values[self.run_btn.index], str):
                input = self.db['require_input'].values[self.run_btn.index]
                dialog = MultiInputDialog(input.split(";"))
                if dialog.exec():
                    retval = dialog.getInputs()
                    spec = importlib.util.spec_from_file_location("module", file)
                    foo = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(foo)
                    try:
                        ret_msg = foo.function(retval)
                        print(ret_msg)
                        if ret_msg is not None:
                            msg = QMessageBox()
                            msg.setText(ret_msg)
                            msg.setWindowTitle("Notification")
                            retval = msg.exec_()
                    except:
                        print("The function is buggy.")
            else:
                os.system("python " + file)

    def getCurrentSelectedRows(self):
        idx = self.stacklayout.currentIndex()
        if idx <= 0:
            return range(len(self.db))
        else:
            # print("selecting from list " + str(idx))
            prev_selected = self.list[idx-1].currentItem().text()
            return self.list[idx-1].map(prev_selected)

    # def test(self):
    #     idx = self.stacklayout.currentIndex()
    #     current_item = self.list[idx].currentItem().text()
    #     text, ok = QInputDialog.getText(self, 'Input', 'RTL name:')
    #     print("python " + self.db.iloc[self.list[idx].map(current_item), -1].values[0] + " " + str(text))
    #     os.system("python " + self.db.iloc[self.list[idx].map(current_item), -1].values[0] + " " + str(text))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(600, 400)
    win.show()
    sys.exit(app.exec_())
