from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import os
import pandas as pd

class ListWidget(QListWidget):
    def __init__(self, idx):
        super().__init__()
        self.idx = idx

    def setup(self, list):
        for i in list:
            self.addItem(i)

    def createMap(self, df):
        item_list = set(df.iloc[:, self.idx])
        self.item2index = {i: df[df.iloc[:,self.idx] == i].index for i in item_list}

    def map(self, current_item):
        return self.item2index[current_item]

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.db = pd.read_csv("code.csv")
        self.LEVEL = self.db.shape[1] - 1

        self.setWindowTitle("Code Library")

        pagelayout = QVBoxLayout()
        menu_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()
        run_layout = QHBoxLayout()

        pagelayout.addLayout(menu_layout)
        pagelayout.addLayout(self.stacklayout)
        pagelayout.addLayout(run_layout)

        self.list = [ListWidget(i) for i in range(self.LEVEL)]
        for i in self.list:
            i.itemClicked.connect(self.listClick)
            # i.setSortingEnabled(True)

        self.list[0].setup(sorted(set(self.db.iloc[:,0])))
        self.list[0].createMap(self.db.iloc[self.getCurrentSelectedRows()])

        self.back_btn = QPushButton("<")
        self.back_btn.setFixedWidth(50)
        self.back_btn.pressed.connect(self.goBack)
        self.back_btn.setEnabled(False)
        self.path_label = QLabel("")
        menu_layout.addWidget(self.back_btn)
        menu_layout.addWidget(self.path_label)

        self.run_btn = QPushButton("open")
        self.run_btn.setEnabled(False)
        self.run_btn.pressed.connect(self.openFile)
        run_layout.addWidget(self.run_btn)

        self.test_btn = QPushButton("run")
        self.test_btn.pressed.connect(self.test)
        run_layout.addWidget(self.test_btn)

        self.stacklayout.addWidget(self.list[0])
        self.stacklayout.addWidget(self.list[1])

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def listClick(self):
        idx = self.stacklayout.currentIndex()
        if idx >= self.LEVEL - 1:
            print("ready to run")
            self.run_btn.setEnabled(True)
        else:
            self.back_btn.setEnabled(True)
            self.run_btn.setEnabled(False)
            # print(self.list[0].currentItem().text())
            selected = self.list[0].currentItem().text()
            # print(self.db[self.db.iloc[:,0] == self.list[0].currentItem().text()].iloc[:,1].values)
            self.list[1].clear()
            self.list[1].setup(sorted(self.db[self.db.iloc[:,0] == self.list[0].currentItem().text()].iloc[:,1].values))
            self.stacklayout.setCurrentIndex(idx+1)
            self.list[1].createMap(self.db.iloc[self.getCurrentSelectedRows(), :])

        self.updatePath(idx)

    def goBack(self):
        idx = self.stacklayout.currentIndex()
        self.list[idx].clear()
        self.stacklayout.setCurrentIndex(idx-1)
        self.run_btn.setEnabled(False)
        if idx - 1 <= 0:
            self.back_btn.setEnabled(False)
            self.path_label.setText("")
        else:
            self.updatePath(idx)

    def updatePath(self, idx):
        path_list = []
        for i in range(idx+1):
            path_list.append(self.list[i].currentItem().text())
        self.path_label.setText(" > ".join(path_list))

    def openFile(self):
        idx = self.stacklayout.currentIndex()
        current_item = self.list[idx].currentItem().text()
        print(self.db.iloc[self.list[idx].map(current_item), -1].values[0])
        os.system("start " + self.db.iloc[self.list[idx].map(current_item), -1].values[0])
        # MACOS os.system("open " + )
        # Windows os.system("start " + )

    def getCurrentSelectedRows(self):
        idx = self.stacklayout.currentIndex()
        if idx <= 0:
            return range(len(self.db))
        else:
            prev_selected = self.list[idx-1].currentItem().text()
            return self.list[idx-1].map(prev_selected)

    def test(self):
        idx = self.stacklayout.currentIndex()
        current_item = self.list[idx].currentItem().text()
        text, ok = QInputDialog.getText(self, 'Input', 'RTL name:')
        print("python " + self.db.iloc[self.list[idx].map(current_item), -1].values[0] + " " + str(text))
        os.system("python " + self.db.iloc[self.list[idx].map(current_item), -1].values[0] + " " + str(text))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
