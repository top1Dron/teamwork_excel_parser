from io import StringIO
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

    def get_valid_format(self):
        # excel_file =ExcelFile(self.file.file)
        df = pandas.read_excel(self.file.file)
        print(df.tail())
        self._group_tasks(df.to_dict(orient="records"))
        new_excel_data = pandas.DataFrame.from_records(self.output_data)
        new_excel_data.to_excel(self.response_file_name, index=False, header=True)

    @staticmethod
    def __key_func(k):
        return k['Task Id']

    def _group_tasks(self, data):
        # sort INFO data by 'company' key.
        data = sorted(data, key=self.__key_func)

        for key, value in groupby(data, self.__key_func):
            self.output_data.append(self.get_new_row(list(value)))
        print(self.output_data)
        print(len(self.output_data))

    def get_new_row(self, group_rows):
        new_row = {}
        for group_row in group_rows:
            new_row["project"] = group_row["Project"]
            new_row["task_link"] = self.task_link + str(group_row["Task Id"])
            new_row["description"] = group_row["Task"]
            if not new_row.get('hours'):
                new_row["hours"] = float(group_row["Decimal Hours"])
            else:
                new_row["hours"] += float(group_row["Decimal Hours"])
            new_row["estimated_hours"] = float(group_row["Estimated"])/60 if group_row["Estimated"] else ""
        return new_row




    #     output_data = {}
    #     for row in data:
    #         if output_data.get(row["Task Id"]):
    #             output_data[row['Task Id']] += float(row["Decimal Hours"])
    #         else:
    #             output_data[row['Task Id']] = float(row["Decimal Hours"])
    #         output_data[row["Task Id"]] = self._get_row_data(row, )
    #     print(output_data)
    #
    # def _get_row_data(self, row):
    #     new_row = {row[''], self.task_link + row['Task Id'], )
