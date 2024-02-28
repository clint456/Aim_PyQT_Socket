"""
本程序使用的库：
Resource为资源文件，里面储存了ui界面涉及到的图片等资源信息。部分编译器可能会提示没有使用该库文件。但是在
动态加载ui界面的过程中，该文件必不可少。Resource.qrc文件是用QTdesigner设计完成后自动生成的，然后需要
使用python的pyside2库中自带的转换工具将.qrc文件转换成.py文件。这样才能被python所识别。注意这里还需要
将Resource.py文件放在主程序（使用该ui资源文件的程序）相同的目录下。
PySide2为写QT程序的库。matplotlib为作图常用库。sklearn是机器学习库。NEAUfunc2中包含吴其恒写的相关函数。
numpy是数值计算库。webbrowser库用于打开某个网页，在该软件中用来打开东北农业大学官网。
"""
import sklearn.metrics._pairwise_distances_reduction._middle_term_computer
import sklearn.metrics._pairwise_distances_reduction._datasets_pair
import Resource
from PySide2.QtUiTools import QUiLoader
from PySide2.QtGui import *
from PySide2.QtCore import *
from PySide2.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox, QFileDialog
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.backends.backend_qt5agg import (
    FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
from sklearn.cluster import OPTICS, cluster_optics_dbscan
from NEAUfunc2 import wgs842gk, Delaunaycal, ClusterDecal
import numpy as np
import webbrowser

"""
这里先定义全局变量，data_path为数据集地址，字符型变量。
"""
data_path: str = ''

"""
定义函数checkinput(self):该函数用于检查输入情况
以第一个if语句为例进行说明：
    self.ui.lineEdit.text()      代表的是当前ui界面里面的lineEdit控件的文本内容，lineEdit为一个单行文本框。
同理 self.ui.doubleSpinBox.text() 代表的是当前ui界面里面的doubleSpinBox控件的文本内容，doubleSpinBox为一个双精度数字显示控件。
    self.ui.label_14.setText("错误：请输入农机实际作业幅宽！")  代表的是在当前ui界面里面的label_14控件更改文本内容为"错误：请输入农机实际作业幅宽！"
QMessageBox.critical(self.ui,'错误','请输入农机实际作业幅宽！') 函数用于弹出一个错误提示框，括号内的第一个参数表示在当前ui上，第二个参数是设置错误提示框的标题栏内容为’错误‘，第三个参数是设置提示框内容。

综上，checkinput(self)函数就是用来检查哪个本应设置的参数为空，显示提示信息并弹出错误提示框。
"""


def checkinput(self):
    # 检查输入情况
    if self.ui.lineEdit.text() == '' and not (self.ui.doubleSpinBox.text() == '0.00') and not (
            self.ui.lineEdit_2.text() == ''):
        self.ui.label_14.setText("错误：请输入农机实际作业幅宽！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请输入农机实际作业幅宽！')

    if self.ui.doubleSpinBox.text() == '0.00' and not (self.ui.lineEdit.text() == '') and not (
            self.ui.lineEdit_2.text() == ''):
        self.ui.label_14.setText("错误：请设置纵向横向插值比例！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请设置纵向横向插值比例！')

    if self.ui.lineEdit_2.text() == '' and not (self.ui.lineEdit.text() == '') and not (
            self.ui.doubleSpinBox.text() == '0.00'):
        self.ui.label_14.setText("错误：请设置文件路径！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请设置文件路径！')

    if self.ui.lineEdit.text() == '' and self.ui.doubleSpinBox.text() == '0.00' and not (
            self.ui.lineEdit_2.text() == ''):
        self.ui.label_14.setText("错误：请输入农机实际作业幅宽！请设置纵向横向插值比例！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请输入农机实际作业幅宽！\n请设置纵向横向插值比例！')

    if self.ui.doubleSpinBox.text() == '0.00' and not (self.ui.lineEdit.text() == '') and (
            self.ui.lineEdit_2.text() == ''):
        self.ui.label_14.setText("错误：请设置文件路径！请设置纵向横向插值比例！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请设置文件路径！\n请设置纵向横向插值比例！')

    if self.ui.lineEdit_2.text() == '' and self.ui.lineEdit.text() == '' and not (
            self.ui.doubleSpinBox.text() == '0.00'):
        self.ui.label_14.setText("错误：请设置文件路径！请输入农机实际作业幅宽！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请设置文件路径！\n请输入农机实际作业幅宽！')

    if self.ui.lineEdit_2.text() == '' and self.ui.lineEdit.text() == '' and (
            self.ui.doubleSpinBox.text() == '0.00'):
        self.ui.label_14.setText("错误：请设置路径与参数！")
        QMessageBox.critical(
            self.ui,
            '错误',
            '请设置路径与参数！')


"""
pyside2里面的内置控件有时候不能满足我们的需求，比如在该程序中需要显示matplotlib绘制的图像。那么我们需要一个定制的控件来满足我们的需求。
class MplWidget(QWidget):这里就是在QWidget控件的基础上进行改造升级得到新的控件MplWidget和MplWidget_2
MplWidget包含了matplotlib中的工具箱和一个只有一个坐标轴的画布
MplWidget_2包含了matplotlib中的工具箱和一个包含四个坐标轴的画布
"""


class MplWidget(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())  # self.canvas设置为matplotlib中的FigureCanvas，定义了画布

        vertical_layout = QVBoxLayout()  # 定义一种布局结构vertical_layout，将其设置为QVBoxLayout()布局，即在垂直方向上排列控件
        vertical_layout.addWidget(self.canvas)  # 在vertical_layout布局中添加self.canvas
        vertical_layout.addWidget(NavigationToolbar(self.canvas, self))  # 在vertical_layout布局中添加NavigationToolbar工具箱
        self.canvas.axes = self.canvas.figure.add_subplot(111)  # 在self.canvas画布中只画一张图就是添加一个坐标轴add_subplot(111)
        self.setLayout(vertical_layout)  # 给该控件MplWidget设置布局vertical_layout


class MplWidget_2(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.canvas = FigureCanvas(Figure())

        vertical_layout = QVBoxLayout()
        vertical_layout.addWidget(self.canvas)
        vertical_layout.addWidget(NavigationToolbar(self.canvas, self))
        self.canvas.ax1 = self.canvas.figure.add_subplot(211)  # 这里是设置四个坐标轴，后面分别进行绘制
        # add_subplot(211) 是指把画布分成两行一列2X1的两个部分，在第一个部分设置坐标轴，并把坐标轴命名为self.canvas.ax1
        self.canvas.ax2 = self.canvas.figure.add_subplot(234)
        # add_subplot(234) 是指把画布分成两行三列2X3的六个部分，在第四个部分设置坐标轴，并把坐标轴命名为self.canvas.ax2
        self.canvas.ax3 = self.canvas.figure.add_subplot(235)
        self.canvas.ax4 = self.canvas.figure.add_subplot(236)
        self.canvas.figure.subplots_adjust(hspace=0.355, wspace=0.315)  # 这里是设置四个坐标轴间的上下间距
        self.setLayout(vertical_layout)


"""
这里后面有四个class:
class MainWidget_old(QWidget):定义不用聚类方法的程序界面。
class MainWidget_new(QWidget):定义使用聚类方法的程序界面。
class Choose(QWidget):定义完成登录后选择采用哪种方法的选择程序界面。
class Register(QWidget):定义登录与注册界面。
"""


class MainWidget_old(QWidget):

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        QWidget.__init__(self)
        loader = QUiLoader()
        loader.registerCustomWidget(MplWidget)
        self.ui = loader.load('ui/ImppTs_old.ui')
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.setAttribute(Qt.WA_TranslucentBackground)
        # self.ui.setMouseTracking(True)

        # 初始化图窗名称
        self.ui.mplWidget1.canvas.axes.set_title('Working track')
        self.ui.mplWidget1.canvas.draw()

        self.ui.mplWidget2.canvas.axes.set_title('Working area')
        self.ui.mplWidget2.canvas.draw()

        self.ui.mplWidget3.canvas.axes.set_title('Schematic example')
        self.ui.mplWidget3.canvas.draw()

        self.ui.mplWidget3_2.canvas.axes.set_title('Working track')
        self.ui.mplWidget3_2.canvas.draw()

        self.ui.mplWidget3_3.canvas.axes.set_title('Working area')
        self.ui.mplWidget3_3.canvas.draw()

        self.ui.mplWidget3_4.canvas.axes.set_title('Schematic example')
        self.ui.mplWidget3_4.canvas.draw()

        self.ui.pushButton.clicked.connect(self.instruct0)  # 加载文件按钮pushButton
        self.ui.pushButton_9.clicked.connect(self.instruct1)  # 计算作业面积按钮pushButton_9
        self.ui.btn_close_8.clicked.connect(self.instruct2)  # 跳转官网按钮btn_close_8
        self.ui.pushButton_2.clicked.connect(self.instruct3)  # 独立窗口打开图片按钮pushButton_2
        self.ui.pushButton_4.clicked.connect(self.instruct4)  # 储存数据按钮左pushButton_4
        self.ui.pushButton_5.clicked.connect(self.instruct5)  # 储存数据按钮右pushButton_5

    def instruct0(self):
        global data_path
        data_path, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要上传的数据集",  # 标题
            r"data_example\\黑02-N6709 11-02轨迹.csv",  # 起始目录
            "图片类型 (*.csv *.mat *.excel *.txt)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.lineEdit_2.setText(data_path)

    def instruct1(self):
        global data_path
        self.ui.label_14.setText("正在计算中.......")
        checkinput(self)
        print("数据集地址为：" + data_path)
        # data_path1 = "E:\COWA_NEAU\data_example\黑02-N8889 11-02轨迹.csv"
        # data_path2 = "E:\COWA_NEAU\data_example\黑02-N6709 11-02轨迹.csv"
        self.ui.label_14.setText("正在计算中.......")

        width = float(self.ui.lineEdit.text())
        ratio = float(self.ui.doubleSpinBox.text())
        data = wgs842gk(data_path)
        # a = ClusterDecal(data, ratio, width)   #a为新的算法
        b = Delaunaycal(data, width=width, ratio=ratio)  # b为旧的算法
        b.calculatearea()

        self.ui.textBrowser.clear()
        self.ui.textBrowser_2.clear()
        self.ui.textBrowser.append(str(b.adinter[0]))
        self.ui.textBrowser_2.append(str(b.area[1]))
        self.ui.textBrowser.ensureCursorVisible()
        self.ui.textBrowser_2.ensureCursorVisible()

        self.ui.mplWidget1.canvas.axes.clear()  # 将该画布该坐标轴清空
        self.ui.mplWidget2.canvas.axes.clear()
        self.ui.mplWidget3.canvas.axes.clear()

        """
        以下均为画图，都是在相应控件的画布上用matplotlib的函数画图
        """

        self.ui.mplWidget1.canvas.axes.scatter(b.adinter[0][:, 0], b.adinter[0][:, 1], s=0.5, color='r')
        self.ui.mplWidget1.canvas.axes.set_title('Working track')
        self.ui.mplWidget1.canvas.draw()

        self.ui.mplWidget3_2.canvas.axes.scatter(b.adinter[0][:, 0], b.adinter[0][:, 1], s=0.5, color='r')
        self.ui.mplWidget3_2.canvas.axes.set_title('Working track')
        self.ui.mplWidget3_2.canvas.draw()

        self.ui.mplWidget2.canvas.axes.triplot(b.adinter[0][:, 0], b.adinter[0][:, 1], b.area[1],
                                               linewidth=0.5, color='b')
        self.ui.mplWidget2.canvas.axes.set_title('Working area')
        self.ui.mplWidget2.canvas.draw()

        self.ui.mplWidget3_3.canvas.axes.triplot(b.adinter[0][:, 0], b.adinter[0][:, 1], b.area[1],
                                                 linewidth=0.5, color='b')
        self.ui.mplWidget3_3.canvas.axes.set_title('Working area')
        self.ui.mplWidget3_3.canvas.draw()

        self.ui.mplWidget3.canvas.axes.triplot(b.adinter[0][:, 0], b.adinter[0][:, 1], b.area[2],
                                               linewidth=0.5, zorder=1, color='b', label='triangulation')
        self.ui.mplWidget3.canvas.axes.scatter(b.adinter[0][:, 0], b.adinter[0][:, 1], s=0.5 * 2, zorder=2,
                                               color='r', label='predict trajectory')
        self.ui.mplWidget3.canvas.axes.legend(('triangulation', 'predict  trajectory'), loc='upper left')
        self.ui.mplWidget3.canvas.axes.set_title('Schematic example')
        self.ui.mplWidget3.canvas.draw()

        self.ui.mplWidget3_4.canvas.axes.triplot(b.adinter[0][:, 0], b.adinter[0][:, 1], b.area[2],
                                                 linewidth=0.5, zorder=1, color='b', label='triangulation')
        self.ui.mplWidget3_4.canvas.axes.scatter(b.adinter[0][:, 0], b.adinter[0][:, 1], s=0.5 * 2, zorder=2,
                                                 color='r', label='predict trajectory')
        self.ui.mplWidget3_4.canvas.axes.legend(('triangulation', 'predict  trajectory'), loc='upper left')
        self.ui.mplWidget3_4.canvas.axes.set_title('Schematic example')
        self.ui.mplWidget3_4.canvas.draw()

        print("农机作业面积为：" + str(b.area[0] * 0.0015) + "亩")
        self.ui.label_14.setText("农机作业面积为：" + '%.2f' % b.area[0] * 0.0015 + "亩(保留两位小数)")
        QMessageBox.information(
            self.ui,
            '计算完成',
            "农机作业面积为：" + '%.2f' % b.area[0] * 0.0015 + "亩(保留两位小数)")

        del width, ratio

    def instruct2(self):
        webbrowser.open(url='http://www.neau.edu.cn/', new=1)  # 打开东北农业大学官网

    def instruct3(self):
        global data_path
        self.ui.label_14.setText("正在绘制中.......")
        checkinput(self)
        width = float(self.ui.lineEdit.text())
        ratio = float(self.ui.doubleSpinBox.text())
        self.ui.label_14.setText("正在绘制中.......")
        data = wgs842gk(data_path)
        caldata = Delaunaycal(data, width, ratio)
        plt.figure(1)
        caldata.interplot()
        plt.figure(2)
        caldata.tplot()
        caldata.uncuteplot()
        self.ui.label_14.setText("绘制完成！")
        plt.show(block=True)

    def instruct4(self):
        global data_path

        filePath_1, _ = QFileDialog.getSaveFileName(
            self.ui,  # 父窗口对象
            "保存文件",  # 标题
            r"COWA_NEAU\shuchu\本算法预测的农机轨迹点.csv",  # 起始目录
            "csv类型 (.csv)"  # 选择类型过滤项，过滤内容在括号中
        )
        checkinput(self)
        width = float(self.ui.lineEdit.text())
        ratio = float(self.ui.doubleSpinBox.text())
        data = wgs842gk(data_path)
        caldata = Delaunaycal(data, width=width, ratio=ratio)

        np.savetxt(filePath_1, caldata.adinter[0],
                   delimiter=",")  # 在界面中展示caldata.adinter.shape与caldata.adinter.dtype

        QMessageBox.information(
            self.ui,
            '保存成功',
            '已将数据保存到' + filePath_1)

    def instruct5(self):
        global data_path

        filePath_2, _ = QFileDialog.getSaveFileName(
            self.ui,  # 父窗口对象
            "保存文件",  # 标题
            r"COWA_NEAU\shuchu\构成本算法预测农机工作区域的单纯形顶点.csv",  # 起始目录
            "csv类型 (.csv)"  # 选择类型过滤项，过滤内容在括号中
        )
        checkinput(self)
        width = float(self.ui.lineEdit.text())
        ratio = float(self.ui.doubleSpinBox.text())
        data = wgs842gk(data_path)
        caldata = Delaunaycal(data, width, ratio)

        np.savetxt(filePath_2, caldata.area[1],
                   delimiter=",")  # 在界面中展示caldata.adinter.shape与caldata.adinter.dtype

        QMessageBox.information(
            self.ui,
            '保存成功',
            '已将数据保存到' + filePath_2)

    # 拖动窗口


class MainWidget_new(QWidget):

    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        QWidget.__init__(self)
        self.ratio = None
        self.width = None
        self.unique_label_s = None
        self.labels_s = None
        self.a = None
        loader = QUiLoader()
        loader.registerCustomWidget(MplWidget)
        loader.registerCustomWidget(MplWidget_2)
        self.ui = loader.load('ui/ImppTs_new.ui')
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.setAttribute(Qt.WA_TranslucentBackground)

        self.ui.pushButton.clicked.connect(self.instruct0)  # 加载文件按钮pushButton
        self.ui.pushButton_3.clicked.connect(self.instruct4)  # 绘制轨迹可达性图pushButton_3
        self.ui.pushButton_4.clicked.connect(self.instruct5)  # 验证确认聚类半径pushButton_4
        self.ui.pushButton_5.clicked.connect(self.instruct6)  # 验证确认聚类半径pushButton_5
        self.ui.pushButton_9.clicked.connect(self.instruct1)  # 计算作业面积按钮pushButton_9
        self.ui.btn_close_8.clicked.connect(self.instruct2)  # 跳转官网按钮btn_close_8
        self.ui.pushButton_2.clicked.connect(self.instruct3)  # 独立窗口打开图片按钮pushButton_2

    def instruct0(self):
        global data_path
        data_path, _ = QFileDialog.getOpenFileName(
            self.ui,  # 父窗口对象
            "选择你要上传的数据集",  # 标题
            r"data_example\\黑02-N6709 11-02轨迹.csv",  # 起始目录
            "图片类型 (*.csv *.mat *.excel *.txt)"  # 选择类型过滤项，过滤内容在括号中
        )
        self.ui.lineEdit_2.setText(data_path)

    def instruct4(self):
        global data_path
        self.ui.label_14.setText("正在绘制中.......")
        checkinput(self)
        print("数据集地址为：" + data_path)
        self.width = float(self.ui.lineEdit.text())
        self.ratio = float(self.ui.doubleSpinBox.text())
        epsp1 = float(self.ui.lineEdit_5.text())
        epsp2 = float(self.ui.lineEdit_4.text())

        self.ui.label_14.setText("正在绘制中.......")
        print("农机实际作业幅宽(m)：" + str(self.width))
        print("纵向横向插值比例(Radio)：" + str(self.ratio))
        print("用于观察的聚类半径1：" + str(epsp1))
        print("用于观察的聚类半径2：" + str(epsp2))
        data = wgs842gk(data_path)
        self.a = ClusterDecal(data, ratio=self.ratio, width=self.width, epsp1=epsp1, epsp2=epsp2)
        self.a.fit()

        self.ui.mplWidget1.canvas.ax1.clear()
        # 画图
        clust = self.a.clust
        labels_p1 = cluster_optics_dbscan(
            reachability=clust.reachability_,
            core_distances=clust.core_distances_,
            ordering=clust.ordering_,
            eps=self.a.epsp1,
        )
        labels_p2 = cluster_optics_dbscan(
            reachability=clust.reachability_,
            core_distances=clust.core_distances_,
            ordering=clust.ordering_,
            eps=self.a.epsp2,
        )
        reachability = clust.reachability_[clust.ordering_]
        labels = clust.labels_[clust.ordering_]
        unique_label_p1 = set(np.absolute(labels_p1))
        unique_label_p2 = set(np.absolute(labels_p2))

        # Reachability plot
        unique_label = set(np.absolute(labels))
        space = np.arange(len(self.a.X))
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label))]
        for klass, color in zip(unique_label, colors):
            Xk = space[labels == klass]
            Rk = reachability[labels == klass]
            self.ui.mplWidget1.canvas.ax1.plot(Xk, Rk, "o", markerfacecolor=color, markersize=4, markeredgecolor="none",
                                               alpha=0.3)
        self.ui.mplWidget1.canvas.ax1.plot(space[labels == -1], reachability[labels == -1], "k.", alpha=0.3)
        self.ui.mplWidget1.canvas.ax1.plot(space, np.full_like(space, self.a.epsp1, dtype=float), "k-", alpha=0.5)
        self.ui.mplWidget1.canvas.ax1.plot(space, np.full_like(space, self.a.epsp2, dtype=float), "k-.", alpha=0.5)
        self.ui.mplWidget1.canvas.ax1.set_ylabel("Reachability (epsilon distance)")
        self.ui.mplWidget1.canvas.ax1.set_title("Reachability Plot")

        # OPTICS
        for klass, color in zip(unique_label, colors):
            Xk = self.a.X[clust.labels_ == klass]
            self.ui.mplWidget1.canvas.ax2.plot(Xk[:, 0], Xk[:, 1], "o", markerfacecolor=color, markersize=4,
                                               markeredgecolor="none", alpha=0.3)
        self.ui.mplWidget1.canvas.ax2.plot(self.a.X[clust.labels_ == -1, 0], self.a.X[clust.labels_ == -1, 1], "k+",
                                           alpha=0.1)
        self.ui.mplWidget1.canvas.ax2.set_title("Automatic Clustering\nOPTICS")

        # DBSCAN at p1
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label_p1))]
        for klass, color in zip(unique_label_p1, colors):
            Xk = self.a.X[labels_p1 == klass]
            self.ui.mplWidget1.canvas.ax3.plot(Xk[:, 0], Xk[:, 1], "o", markerfacecolor=color, markersize=4,
                                               markeredgecolor="none", alpha=0.3)
        self.ui.mplWidget1.canvas.ax3.plot(self.a.X[labels_p1 == -1, 0], self.a.X[labels_p1 == -1, 1], "k+", alpha=0.1)
        self.ui.mplWidget1.canvas.ax3.set_title(f"Clustering at {self.a.epsp1} epsilon cut\nDBSCAN")

        # DBSCAN at p2
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label_p2))]
        for klass, color in zip(unique_label_p2, colors):
            Xk = self.a.X[labels_p2 == klass]
            self.ui.mplWidget1.canvas.ax4.plot(Xk[:, 0], Xk[:, 1], "o", markerfacecolor=color, markersize=4,
                                               markeredgecolor="none", alpha=0.3)
        self.ui.mplWidget1.canvas.ax4.plot(self.a.X[labels_p2 == -1, 0], self.a.X[labels_p2 == -1, 1], "k+", alpha=0.1)
        self.ui.mplWidget1.canvas.ax4.set_title(f"Clustering at {self.a.epsp2} epsilon cut\nDBSCAN")
        self.ui.mplWidget1.canvas.draw()

        self.ui.label_14.setText("绘制完成，请输入聚类半径并前往验证/确认聚类半径。")

        return self

    def instruct5(self):
        self.ui.tabWidget.setCurrentIndex(1)
        eps = float(self.ui.lineEdit_3.text())  # eps = 36
        clust = self.a.clust
        labels_s = cluster_optics_dbscan(
            reachability=clust.reachability_,
            core_distances=clust.core_distances_,
            ordering=clust.ordering_,
            eps=eps,
        )
        unique_label_s = set(np.absolute(labels_s))
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label_s))]
        for klass, color in zip(unique_label_s, colors):
            Xk = self.a.X[labels_s == klass]
            self.ui.mplWidget3_4.canvas.axes.plot(Xk[:, 0], Xk[:, 1], "o", markerfacecolor=color, markersize=4,
                                                  markeredgecolor="none",
                                                  alpha=0.3)
        self.ui.mplWidget3_4.canvas.axes.plot(self.a.X[labels_s == -1, 0], self.a.X[labels_s == -1, 1], "k+", alpha=0.1)
        self.ui.mplWidget3_4.canvas.axes.set_title(f"Clustering at {eps} epsilon cut\nDBSCAN")
        self.labels_s = labels_s
        self.unique_label_s = unique_label_s
        self.ui.mplWidget3_4.canvas.axes.set_title('The clustering results of the selected clustering radius')
        self.ui.mplWidget3_4.canvas.draw()

    def instruct6(self):
        eps = float(self.ui.lineEdit_6.text())  # eps = 36
        self.ui.mplWidget3_4.canvas.axes.clear()
        clust = self.a.clust
        labels_s = cluster_optics_dbscan(
            reachability=clust.reachability_,
            core_distances=clust.core_distances_,
            ordering=clust.ordering_,
            eps=eps,
        )
        unique_label_s = set(np.absolute(labels_s))
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label_s))]
        for klass, color in zip(unique_label_s, colors):
            Xk = self.a.X[labels_s == klass]
            self.ui.mplWidget3_4.canvas.axes.plot(Xk[:, 0], Xk[:, 1], "o", markerfacecolor=color, markersize=4,
                                                  markeredgecolor="none",
                                                  alpha=0.3)
        self.ui.mplWidget3_4.canvas.axes.plot(self.a.X[labels_s == -1, 0], self.a.X[labels_s == -1, 1], "k+", alpha=0.1)
        self.ui.mplWidget3_4.canvas.axes.set_title(f"Clustering at {eps} epsilon cut\nDBSCAN")
        self.labels_s = labels_s
        self.unique_label_s = unique_label_s
        self.ui.mplWidget3_4.canvas.axes.set_title('The clustering results of the selected clustering radius')
        self.ui.mplWidget3_4.canvas.draw()
        return self

    def instruct1(self):

        self.ui.label_21.setText("正在计算中,请耐心等待.......")
        labels_s = self.labels_s
        unique_label_s = self.unique_label_s
        colors = [plt.cm.Spectral(each) for each in np.linspace(0, 1, len(unique_label_s))]
        self.ui.mplWidget3_1.canvas.axes.clear()
        self.ui.mplWidget3_2.canvas.axes.clear()
        self.ui.mplWidget3_3.canvas.axes.clear()
        for klass, color in zip(unique_label_s, colors):
            ki = labels_s == klass
            Xk = self.a.allpoints[np.r_[ki, ki, ki]]
            tocal = Delaunaycal(Xk, width=self.width, ratio=self.width, inter='off')
            self.a.area += tocal.calculatearea()[0]

            tocal.interplot(self.ui.mplWidget3_1.canvas.axes, c=color)

            tocal.tplot(self.ui.mplWidget3_2.canvas.axes, c=color)
            hans, labs = plt.gca().get_legend_handles_labels()
            self.ui.mplWidget3_3.canvas.axes.legend(handles=hans[0::2], labels=labs[0::2])
            size = 0.5
            self.ui.mplWidget3_3.canvas.axes.triplot(tocal.adinter[0][:, 0], tocal.adinter[0][:, 1], tocal.area[2],
                                                     linewidth=size, zorder=1, color='b',
                                                     label='triangulation')
            self.ui.mplWidget3_3.canvas.axes.scatter(tocal.adinter[0][:, 0], tocal.adinter[0][:, 1], s=size * 2,
                                                     zorder=2, color='r',
                                                     label='predict trajectory')

            self.ui.mplWidget3_3.canvas.axes.legend(('triangulation', '', 'predict  trajectory'), loc='upper left')
            self.ui.mplWidget3_1.canvas.axes.set_title('Prediction of farm machinery working area after clustering')
            self.ui.mplWidget3_2.canvas.axes.set_title('Prediction of farm machinery working track after clustering')
            self.ui.mplWidget3_3.canvas.axes.set_title('Example diagram of algorithm principle')
            self.ui.mplWidget3_3.canvas.draw()

        self.ui.label_21.setText("计算成功！农机作业面积为：" + '%.2f' % self.a.area + "平方米(保留两位小数)")
        QMessageBox.information(
            self.ui,
            '计算完成',
            "农机作业面积为：" + '%.2f' % self.a.area + "平方米(保留两位小数)")

    def instruct2(self):
        webbrowser.open(url='http://www.neau.edu.cn/', new=1)

    def instruct3(self):
        global data_path
        self.ui.label_14.setText("正在绘制中.......")
        checkinput(self)
        width = float(self.ui.lineEdit.text())
        ratio = float(self.ui.doubleSpinBox.text())
        epsp1 = float(self.ui.lineEdit_5.text())
        epsp2 = float(self.ui.lineEdit_4.text())
        self.ui.label_14.setText("正在绘制中.......")
        data = wgs842gk(data_path)
        a = ClusterDecal(data, ratio=ratio, width=width, epsp1=epsp1, epsp2=epsp2)
        a.fit()
        a.reachbasedplot()
        self.ui.label_14.setText("绘制完成，请输入聚类半径并前往验证/确认聚类半径。")


