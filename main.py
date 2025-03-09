import os
import sys
import threading

from sympy import Q
from test import test, match
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QFileDialog, QLabel, QListWidget, QComboBox, QLineEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class FolderSelectorApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Quick Hacker")
        self.setGeometry(200, 300, 500, 700)
        
        self.folder_list = []  # 用于存储已选择的文件夹路径

        # 初始化UI
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        layout = QVBoxLayout()

        # 设置背景颜色
        self.setStyleSheet("background-color: #f0f0f0;")
        
        self.type_label = QLabel("选择测试类型", self)
        self.type_label.setFont(QFont("Microsoft YaHei", 12))
        self.type_label.setAlignment(Qt.AlignCenter)  # 标签居中
        self.type_label.setStyleSheet("color: #333333;")  # 设置字体颜色
        layout.addWidget(self.type_label)
        self.comboBox1 = QComboBox(self)
        self.comboBox1.addItems(["三角函数only", "三角函数+递归函数"])
        self.comboBox1.setFixedHeight(40)
        self.comboBox1.setStyleSheet("background-color: #ffffff; border: 1px solid #cccccc;")  # 设置背景和边框
        self.comboBox1.setFont(QFont("Microsoft YaHei", 12))
        self.comboBox1.currentIndexChanged.connect(self.update_comboBox2)
        layout.addWidget(self.comboBox1)
        
        self.method_label = QLabel("选择评测方式", self)
        self.method_label.setFont(QFont("Microsoft YaHei", 12))
        self.method_label.setAlignment(Qt.AlignCenter)  # 标签居中
        self.method_label.setStyleSheet("color: #333333;")  # 设置字体颜色
        layout.addWidget(self.method_label)
        self.comboBox2 = QComboBox(self)
        self.comboBox2.addItems(["sympy比对", "对拍"])
        self.comboBox2.setFixedHeight(40)
        self.comboBox2.setStyleSheet("background-color: #ffffff; border: 1px solid #cccccc;")  # 设置背景和边框
        self.comboBox2.setFont(QFont("Microsoft YaHei", 12))
        self.comboBox2.currentIndexChanged.connect(self.add_fileSelector)
        layout.addWidget(self.comboBox2)
        
        self.matchFolderPathEdit = QLineEdit(self)
        self.matchFolderPathEdit.setPlaceholderText("对拍文件路径")
        self.matchFolderPathEdit.setFont(QFont("Microsoft YaHei", 12))
        self.matchFolderPathEdit.setFixedHeight(40)
        self.matchFolderPathEdit.setVisible(False)
        self.matchFolderPathEdit.setStyleSheet("background-color: #ffffff; border: 1px solid #cccccc;")
        layout.addWidget(self.matchFolderPathEdit)
        
        # 创建选择文件夹的按钮
        self.matchFolderButton = QPushButton("选择对拍文件", self)
        self.matchFolderButton.setEnabled(False)  # 初始时禁用按钮
        self.matchFolderButton.setFont(QFont("Microsoft YaHei", 12))
        self.matchFolderButton.clicked.connect(self.select_match_folder)
        self.matchFolderButton.setVisible(False) 
        self.matchFolderButton.setStyleSheet("""
            QPushButton {
                background-color: #d3d3d3; 
                color: black; 
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
        """)  # 设置按钮样式
        layout.addWidget(self.matchFolderButton)

        # 创建并美化标签，显示选择的文件夹
        self.folder_label = QLabel("已选测试文件", self)
        self.folder_label.setFont(QFont("Microsoft YaHei", 12))  # 设置字体
        self.folder_label.setAlignment(Qt.AlignCenter)  # 标签居中
        self.folder_label.setStyleSheet("color: #333333;")  # 设置字体颜色
        layout.addWidget(self.folder_label)

        # 创建并美化列表控件，显示已选择的文件夹
        self.folder_list = QListWidget(self)
        self.folder_list.setFont(QFont("Arial", 12))  # 设置字体
        self.folder_list.setStyleSheet("background-color: #ffffff; border: 1px solid #cccccc;")  # 设置背景和边框
        layout.addWidget(self.folder_list)

        # 创建选择文件夹按钮并美化
        self.select_button = QPushButton("Add Folders", self)
        self.select_button.setFont(QFont("Microsoft YaHei", 12))
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #d3d3d3; 
                color: black; 
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
        """)  # 设置按钮样式
        self.select_button.clicked.connect(self.select_folders)
        layout.addWidget(self.select_button)

        # 创建并美化测试按钮
        self.test_button = QPushButton("Hack now!", self)
        self.test_button.setFont(QFont("Microsoft YaHei", 12))
        self.test_button.setStyleSheet("""
            QPushButton {
                background-color: #d3d3d3; 
                color: black; 
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0c0c0;
            }
        """)  # 设置按钮样式
        self.test_button.clicked.connect(self.hack)
        layout.addWidget(self.test_button)

        # 添加间距以美化布局
        layout.addSpacing(20)

        # 设置窗口的布局
        self.setLayout(layout)

    def update_comboBox2(self):
        """根据第一个下拉菜单的选择更新第二个下拉菜单"""
        selected = self.comboBox1.currentText()
        
        # 根据第一个菜单的选择更新第二个菜单的选项
        if selected == "三角函数only":
            self.comboBox2.clear()
            self.comboBox2.addItems(["sympy比对", "对拍"])
            self.matchFolderButton.setEnabled(False)  # 禁用按钮
            self.matchFolderButton.setVisible(False)  # 隐藏标签
            self.matchFolderPathEdit.setVisible(False)  # 隐藏输入框
        elif selected == "三角函数+递归函数":
            self.comboBox2.clear()
            self.comboBox2.addItem("对拍") 
            
    def add_fileSelector(self):
        self.matchFolderButton.setEnabled(True)  # 启用按钮
        self.matchFolderButton.setVisible(True)  # 显示标签
        self.matchFolderPathEdit.setVisible(True)  # 显示输入框
        
    def select_match_folder(self):
        path = QFileDialog.getExistingDirectory(self, "Select Folder", "", QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if path:
            self.matchFolderPathEdit.setText(path)
            
    def select_folders(self):
        """弹出文件夹选择框，可添加多个文件夹"""
        folders = QFileDialog.getExistingDirectory(self, "Select Folder", "", QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)
        if folders:
            # 支持选择多个文件夹时，返回的会是一个包含多个路径的列表
            list = folders.split(';')  # 使用分号分割多个选择的文件夹路径
            for folder in list:
                self.folder_list.addItem(folder)  # 在列表中添加已选择的文件夹路径
            self.update_folder_label()  # 更新标签内容
            
    def hack(self):
        selected = self.comboBox2.currentText()
        if selected == "sympy比对":
            folder_count = self.folder_list.count()
            for i in range(folder_count):
                folder = self.folder_list.item(i).text()
                test(folder)
            print("All files have been hacked")
        elif selected == "对拍":
            match_folder = self.matchFolderPathEdit.text()
            folder_count = self.folder_list.count()
            for i in range(folder_count):
                folder = self.folder_list.item(i).text()
                match(match_folder=match_folder,test_folder=folder)
            print("All files have been hacked")
            
    def update_folder_label(self):
        """更新标签内容，显示已选择的文件夹"""
        folder_count = self.folder_list.count()
        if folder_count > 0:
            self.folder_label.setText(f"已选择{folder_count}个测试文件")
        else:
            self.folder_label.setText("选择测试文件")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = FolderSelectorApp()
    window.show()

    sys.exit(app.exec_())

