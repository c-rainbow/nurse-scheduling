
import tkinter as tk

from shiftscheduler.gui import util


class UpperFrame(tk.Frame):

    def __init__(self, master, lower_frame, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self._lower_frame = lower_frame

        # Configure layouts
        util.SetGridWeights(self, column_weights=(1, 2, 2, 2, 1))
        self.CreateBareboneExcelButton(1)
        self.CreateNewScheduleButton(2)
        self.CreateUpdateScheduleButton(3)

    def CreateBareboneExcelButton(self, col_index):
        frame = tk.Frame(self)
        util.SetGrid(frame, 0, col_index)

        button_label = tk.Button(
            frame, text='기본 엑셀 파일 받기', command=self._lower_frame.ShowBareboneFrame)
        button_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def CreateNewScheduleButton(self, col_index):
        frame = tk.Frame(self)
        util.SetGrid(frame, 0, col_index)

        button_label = tk.Button(
            frame, text='새 일정 넣기', command=self._lower_frame.ShowNewScheduleFrame)
        button_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def CreateUpdateScheduleButton(self, col_index):
        frame = tk.Frame(self)
        util.SetGrid(frame, 0, col_index)

        button_label = tk.Button(
            frame, text='기존 일정 수정하기', command=self._lower_frame.ShowUpdateScheduleFrame)
        button_label.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)