class Choose(QWidget):
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        QWidget.__init__(self)
        loader = QUiLoader()
        loader.registerCustomWidget(MplWidget)
        self.ui = loader.load('ui/xuanze.ui')
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.setAttribute(Qt.WA_TranslucentBackground)

        def change_widget3():
            choose.ui.close()
            stats_old.ui.show()

        def change_widget2():
            choose.ui.close()
            stats_new.ui.show()

        self.ui.pushButton_6.clicked.connect(change_widget2)
        self.ui.pushButton_7.clicked.connect(change_widget3)


class Register(QWidget):
    def __init__(self):
        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        QWidget.__init__(self)
        loader = QUiLoader()
        loader.registerCustomWidget(MplWidget)
        self.ui = loader.load('ui/denglu.ui')
        self.ui.setWindowFlags(Qt.FramelessWindowHint)
        self.ui.setAttribute(Qt.WA_TranslucentBackground)
        self.ui.widget_3.hide()

        def change_widget3():
            self.ui.widget_2.hide()
            self.ui.widget_3.show()

        def change_widget2():
            self.ui.widget_3.hide()
            self.ui.widget_2.show()

        self.ui.pushButton.clicked.connect(change_widget2)
        self.ui.pushButton_2.clicked.connect(change_widget3)

        self.ui.pushButton_3.clicked.connect(self.denglu)
        self.ui.pushButton_6.clicked.connect(self.zhuce)

    def denglu(self):
        register.ui.close()
        choose.ui.show()

    def zhuce(self):
        choice = QMessageBox.question(
            self.ui,
            '注册成功',
            '是否直接登录，开始使用本系统？')

        if choice == QMessageBox.Yes:
            self.ui.close()
            register.ui.close()
            choose.ui.show()
        if choice == QMessageBox.No:
            self.ui.widget_3.hide()
            self.ui.widget_2.show()


app = QApplication([])
register = Register()
choose = Choose()
stats_old = MainWidget_old()
stats_new = MainWidget_new()
register.ui.show()
app.exec_()
