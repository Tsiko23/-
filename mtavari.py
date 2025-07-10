import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QTableWidget,
    QTableWidgetItem, QMessageBox, QDateEdit, QFileDialog, QInputDialog
)
from PyQt5.QtCore import QDate, Qt
from db import (
    create_table, add_member, get_all_members,
    update_days_left, delete_member
)
import matplotlib.pyplot as plt


class GymApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gym Membership Management")
        self.setGeometry(300, 100, 1000, 650)

        self.subscriptions = {
            "Silver": (80, 12),
            "Gold": (100, 18),
            "Platinum": (150, 30)
        }

        self.member_ids = []
        self.init_ui()
        self.apply_styles()
        create_table()
        self.load_members()
        self.update_revenue_label()
        self.update_end_date()

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f2f5;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 12pt;
            }
            QLineEdit, QComboBox, QDateEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover:!disabled {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #a5d6a7;
                color: #eee;
            }
            QTableWidget {
                background-color: white;
                gridline-color: #ddd;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 4px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
        """)

    def init_ui(self):
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("სახელი და გვარი")

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("ID ნომერი")

        self.subscription_combo = QComboBox()
        self.subscription_combo.addItems(self.subscriptions.keys())
        self.subscription_combo.currentIndexChanged.connect(self.update_end_date)

        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.dateChanged.connect(self.update_end_date)

        self.end_label = QLabel("აბონემენტის დასრულება: -")

        self.add_button = QPushButton("➕ დამატება")
        self.add_button.clicked.connect(self.add_member)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 მოძებნე სახელი")
        self.search_input.textChanged.connect(self.search_member)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "სახელი", "ID ნომერი", "აბონემენტი",
            "ფასი", "თარიღი", "დარჩენილი დღე"
        ])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.selectionModel().selectionChanged.connect(self.on_selection_changed)

        self.checkin_button = QPushButton("Check-in")
        self.checkin_button.clicked.connect(self.check_in)
        self.checkin_button.setEnabled(False)

        self.delete_button = QPushButton("წაშლა")
        self.delete_button.clicked.connect(self.delete_member)
        self.delete_button.setEnabled(False)

        self.refresh_button = QPushButton("განახლება")
        self.refresh_button.clicked.connect(self.load_members)

        self.extend_button = QPushButton("გახანგრძლივება")
        self.extend_button.clicked.connect(self.extend_membership_custom)
        self.extend_button.setEnabled(False)

        self.stats_button = QPushButton("სტატისტიკა")
        self.stats_button.clicked.connect(self.show_stats)

        self.revenue_label = QLabel("მთლიანი შემოსავალი: 0 ლარი")
        self.member_count_label = QLabel("წევრების რაოდენობა: 0")

        input_layout = QHBoxLayout()
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.id_input)
        input_layout.addWidget(self.subscription_combo)
        input_layout.addWidget(self.date_input)
        input_layout.addWidget(self.add_button)

        options_layout = QHBoxLayout()
        options_layout.addWidget(self.end_label)
        options_layout.addWidget(self.search_input)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.checkin_button)
        buttons_layout.addWidget(self.extend_button)
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.refresh_button)
        buttons_layout.addWidget(self.stats_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(input_layout)
        main_layout.addLayout(options_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addWidget(self.table)
        main_layout.addWidget(self.revenue_label)
        main_layout.addWidget(self.member_count_label)

        self.setLayout(main_layout)

    def on_selection_changed(self):
        has_selection = bool(self.table.selectedItems())
        self.checkin_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
        self.extend_button.setEnabled(has_selection)

    def update_end_date(self):
        sub_type = self.subscription_combo.currentText()
        days = self.subscriptions[sub_type][1]
        start = self.date_input.date()
        end = start.addDays(days)
        self.end_label.setText(f"დღევანდელი აბონემენტი დასრულდება: {end.toString('yyyy-MM-dd')}")

    def add_member(self):
        name = self.name_input.text().strip()
        id_number = self.id_input.text().strip()
        subscription = self.subscription_combo.currentText()
        price, days = self.subscriptions[subscription]
        start_date = self.date_input.date().toString("yyyy-MM-dd")

        if not name or not id_number:
            QMessageBox.warning(self, "გთხოვთ შეავსოთ", "ყველა ველი სავალდებულოა!")
            return

        if any(m[2] == id_number for m in get_all_members()):
            QMessageBox.warning(self, "დუბლიკატი", "ასეთი ID უკვე არსებობს!")
            return

        try:
            add_member(name, id_number, subscription, price, start_date, days)
            self.name_input.clear()
            self.id_input.clear()
            self.load_members()
            self.update_revenue_label()
        except Exception as e:
            QMessageBox.critical(self, "შეცდომა", str(e))

    def load_members(self):
        self.table.setRowCount(0)
        self.member_ids.clear()

        members = [m for m in get_all_members() if m[6] > 0]

        for row, m in enumerate(members):
            self.member_ids.append(m[0])
            self.table.insertRow(row)
            for col, val in enumerate(m[1:]):
                item = QTableWidgetItem(str(val))
                self.table.setItem(row, col, item)

        self.member_count_label.setText(f"წევრების რაოდენობა: {len(members)}")
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)

    def search_member(self):
        text = self.search_input.text().lower()
        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text().lower()
            id_number = self.table.item(row, 1).text().lower()
            visible = text in name or text in id_number
            self.table.setRowHidden(row, not visible)

    def update_revenue_label(self):
        members = get_all_members()
        total = sum(m[4] for m in members)
        self.revenue_label.setText(f"მთლიანი შემოსავალი: {total:.2f} ლარი")

    def check_in(self):
        row = self.table.currentRow()
        if row < 0: return
        member_id = self.member_ids[row]
        days_left = int(self.table.item(row, 5).text())
        if days_left <= 0:
            QMessageBox.information(self, "შეწყდა", "ვადა ამოწურულია.")
            return
        update_days_left(member_id, days_left - 1)
        self.load_members()

    def extend_membership_custom(self):
        row = self.table.currentRow()
        if row < 0: return
        options = {
            "Silver (12 დღე)": 12,
            "Gold (18 დღე)": 18,
            "Platinum (30 დღე)": 30
        }
        item, ok = QInputDialog.getItem(self, "აირჩიე პაკეტი", "რამდენი დღით გსურს?", list(options.keys()), 0, False)
        if ok and item:
            days = options[item]
            member_id = self.member_ids[row]
            current_days = int(self.table.item(row, 5).text())
            update_days_left(member_id, current_days + days)
            QMessageBox.information(self, "დასრულდა", f"დაემატა {days} დღე.")
            self.load_members()

    def delete_member(self):
        row = self.table.currentRow()
        if row < 0: return
        member_id = self.member_ids[row]
        reply = QMessageBox.question(self, "წაშლა", "დარწმუნებული ხართ?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            delete_member(member_id)
            self.load_members()
            self.update_revenue_label()

    def show_stats(self):
        members = get_all_members()
        data = {"Silver": 0, "Gold": 0, "Platinum": 0}
        for m in members:
            data[m[3]] += 1
        labels, sizes = list(data.keys()), list(data.values())
        colors = ['#c0c0c0', '#ffd700', '#e5e4e2']
        fig, ax = plt.subplots()
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.axis('equal')
        plt.title("აბონემენტების ტიპები")
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GymApp()
    window.show()
    sys.exit(app.exec_())
