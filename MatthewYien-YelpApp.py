#!/usr/bin/env python
import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout
from PyQt5 import uic, QtCore
from PyQt5.QtGui import QIcon, QPixmap
import psycopg2

qt_creator_file = "MatthewYien-YelpApp.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qt_creator_file)


class YelpApp(QMainWindow):
    def __init__(self):
        super(YelpApp, self).__init__()
        self.ui = Ui_MainWindow()

        # GUI Elements - Businesses Page
        self.ui.setupUi(self)
        self.load_state_list()
        self.ui.stateList.currentTextChanged.connect(self.state_changed)
        self.ui.cityList.itemSelectionChanged.connect(self.city_changed)
        self.ui.zipList.itemSelectionChanged.connect(self.zip_changed)
        self.ui.zipList.itemSelectionChanged.connect(self.zipcode_stat)
        self.ui.searchButton.clicked.connect(self.search_button_pressed)
        self.ui.clearButton.clicked.connect(self.clear_button_pressed)
        self.ui.refreshButton.clicked.connect(self.refresh_button_pressed)

    def execute_query(self, query):
        try:
            # Will need to change data to your database
            connection = psycopg2.connect("dbname='yelpdb' user='postgres' host='localhost' password='accessEntry'")
        except:
            print("Unable to connect to the database.")

        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        result = cur.fetchall()
        connection.close()
        return result

    def load_state_list(self):
        self.ui.stateList.clear()
        sql_command = "SELECT distinct state_name FROM business ORDER BY state_name;"
        print(sql_command)
        print("")

        try:
            results = self.execute_query(sql_command)
            print(results)
            print("")

            for row in results:
                self.ui.stateList.addItem(row[0])
        except:
            print("Query failed.")

        self.ui.stateList.setCurrentIndex(-1)
        self.ui.stateList.clearEditText()

    def state_changed(self):
        self.ui.cityList.clear()
        state = self.ui.stateList.currentText()
        if self.ui.stateList.currentIndex() >= 0:
            sql_command = "SELECT distinct city FROM business WHERE state_name = '" + state + "' ORDER BY city;"
            print(sql_command)
            print("")

            try:
                results = self.execute_query(sql_command)
                print(results)
                print("")

                for row in results:
                    self.ui.cityList.addItem(row[0])
            except:
                print("Query failed - state_changed().")

    def city_changed(self):
        self.ui.zipList.clear()
        state = self.ui.stateList.currentText()
        city = self.ui.cityList.selectedItems()[0].text()

        if  (self.ui.stateList.currentIndex() >= 0) and (len(self.ui.cityList.selectedItems()) > 0):
            sql_command = "SELECT distinct zip_code FROM business WHERE state_name = '" + state + "' AND city = '" + city + "' ORDER BY zip_code;"
            print(sql_command)
            print("")

            try:
                results = self.execute_query(sql_command)
                print(results)
                print("")

                for row in results:
                    item = str(row[0])
                    self.ui.zipList.addItem(item)
            except:
                print("Query failed - city_changed().")

    def zip_changed(self):
        self.ui.categoryList.clear()
        self.ui.businessTable.clear()
        zipcode = self.ui.zipList.selectedItems()[0].text()

        if len(self.ui.zipList.selectedItems()) > 0:
            sql_command = "SELECT distinct category_type FROM hascategory, business WHERE zip_code = '" + zipcode + "' AND hascategory.business_id = business.business_id ORDER BY category_type;"
            print(sql_command)
            print("")

            try:
                results = self.execute_query(sql_command)
                print(results)
                print("")

                for row in results:
                    self.ui.categoryList.addItem(row[0])
            except:
                print("Query failed - zip_changed().")

            sql_command2 = "SELECT business_name, address, city, business_avg_star, num_of_checkins, num_of_tips FROM business WHERE zip_code = '" + zipcode + "' ORDER BY business_name;"
            print(sql_command2)
            print("")

            try:
                results2 = self.execute_query(sql_command2)
                print(results2)
                print("")

                style = "::section {""background-color: #e4e1e2; }"
                self.ui.businessTable.horizontalHeader().setStyleSheet(style)
                self.ui.businessTable.setColumnCount(len(results2[0]))
                self.ui.businessTable.setRowCount(len(results2))
                self.ui.businessTable.setHorizontalHeaderLabels(
                    ["Business Name", "Address", "City", "Stars", "Num of Checkins", "Num of Tips"])
                self.ui.businessTable.resizeColumnsToContents()
                self.ui.businessTable.setColumnWidth(0, 275)
                self.ui.businessTable.setColumnWidth(1, 250)
                self.ui.businessTable.setColumnWidth(2, 120)
                self.ui.businessTable.setColumnWidth(3, 60)
                self.ui.businessTable.setColumnWidth(4, 90)
                self.ui.businessTable.setColumnWidth(5, 75)

                current_row_count = 0

                for row in results2:
                    for col_count in range(0, len(results2[0])):
                        self.ui.businessTable.setItem(current_row_count, col_count,
                                                      QTableWidgetItem(str(row[col_count])))

                    current_row_count += 1
            except:
                print("Query failed - business_table_display.")

    def zipcode_stat(self):
        self.ui.numBusinesses.clear()
        self.ui.topCategory.clear()
        zipcode = self.ui.zipList.selectedItems()[0].text()

        if len(self.ui.zipList.selectedItems()) > 0:
            sql_command1 = "SELECT count(*) FROM business WHERE zip_code = '" + zipcode + "'"
            print(sql_command1)
            print("")

            sql_command2 = "SELECT count(*) as num_business, category_type FROM hascategory, business WHERE zip_code = '" + zipcode + "' AND hascategory.business_id = business.business_id GROUP BY category_type ORDER BY num_business DESC;"
            print(sql_command2)
            print("")

            try:
                results1 = self.execute_query(sql_command1)
                print(results1)
                print("")

                self.ui.numBusinesses.addItem(str(results1[0][0]))

            except:
                print("Query failed - zipcode_stat1().")

            try:
                results2 = self.execute_query(sql_command2)
                print(results2)
                print("")

                style = "::section {""background-color: #21bfae; }"
                self.ui.topCategory.horizontalHeader().setStyleSheet(style)
                self.ui.topCategory.setColumnCount(len(results2[0]))
                self.ui.topCategory.setRowCount(len(results2))
                self.ui.topCategory.setHorizontalHeaderLabels(["Num of Businesses", "Category"])
                self.ui.topCategory.resizeColumnsToContents()
                self.ui.topCategory.setColumnWidth(0, 150)
                self.ui.topCategory.setColumnWidth(1, 400)

                current_row_count = 0

                for row in results2:
                    for col_count in range(0, len(results2[0])):
                        self.ui.topCategory.setItem(current_row_count, col_count, QTableWidgetItem(str(row[col_count])))
                    current_row_count += 1
            except:
                print("Query failed - zipcode_stat2().")

    def search_button_pressed(self):
        category = self.ui.categoryList.selectedItems()[0].text()

        if len(self.ui.categoryList.selectedItems()) > 0:
            zipcode = self.ui.zipList.selectedItems()[0].text()

            for i in reversed(range(self.ui.businessTable.rowCount())):
                self.ui.businessTable.removeRow(i)

            sql_command = "SELECT business_name, address, city, business_avg_star, num_of_checkins, num_of_tips FROM hascategory, business WHERE category_type = '" + category + "' AND zip_code = '" + zipcode + "' AND hascategory.business_id = business.business_id ORDER BY business_name;"
            print(sql_command)
            print("")

            try:
                results = self.execute_query(sql_command)
                print(results)
                print("")

                style = "::section {""background-color: #07635E; }"
                self.ui.businessTable.horizontalHeader().setStyleSheet(style)
                self.ui.businessTable.setColumnCount(len(results[0]))
                self.ui.businessTable.setRowCount(len(results))
                self.ui.businessTable.setHorizontalHeaderLabels(
                    ["Business Name", "Address", "City", "Stars", "Num of Checkins", "Num of Tips"])
                self.ui.businessTable.resizeColumnsToContents()
                self.ui.businessTable.setColumnWidth(0, 350)
                self.ui.businessTable.setColumnWidth(1, 250)
                self.ui.businessTable.setColumnWidth(2, 70)
                self.ui.businessTable.setColumnWidth(3, 30)
                self.ui.businessTable.setColumnWidth(4, 100)
                self.ui.businessTable.setColumnWidth(5, 70)

                current_row_count = 0

                for row in results:
                    for col_count in range(0, len(results[0])):
                        self.ui.businessTable.setItem(current_row_count, col_count,
                                                      QTableWidgetItem(str(row[col_count])))

                    current_row_count += 1
            except:
                print("Query failed - search_button_pressed().")

    def clear_button_pressed(self):
        self.ui.businessTable.clear()
        self.ui.businessTable.setColumnCount(0)

    def refresh_button_pressed(self):
        self.ui.popularBusinessesTable.clear()
        category = self.ui.categoryList.selectedItems()[0].text()

        self.ui.popularBusinessesTable.setColumnCount(0)

        if len(self.ui.categoryList.selectedItems()) > 0:
            zipcode = self.ui.zipList.selectedItems()[0].text()

            sql_command = "SELECT businesspopularity.business_name, businesspopularity.num_of_checkins, businesspopularity.num_of_tips, businesspopularity.business_avg_star, popularity_rating FROM businesspopularity, business WHERE category_type = '" + category + "' AND zip_code = '" + zipcode + "' AND businesspopularity.business_id = business.business_id" + " ORDER BY popularity_rating DESC;"
            print(sql_command)
            print("")

            try:
                results = self.execute_query(sql_command)
                print(results)
                print("")

                style = "::section {""background-color: #42ded1; }"
                self.ui.popularBusinessesTable.horizontalHeader().setStyleSheet(style)
                self.ui.popularBusinessesTable.setColumnCount(len(results[0]))
                self.ui.popularBusinessesTable.setRowCount(len(results))
                self.ui.popularBusinessesTable.setHorizontalHeaderLabels(
                    ["Business Name", "Num of Check-ins", "Num of Tips", "Avg_rating", "Popularity Score"])
                self.ui.popularBusinessesTable.resizeColumnsToContents()
                self.ui.popularBusinessesTable.setColumnWidth(0, 400)
                self.ui.popularBusinessesTable.setColumnWidth(1, 150)
                self.ui.popularBusinessesTable.setColumnWidth(2, 150)
                self.ui.popularBusinessesTable.setColumnWidth(3, 150)
                self.ui.popularBusinessesTable.setColumnWidth(4, 200)

                current_row_count = 0

                for row in results:
                    for col_count in range(0, len(results[0])):
                        self.ui.popularBusinessesTable.setItem(current_row_count, col_count, QTableWidgetItem(str(row[col_count])))

                    current_row_count += 1
            except:
                print("Query failed - get_popular_business().")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YelpApp()
    window.show()
    sys.exit(app.exec_())