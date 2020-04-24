
import os
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter import scrolledtext
from tkinter import ttk

import tkcalendar as tkc

from shiftscheduler.excel import input as excel_input
from shiftscheduler.excel import output as excel_output
from shiftscheduler.gui import util
from shiftscheduler.i18n import gettext
from shiftscheduler.solver import input as solver_input
from shiftscheduler.solver import output as solver_output
from shiftscheduler.validation import validator


_ = gettext.GetTextFn('gui/update_schedule')
DATE_PATTERN = _('y/m/d')
LOCALE_CODE = gettext.GetLanguageCode()


class UpdateScheduleFrame(ttk.Frame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        util.SetGridWeights(self, column_weights=(1, 2))

        self.open_filename_strv = tk.StringVar(value='')
        self.start_date_cal = None  # To be assigned when DateEntry is created
        self.end_date_cal = None  # To be assigned when DateEntry is created
        self.keep_offdate_var = tk.BooleanVar()
        self.max_time_var = tk.IntVar()

        self.createLeftFrame()
        self.createRightFrame()

    def createLeftFrame(self):
        left_frame = ttk.Frame(self)
        util.SetGrid(left_frame, 0, 0)
        util.SetGridWeights(left_frame, row_weights=(1, 1, 1, 1, 1, 1, 1, 1, 2, 1))

        # Open modified schedule
        open_file_button = ttk.Button(left_frame, text=_('파일 불러오기'), command=self.openExcelToUpdate)
        util.SetGrid(open_file_button, 0, 0)
        open_file_label = ttk.Label(left_frame, textvariable=self.open_filename_strv)
        util.SetGrid(open_file_label, 1, 0)

        # Select date range to update
        start_date_label = ttk.Label(left_frame, text=_('수정 시작 날짜'))
        util.SetGrid(start_date_label, 2, 0)
        self.start_date_cal = tkc.DateEntry(
            left_frame, year=2020, month=5, day=1, date_pattern=DATE_PATTERN, locale=LOCALE_CODE)
        util.SetGrid(self.start_date_cal, 3, 0)
        # End date to update
        end_date_label = ttk.Label(left_frame, text=_('수정 끝 날짜'))
        util.SetGrid(end_date_label, 4, 0)
        self.end_date_cal = tkc.DateEntry(
            left_frame, year=2020, month=5, day=31, date_pattern=DATE_PATTERN, locale=LOCALE_CODE)
        util.SetGrid(self.end_date_cal, 5, 0)

        # Checkbox to keep the off dates
        keep_offdate_checkbox = ttk.Checkbutton(
            left_frame, text=_('기존의 오프날짜 유지'), variable=self.keep_offdate_var,
            onvalue=True, offvalue=False)
        util.SetGrid(keep_offdate_checkbox, 6, 0)

        # Max search time frame
        max_time_frame = ttk.Frame(left_frame)
        util.SetGrid(max_time_frame, 7, 0)
        util.SetGridWeights(max_time_frame, column_weights=(4, 1, 1))
        
        max_time_label1 = ttk.Label(max_time_frame, text=_('최대 검색 시간'))
        util.SetGrid(max_time_label1, 0, 0)

        self.max_time_var.set(1)
        max_time_spinbox = ttk.Spinbox(max_time_frame, from_=1, to=30, textvariable=self.max_time_var)
        util.SetGrid(max_time_spinbox, 0, 1)

        max_time_label2 = ttk.Label(max_time_frame, text=_('분'))
        util.SetGrid(max_time_label2, 0, 2)

        max_time_info_label = ttk.Label(left_frame, text=_('시간 내로 조건에 맞는 일정을 찾을 수 없을 시\n작업을 중지합니다'))
        util.SetGrid(max_time_info_label, 8, 0)

        # Start button
        submit_button = ttk.Button(left_frame, text=_('시작'), command=self.updateSchedule)
        util.SetGrid(submit_button, 9, 0)

    def createRightFrame(self):
        # Right side only displays status of validation and solver run
        right_frame = ttk.Frame(self)
        util.SetGrid(right_frame, 0, 1)
        util.SetGridWeights(right_frame, row_weights=(1, 9))

        label = ttk.Label(right_frame, text=_('진행상황'))
        util.SetGrid(label, 0, 0)
        self.status_text_area = scrolledtext.ScrolledText(right_frame, state=tk.DISABLED)
        util.SetGrid(self.status_text_area, 1, 0)
        

    def clearFields(self):
        self.open_filename_strv.set('')

        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.delete(1.0, tk.END)
        self.status_text_area.configure(state=tk.DISABLED)

    def updateLabels(self, filepath, start_date, end_date):
        self.clearFields()
        filename = os.path.basename(filepath)
        self.open_filename_strv.set(_('선택한 파일: {filename}') % filename)

    def addToTextArea(self, text_to_add):
        self.status_text_area.configure(state=tk.NORMAL)
        self.status_text_area.insert(tk.END, text_to_add)
        self.status_text_area.configure(state=tk.DISABLED)

    def updateSchedule(self):
        update_start_date = self.start_date_cal.get_date()
        update_end_date = self.end_date_cal.get_date()
        keep_offdates = self.keep_offdate_var.get()

        if update_start_date > update_end_date:
            self.addToTextArea(_('수정 시작 날짜가 끝 날짜 이후입니다\n'))
            return

        excel_start_date = self.base_schedule.software_config.start_date        
        excel_end_date = self.base_schedule.software_config.end_date        
        if update_start_date < excel_start_date:
            self.addToTextArea(_('수정 시작 날짜가 일정표 시작 날짜 이전입니다\n'))
            return
        if excel_end_date < update_end_date:
            self.addToTextArea(_('수정 끝 날짜가 일정표 끝 날짜 이후입니다\n'))
            return

        solver, var_dict = solver_input.FromTotalSchedule(
            self.base_schedule, exclude_start=update_start_date, exclude_end=update_end_date,
            keep_offdates=keep_offdates)
        self.addToTextArea(_('solve 시작\n'))
        
        max_time_ms = self.max_time_var.get() * 60 * 1000
        solver.set_time_limit(max_time_ms)
        status = solver.Solve()
        self.addToTextArea(_('solve 끝. 결과: {status}\n') % status)

        if status == solver.INFEASIBLE:
            messagebox.showerror(message=_('가능한 일정이 없습니다. 조건을 변경해 주세요'))
            return
        else:
            messagebox.showinfo(message=_('일정을 완성하였습니다. 저장할 파일 경로를 설정해 주세요'))

        new_schedule = solver_output.ToTotalSchedule(
            base_schedule.software_config, base_schedule.person_configs, base_schedule.date_configs,
            var_dict)

        errors = validator.ValidateTotalScheduleFormat(new_schedule, barebone=False)
        if errors:
            self.addToTextArea('\n'.join(errors))
            return
    
        # Save to Excel file
        filepath = filedialog.asksaveasfilename(title=_('완성된 엑셀 파일 저장하기'))
        if filepath:
            excel_output.FromTotalSchedule(new_schedule, filepath)

    def openExcelToUpdate(self):
        filepath = filedialog.askopenfilename(title=_('수정할 엑셀 파일 열기'))
        if not filepath:
            return

        self.base_schedule = excel_input.ReadFromExcelFile(filepath)

        # Update labels
        start_date = self.base_schedule.software_config.start_date
        end_date = self.base_schedule.software_config.end_date
        self.updateLabels(filepath, start_date, end_date)

        # Validate
        errors = validator.ValidateTotalScheduleFormat(self.base_schedule, barebone=True)
        
        if errors:
            self.addToTextArea('\n'.join(errors))
        else:
            self.addToTextArea(_('오류가 없습니다. "시작" 버튼을 눌러주세요\n'))
