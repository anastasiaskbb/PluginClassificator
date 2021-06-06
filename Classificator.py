# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Classificator
                                 A QGIS plugin
 classification of the types of permitted use of land plots in the cadastre based on a dictionary with the possibility of supplementing it
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2021-06-02
        git sha              : $Format:%H$
        copyright            : (C) 2021 by Anastasia Zavorotnyaya
        email                : anastasiaskbb@mail.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt import QtCore, QtWidgets

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the DockWidget
from .Classificator_dockwidget import ClassificatorDockWidget
import os.path
import json
import re
import pandas as pd


class Classificator:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)

        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Classificator_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Classifer Plagin')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'Classificator')
        self.toolbar.setObjectName(u'Classificator')

        # print "** INITIALIZING Classificator"

        self.pluginIsActive = False
        self.dockwidget = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Classificator', message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/Classificator/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u''),
            callback=self.run,
            parent=self.iface.mainWindow())

    # --------------------------------------------------------------------------

    def onClosePlugin(self):
        """Cleanup necessary items here when plugin dockwidget is closed"""
        
        # print "** CLOSING Classificator"

        # disconnects
        self.dockwidget.closingPlugin.disconnect(self.onClosePlugin)

        # remove this statement if dockwidget is to remain
        # for reuse if plugin is reopened
        # Commented next statement since it causes QGIS crashe
        # when closing the docked window:
        # self.dockwidget = None

        self.pluginIsActive = False

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""

        # print "** UNLOAD Classificator"

        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Classifer Plagin'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    # --------------------------------------------------------------------------

    def run(self):
        """Run method that loads and starts the plugin"""

        if not self.pluginIsActive:
            self.pluginIsActive = True

            # print "** STARTING Classificator"

            # dockwidget may not exist if:
            #    first run of plugin
            #    removed on close (see self.onClosePlugin method)
            if self.dockwidget == None:
                # Create the dockwidget (after translation) and keep reference
                self.dockwidget = ClassificatorDockWidget()

            # connect to provide cleanup on closing of dockwidget
            self.dockwidget.closingPlugin.connect(self.onClosePlugin)

            # show the dockwidget
            # TODO: fix to allow choice of dock location
            self.iface.addDockWidget(Qt.TopDockWidgetArea, self.dockwidget)
            self.dockwidget.show()



            # Словарик с классами
            with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "r") as read_file:
                dictionary = json.load(read_file)
            print(dictionary)
            for n in dictionary:
                print(n)


            # self.dockwidget.listWidget.addItems(dictionary['Гаражи'])
            

            self.dockwidget.pushButton_3.setEnabled(False)
            self.dockwidget.pushButton_7.setEnabled(False)   

            def cls():     
                self.dockwidget.listWidget.clear()
                mass = []
                print("----------------------")
                # for key, words in dictionary.items():
                with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "r") as read_file:
                    dictionary = json.load(read_file)
                    print(dictionary)
                    for n in dictionary:
                        print(n)
                self.dockwidget.listWidget.addItems(dictionary.keys()) 
                print("----------------------")
                # self.dockwidget.listWidget.addItems(key)
 
            def cls_2():
                
                self.dockwidget.listWidget_2.clear()
                # for key in dictionary.keys():
                print(self.dockwidget.listWidget.currentItem().text())
                key = str(self.dockwidget.listWidget.currentItem().text())
                
                words = dictionary.get(key, )
                mass = []
                for word in words:
                    mass.append(word)
                self.dockwidget.listWidget_2.addItems(mass)
                        
                         
            self.dockwidget.pushButton_5.clicked.connect(cls)
            self.dockwidget.listWidget.itemClicked.connect(cls_2)
            

            def deleteEnabled_1():
                self.dockwidget.pushButton_7.setEnabled(True)

            def deleteEnabled_2():
                self.dockwidget.pushButton_3.setEnabled(True)

            self.dockwidget.listWidget.itemClicked.connect(deleteEnabled_1)
            self.dockwidget.listWidget_2.itemClicked.connect(deleteEnabled_2)


            def deleteItem():
                item = self.dockwidget.listWidget_2.selectedItems()
                for i in item:
                    self.dockwidget.listWidget_2.takeItem(self.dockwidget.listWidget_2.row(i))
                    dictionary[self.dockwidget.listWidget.currentItem().text()].remove(i.text())

                with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "w", encoding = 'utf-8') as write_file:
                    json.dump(dictionary, write_file, ensure_ascii=False )


            self.dockwidget.pushButton_3.clicked.connect(deleteItem)

            def createItem():
                if self.dockwidget.lineEdit.text()!='':
                    self.dockwidget.listWidget_2.addItem(self.dockwidget.lineEdit.text())
                    dictionary[self.dockwidget.listWidget.currentItem().text()].append(self.dockwidget.lineEdit.text())
                    with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "w", encoding = 'utf-8') as write_file:
                        json.dump(dictionary, write_file, ensure_ascii=False)

            self.dockwidget.pushButton_2.clicked.connect(createItem)


            #Удаление класса
            def deleteItem_2():
                item = self.dockwidget.listWidget.selectedItems()
                for i in item:
                    word = self.dockwidget.listWidget.currentItem().text()
                    del dictionary[word]
                    self.dockwidget.listWidget.takeItem(self.dockwidget.listWidget.row(i))
                self.dockwidget.listWidget_2.clear()

                with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "w", encoding = 'utf-8') as write_file:
                    json.dump(dictionary, write_file, ensure_ascii=False )

            self.dockwidget.pushButton_7.clicked.connect(deleteItem_2)


            #Создание класса
            def createItem_2():
                if self.dockwidget.lineEdit_2.text()!='':
                    self.dockwidget.listWidget.addItem(self.dockwidget.lineEdit_2.text())
                    dictionary[self.dockwidget.lineEdit_2.text()]=[]
                    with open(os.path.dirname(os.path.abspath(__file__))+'\\dictionary.json', "w", encoding = 'utf-8') as write_file:
                        json.dump(dictionary, write_file, ensure_ascii=False)

            self.dockwidget.pushButton_6.clicked.connect(createItem_2)



            def openFile():
                dir = QtWidgets.QFileDialog.getOpenFileName()[0]
                self.dockwidget.label_3.setText(dir)
                #print(self.dockwidget.label_3.text())

            self.dockwidget.pushButton.clicked.connect(openFile)

            def start():
                if self.dockwidget.label_3.text()!="":

                    path = str(self.dockwidget.label_3.text())
                    dir = QtWidgets.QFileDialog.getSaveFileName()[0]
                    df = pd.read_csv(path, index_col=False, sep=";", low_memory=False,nrows=1000)
                    # массив в котором будут храниться значения нового столбца
                    Class = []

                    # перебираем построчно датасет
                    for i, row in enumerate(df.itertuples(), 1):
                        X = []  # сюда запишем значения найденных ключей
                        Y = []  # а сюда позиции найденных слов
                        # Проходимся по ключам и их значениям
                        for key, words in dictionary.items():
                            # Проходимся по значениям. Там массив, поэтому нужно проверить каждое
                            for word in words:
                                search_exemple = re.search(word, str(row), re.I)  # поиск слова без учёта регистра
                                # если находим, то в массив X добавляем название ключа, а в Y позицию найденного слова
                                if search_exemple:
                                    X.append(key)
                                    Y.append(search_exemple.start())
                                    # Если массив Y не пуст, то находим элемент, который находится раньше, добавляем в массив классов значение X с тем же номером
                        # Т.е. если в Y минимальное значение имеет, например, индекс 3, то мы добавляем в класс X с таким же индексом
                        if Y != []:
                            position = Y.index(min(Y))
                            Class.append(X[position])
                        # Ну а если массив Y пустой, то пишем None.
                        else:
                            Class.append("None")

                        #print(i, position + 1, X, Y)




                    df['Класс'] = Class  # добавляем столбец в датасет

                    df.to_csv(dir+r".shp", index=False, sep=";")  # сохраняем его

            self.dockwidget.pushButton_4.clicked.connect(start)

