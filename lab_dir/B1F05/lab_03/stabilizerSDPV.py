# stabilizerSDPV.py
from array import array
import numpy as np
import math
from scipy.integrate import solve_ivp


class StepDownPulseVoltageStabilizer:
    """ Класс описывающий работу схемы понижающего импульсного стабилизатора """

    def_param = {
        "def_U_in": 12.0,  # Входное напряжение (В)
        "def_U_out": 9.0,  # Выходное напряжение (В)
        "def_delta_U_out": 0.05,  # Размах пульсаций выходного напряжения
        "def_I_n": 1.0,  # Ток нагрузки (А)
        "def_LIR": 0.2,  # Коэффициент тока дросселя
        "def_F": 10000,  # Частота импульсов (Гц)
        "def_t_sim": 0.005,  # Время моделирования (с)
        "def_D_min": 0.1,  # Минимальный коэффициент заполнения
        "def_D_max": 0.98,  # Максимальный коэффициент заполнения
    }

    # Перечень методов интегрирования
    integration_methods = ["Eiler", "RK45", "BDF", "Radau"]

    # Исходные параметры схемы
    U_in = def_param["def_U_in"]  # Входное напряжение (В)
    U_out = def_param["def_U_out"]  # Выходное напряжение (В)
    delta_U_out = def_param["def_delta_U_out"]  # Размах пульсаций выходного напряжения
    I_n = def_param["def_I_n"]  # Ток нагрузки (А)
    LIR = def_param["def_LIR"]  # Коэффициент тока дросселя
    F = def_param["def_F"]  # Частота импульсов (Гц)
    D_min = def_param["def_D_min"]  # Минимальный коэффициент заполнения
    D_max = def_param["def_D_max"]  # Максимальный коэффициент заполнения

    # Паразитные параметры
    U_CE_sat = 0.2  # Падение на транзисторе
    U_D_drop = 0.7  # Падение на диоде

    # Расчетные параметры
    L = 0.0  # Индуктивность (Гн)
    C = 0.0  # Емкость (Ф)
    R = 0.0  # Сопротивление нагрузки (Ом)
    delta_I_L_actual = 0.0  # фактическое значение пульсации тока через индуктивность
    delta_U_out_actual = 0.0  # фактическое значение пульсаций выходного напряжения
    t_i = 0.0  # Время импульса
    t_p = 0.0  # Время интервала
    T = 0.0  # Период переключения управляющего сигнала (с)

    # Параметры моделирования
    integration_method = "Eiler"
    t_sim = def_param["def_t_sim"]  # Время моделирования (с)
    t = array('f')  # Временная ось

    # Параметры визуализации
    t_start = 0.0  # начальное время отображения (с)
    t_stop = t_sim  # конечное время отображения (с)

    # Начальные условия
    I_L = 0.0  # Начальный ток через катушку (А)
    U_C = 0.0  # Начальное напряжение на конденсаторе (В)
    U_CE = U_in  # Начальное напряжение коллектор-эмиттер (В)
    U_D = 0.0  # Начальное напряжение на диоде (В)
    I_in = 0.0  # Начальный входной ток (А)
    I_D = 0.0  # Начальный ток через диод (А)

    # Массивы для хранения результатов
    I_L_arr = array('f')
    U_C_arr = array('f')
    U_CE_arr = array('f')
    U_D_arr = array('f')
    I_in_arr = array('f')
    I_D_arr = array('f')

    def __init__(self):
        self.calc_param()
        self.clear_arr()
        self.modeling()

    def clear_arr(self):
        """ Сброс начальных условий переходных процессов схемы
        и очистка массивов хранения результатов """

        self.I_L = 0.0
        self.U_C = 0.0
        self.U_CE = self.U_in
        self.U_D = 0.0
        self.I_in = 0.0
        self.I_D = 0.0

        self.I_L_arr = array('f')
        self.U_C_arr = array('f')
        self.U_CE_arr = array('f')
        self.U_D_arr = array('f')
        self.I_in_arr = array('f')
        self.I_D_arr = array('f')
        self.t = array('f')

    def set_default_param(self):
        # Исходные параметры схемы
        self.U_in = self.def_param["def_U_in"]  # Входное напряжение (В)
        self.D_min = self.def_param["def_D_min"]  # Минимальный коэффициент заполнения
        self.D_max = self.def_param["def_D_max"]  # Максимальный коэффициент заполнения
        self.U_out = self.def_param["def_U_out"]  # Выходное напряжение (В)
        self.delta_U_out = self.def_param["def_delta_U_out"]  # Размах пульсаций выходного напряжения
        self.I_n = self.def_param["def_I_n"]  # Ток нагрузки (А)
        self.F = self.def_param["def_F"]  # Частота импульсов (Гц)
        self.LIR = self.def_param["def_LIR"]  # Коэффициент тока дросселя

        # Расчетные параметры
        self.calc_param()

        # Параметры моделирования
        # self.t_sim = self.def_param["def_t_sim"]  # Время моделирования (с)

        # Параметры визуализации
        self.t_start = 0.0  # начальное время отображения (с)
        self.t_stop = self.t_sim  # конечное время отображения (с)

    def calc_param(self):
        # Определяем расчетные параметры генератора сигналов переключения управляющего
        # транзистора. C учетом падения напряжения на открытом транзисторе U_ce_nas
        # и диоде U_d найдем соотношение t_i/t_p = k
        k = (self.U_out + self.U_D_drop) / (self.U_in - self.U_CE_sat - self.U_out)
        self.T = 1 / self.F
        self.t_i = (self.T * k) / (k + 1)
        self.t_p = self.T / (k + 1)

        # Определяем номинальное сопротивление нагрузки
        self.R = self.U_out / self.I_n

        # Выберем значение коэффициента тока дросселя LIR = 0.3
        # и определим величину индуктивности
        # self.L = (1 - self.U_out / self.U_in) * (self.U_out * self.T / (self.LIR * self.I_n))
        self.L = self.t_i * (self.U_in - self.U_CE_sat - self.U_out) / (self.LIR * self.I_n)

        # Рассчитаем пульсации тока через индуктивность
        D = self.U_out / (self.U_in - self.U_CE_sat)
        self.delta_I_L_actual = (self.U_in - self.U_CE_sat - self.U_out) * D / (self.L * self.F)

        # Расчет емкости на основе заданных пульсаций
        self.C = self.delta_I_L_actual / (8 * self.delta_U_out * self.F)

        # Найдем величину выходной емкости
        # self.C = (1 / 8 * self.T / self.delta_U_out) * self.LIR
        # self.C = self.LIR * self.I_n * self.t_i / (4 * self.U_out * self.delta_U_out)

    def system_of_equations(self, t, y):
        """ Система дифференциальных уравнений для понижающего стабилизатора """
        I_L, U_C = y  # Ток через индуктивность и напряжение на конденсаторе

        # Определение состояния ключа (включен/выключен)
        if (t % self.T) < self.t_i:
            # Ключ включен
            dI_L_dt = (self.U_in - self.U_CE_sat - U_C) / self.L
            dU_C_dt = (I_L - U_C / self.R) / self.C
        else:
            # Ключ выключен
            dI_L_dt = (-U_C - self.U_D_drop) / self.L
            dU_C_dt = (I_L - U_C / self.R) / self.C
        return [dI_L_dt, dU_C_dt]

    def calc_U_I_on_elements(self, t):
        for i in range(len(t)):
            # Определение состояния ключа (включен/выключен)
            if (t[i] % self.T) < self.t_i:
                # Ключ включен
                self.U_CE = self.U_CE_sat  # Напряжение коллектор-эмиттер равно падению на транзисторе
                self.U_D = self.U_in - self.U_CE_sat  # Напряжение на диоде
                self.I_in = self.I_L  # Входной ток равен току через катушку
                self.I_D = 0.0  # Ток через диод равен нулю
            else:
                # Ключ выключен
                self.U_CE = self.U_in  # Напряжение коллектор-эмиттер равно входному напряжению
                self.U_D = self.U_D_drop  # Напряжение на диоде равно падению на диоде
                self.I_in = 0.0  # Входной ток равен нулю
                self.I_D = self.I_L  # Ток через диод равен току через катушку

            self.U_CE_arr.append(self.U_CE)
            self.U_D_arr.append(self.U_D)
            self.I_in_arr.append(self.I_in)
            self.I_D_arr.append(self.I_D)

    def modeling(self):
        """ Расчет параметров схемы понижающего импульсного стабилизатора """

        # Расчет временных параметров
        self.T = self.t_i + self.t_p  # Период переключения (с)
        dt = self.T / 1000  # Шаг по времени (с)
        t = np.arange(0, self.t_sim, dt)  # Временная ось

        self.t = array('f', t)

        # Моделирование переходных процессов в схеме
        if self.integration_method in ["RK45", "BDF", "Radau"]:
            # Начальные условия
            y0 = [self.I_L, self.U_C]
            # Решение системы дифференциальных уравнений
            sol = solve_ivp(self.system_of_equations, [0, self.t_sim], y0,
                            t_eval=t, method=self.integration_method)

            # Сохранение результатов
            self.t = array('f', sol.t)
            self.I_L_arr = array('f', sol.y[0])
            self.U_C_arr = array('f', sol.y[1])

            self.calc_U_I_on_elements(self.t)

        else:
            # Интегрирование (метод Эйлера)
            for i in range(len(t)):
                y_prev = [self.I_L, self.U_C]
                y = self.system_of_equations(t[i], y_prev)
                dI_L_dt, dU_C_dt = y

                self.I_L += dI_L_dt * dt
                self.U_C += dU_C_dt * dt

                # Сохранение результатов
                self.I_L_arr.append(self.I_L)
                self.U_C_arr.append(self.U_C)

            self.calc_U_I_on_elements(self.t)

    def check_ripples(self):
        # Расчет коэффициента заполнения
        D = self.U_out / (self.U_in - self.U_CE_sat)

        # Расчет пульсаций тока через индуктивность
        delta_I_L = (self.U_in - self.U_CE_sat - self.U_out) * D / (self.L * self.F)

        # Расчет фактических пульсаций выходного напряжения
        delta_U_out = delta_I_L / (8 * self.C * self.F)

        # Частота среза LC-фильтра
        f_c = 1 / (2 * math.pi * math.sqrt(self.L * self.C))

        return delta_I_L, delta_U_out, f_c

    def get_index(self, time_start: float):
        settling_index = np.where(np.array(self.t) >= time_start)[0][0]
        return settling_index

    def get_settling_time(self):
        # Поиск времени завершения переходных процессов
        settling_threshold = 0.2  # Допуск 2%
        settling_index = np.where(np.abs(np.array(self.U_C_arr) - self.U_out) / self.U_out < settling_threshold)[0][0]
        return self.t[settling_index]

    def get_settling_time_1(self):
        # Поиск времени завершения переходных процессов
        settling_threshold = 0.02  # Допуск 2%
        settling_index = np.where(np.abs(np.array(self.U_C_arr) - self.U_out) / self.U_out < settling_threshold)[0][0]
        return settling_index * self.T / 1000

    def get_settling_time_2(self):
        # Коэффициент затухания
        sigma = (self.R / 2) * (math.sqrt(self.C / self.L))
        # Собственная частота
        omega_n = 1 / math.sqrt(self.L * self.C)
        # Время установления
        t_s = 3 / (sigma * omega_n)
        return t_s

    def get_settling_time_3(self):
        omega_n = math.sqrt(abs((1 / self.L * self.C) - (self.R / (2 * self.L)) ** 2))
        return 5 / omega_n

    def min_value_U_out(self):
        return self.D_min * (self.U_in - self.U_CE_sat) - (1 - self.D_min) * self.U_D_drop

    def max_value_U_out(self):
        return self.D_max * (self.U_in - self.U_CE_sat) - (1 - self.D_max) * self.U_D_drop
