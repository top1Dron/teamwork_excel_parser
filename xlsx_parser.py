from datetime import datetime
from io import StringIO, BytesIO
from itertools import groupby
from pprint import pprint

import pandas
from pandas import ExcelFile


class TeamworkExcelParser:

    task_link = "https://avada.teamwork.com/#/tasks/"

    def __init__(self, file, response_file_name):
        self.file = file
        self.response_file_name = response_file_name
        self.output_data = []
        self.first_part_data = []
        self.second_part_data = []

    def highlight_value(self, s):
        is_value = s == 'До 15 числа'
        return ['font-weight: bold' if v else '' for v in is_value]
        

    def get_valid_format(self):
        # Читаем содержимое файла
        contents = self.file.read()

        # Используем BytesIO для создания потокового объекта из байтов
        df = pandas.read_excel(BytesIO(contents))

        # Продолжаем обработку данных
        self._group_tasks(df.to_dict(orient="records"))
        new_excel_data = pandas.DataFrame.from_records(self.output_data)

        output = BytesIO()
        writer = pandas.ExcelWriter(output, engine='xlsxwriter')

        styler = new_excel_data.style
        styler.apply(lambda x: ['font-weight: bold' if v == 'До 15 числа' and i == 'description' else '' for i, v in
                                zip(x.index, x)], axis=1)

        new_excel_data.to_excel(writer, sheet_name='sheetName', index=False, na_rep='NaN', header=True)

        for column in new_excel_data:
            column_length = max(new_excel_data[column].astype(str).map(len).max(), len(column))
            col_idx = new_excel_data.columns.get_loc(column)
            writer.sheets['sheetName'].set_column(col_idx, col_idx, min(column_length, 50))

        writer.close()
        output.seek(0)  # Сбрасываем указатель в начало файла
        return output

    @staticmethod
    def __key_func(k):
        return k['Task ID']

    def _group_tasks(self, data):
        # sort INFO data by 'company' key.
        data = sorted(data, key=self.__key_func)
        first_part_data = [log for log in data if datetime.strptime(log["Date"], "%m/%d/%Y").day <= 15]
        second_part_data = [log for log in data if datetime.strptime(log["Date"], "%m/%d/%Y").day > 15]

        for key, value in groupby(data, self.__key_func):
            value = list(value)
            self.output_data.append(self.get_new_row(value))
                
        for key, value in groupby(first_part_data, self.__key_func):
            value = list(value)
            self.first_part_data.append(self.get_new_row(value))
            
        for key, value in groupby(second_part_data, self.__key_func):
            value = list(value)
            self.second_part_data.append(self.get_new_row(value))

        print(self.output_data)
        print(len(self.output_data))
        self.output_data = sorted(self.output_data, key=lambda log: log["project"])
        self.first_part_data = sorted(self.first_part_data, key=lambda log: log["project"])
        self.second_part_data = sorted(self.second_part_data, key=lambda log: log["project"])
        
        hours = round(sum([log["hours"] for log in self.output_data]), 2)
        self.output_data.append(dict(project="", task_link="", description="", 
                                     hours=hours, estimated_hours="", parent_task_with_task=""))
        self.output_data.append(dict(project="", task_link="", description="",
                                     hours="", estimated_hours="", parent_task_with_task=""))
        self.output_data.append(dict(project="", task_link="", description="До 15 числа",
                                     hours="", estimated_hours="", parent_task_with_task=""))
        
        self.output_data.extend(self.first_part_data)
        hours = round(sum([log["hours"] for log in self.first_part_data]), 2)
        self.output_data.append(dict(project="", task_link="", description="",
                                     hours=hours, estimated_hours="", parent_task_with_task=""))
        self.output_data.append(dict(project="", task_link="", description="",
                                     hours="", estimated_hours="", parent_task_with_task=""))
        self.output_data.append(dict(project="", task_link="", description="После 15 числа",
                                     hours="", estimated_hours="", parent_task_with_task=""))
        self.output_data.extend(self.second_part_data)
        hours = round(sum([log["hours"] for log in self.second_part_data]), 2)
        self.output_data.append(dict(project="", task_link="", description="", hours=hours, estimated_hours=""))

    def get_new_row(self, group_rows):
        new_row = {}
        for group_row in group_rows:
            new_row["project"] = group_row["Project"]
            new_row["task_link"] = self.task_link + str(group_row["Task ID"])
            new_row["description"] = group_row["Task"]
            new_row["parent_task_with_task"] = f"{group_row['Parent task']} - {group_row['Task']}"
            new_row["parent_task"] = group_row["Parent task"]
            if not new_row.get('hours'):
                new_row["hours"] = float(group_row["Decimal hours"])
            else:
                new_row["hours"] += float(group_row["Decimal hours"])
            new_row["estimated_hours"] = round(float(group_row["Estimated time"])/60, 2) if group_row["Estimated time"] else ""
        new_row["hours"] = round(new_row["hours"], 2)
        return new_row
        
    def get_new_row_by_time(self, group_rows, first_part: bool = True):
            new_row = {}
            for group_row in group_rows:
                date_of_log = group_row["Date"].day
                if (first_part and date_of_log <= 15) or (not first_part and date_of_log > 15):
                    new_row["project"] = group_row["Project"]
                    new_row["task_link"] = self.task_link + str(group_row["Task ID"])
                    new_row["description"] = group_row["Task"]
                    if not new_row.get('hours'):
                        new_row["hours"] = float(group_row["Decimal Hours"])
                    else:
                        new_row["hours"] += float(group_row["Decimal Hours"])
                    new_row["estimated_hours"] = round(float(group_row["Estimated time"])/60, 2) if group_row["Estimated time"] else ""
            new_row["hours"] = round(new_row["hours"], 2)
            return new_row if new_row != {} else None
