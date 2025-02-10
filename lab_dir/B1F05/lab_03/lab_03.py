import os

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

from array import array


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
    }

    # Исходные параметры схемы 
    U_in = def_param["def_U_in"]  # Входное напряжение (В)
    U_out = def_param["def_U_out"]  # Выходное напряжение (В)
    delta_U_out = def_param["def_delta_U_out"]  # Размах пульсаций выходного напряжения
    I_n = def_param["def_I_n"]  # Ток нагрузки (А)
    LIR = def_param["def_LIR"]  # Коэффициент тока дросселя
    F = def_param["def_F"]  # Частота импульсов (Гц)

    # Паразитные параметры
    U_CE_sat = 0.2  # Падение на транзисторе
    U_D_drop = 0.7  # Падение на диоде

    # Расчетные параметры
    L = 0.0  # Индуктивность (Гн)
    C = 0.0  # Емкость (Ф)
    R = 0.0  # Сопротивление нагрузки (Ом)
    t_i = 0.0  # Время импульса
    t_p = 0.0  # Время интервала
    T = 0.0  # Период переключения (с)

    # Параметры моделирования
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
    I_L_arr = []
    U_C_arr = []
    U_CE_arr = []
    U_D_arr = []
    I_in_arr = []
    I_D_arr = []

    def __init__(self):
        self.calc_param()
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

        self.I_L_arr.clear()
        self.U_C_arr.clear()
        self.U_CE_arr.clear()
        self.U_D_arr.clear()
        self.I_in_arr.clear()
        self.I_D_arr.clear()
        self.t = array('f')

    def set_default_param(self):
        # Исходные параметры схемы
        self.U_in = self.def_param["def_U_in"]  # Входное напряжение (В)
        self.U_out = self.def_param["def_U_out"]  # Выходное напряжение (В)
        self.delta_U_out = self.def_param["def_delta_U_out"]  # Размах пульсаций выходного напряжения
        self.I_n = self.def_param["def_I_n"]  # Ток нагрузки (А)
        self.F = self.def_param["def_F"]  # Частота импульсов (Гц)
        self.LIR = self.def_param["def_LIR"]  # Коэффициент тока дросселя

        # Расчетные параметры
        self.calc_param()

        # Параметры моделирования
        self.t_sim = 0.002  # Время моделирования (с)

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
        self.L = (1 - self.U_out / self.U_in) * (self.U_out * self.T / (self.LIR * self.I_n))

        # Найдем величину выходной емкости
        self.C = (1 / 4 * self.T / self.delta_U_out) * self.LIR * self.I_n

    def modeling(self):
        """ Расчет параметров схемы понижающего импульсного стабилизатора """

        # Расчет временных параметров
        self.T = self.t_i + self.t_p  # Период переключения (с)
        dt = self.T / 1000  # Шаг по времени (с)
        t = np.arange(0, self.t_sim, dt)  # Временная ось

        self.t = array('f', t)

        # Моделирование переходных процессов в схеме
        for i in range(len(t)):
            # Определение состояния ключа (включен/выключен)
            if (t[i] % self.T) < self.t_i:
                # Ключ включен
                dI_L_dt = (self.U_in - self.U_CE_sat - self.U_C) / self.L  # Учет падения на транзисторе
                dU_C_dt = (self.I_L - self.U_C / self.R) / self.C
                self.U_CE = self.U_CE_sat  # Напряжение коллектор-эмиттер равно падению на транзисторе
                self.U_D = self.U_in - self.U_CE_sat  # Напряжение на диоде
                self.I_in = self.I_L  # Входной ток равен току через катушку
                self.I_D = 0.0  # Ток через диод равен нулю
            else:
                # Ключ выключен
                dI_L_dt = (-self.U_C - self.U_D_drop) / self.L  # Учет падения на диоде
                dU_C_dt = (self.I_L - self.U_C / self.R) / self.C
                self.U_CE = self.U_in  # Напряжение коллектор-эмиттер равно входному напряжению
                self.U_D = self.U_D_drop  # Напряжение на диоде равно падению на диоде
                self.I_in = 0.0  # Входной ток равен нулю
                self.I_D = self.I_L  # Ток через диод равен току через катушку

            # Интегрирование (метод Эйлера)
            self.I_L += dI_L_dt * dt
            self.U_C += dU_C_dt * dt

            # Сохранение результатов
            self.I_L_arr.append(self.I_L)
            self.U_C_arr.append(self.U_C)
            self.U_CE_arr.append(self.U_CE)
            self.U_D_arr.append(self.U_D)
            self.I_in_arr.append(self.I_in)
            self.I_D_arr.append(self.I_D)


def on_change_init_param(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.U_in = st.session_state.last_U_in
    stabilizer.U_out = st.session_state.last_U_out
    stabilizer.delta_U_out = st.session_state.last_delta_U_out
    stabilizer.I_n = st.session_state.last_I_n
    stabilizer.LIR = st.session_state.last_LIR
    stabilizer.F = st.session_state.last_F
    stabilizer.calc_param()
    stabilizer.clear_arr()
    stabilizer.modeling()


def on_change_calc_param(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.F = st.session_state.last_F
    stabilizer.L = st.session_state.last_L
    stabilizer.C = st.session_state.last_C
    stabilizer.R = st.session_state.last_R
    stabilizer.t_i = st.session_state.last_t_i
    stabilizer.t_p = st.session_state.last_t_p
    stabilizer.clear_arr()
    stabilizer.modeling()
    st.session_state.auto_calc_param = False


def on_change_t_sim(stabilizer: StepDownPulseVoltageStabilizer):
    stabilizer.t_sim = st.session_state.last_t_sim
    stabilizer.clear_arr()
    stabilizer.modeling()

def run_lab():
    info_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_03', 'about_lab_03.txt')
    image_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_03', 'lab_03.png')
    # st.write("Дисциплина:")

    with open(info_file, 'r', encoding='utf-8') as file:
        content = file.read()  # Читаем весь файл

    # Добавляем радио-кнопки на боковую панель
    option = st.sidebar.radio(
        "",
        ("Теоретические сведения", "Выполнение работы", "Контрольные вопросы")
    )

    # Проверяем выбранную опцию и выводим соответствующий контент
    if option == "Теоретические сведения":
        st.write(content)  # Выводим содержимое файла
    elif option == "Выполнение работы":
        # создаем экземпляр класса Выпрямитель и инициализируем его в сессионном состоянии
        if 'stabilizer' not in st.session_state:
            st.session_state.stabilizer = StepDownPulseVoltageStabilizer()

        stabilizer = st.session_state.stabilizer

        # Инициализация параметров в сессионном состоянии
        if (('last_U_in', 'last_U_out', 'last_delta_U_out', 'last_I_n', 'last_LIR', 'last_F', 'last_L',
             'last_C', 'last_R', 'last_t_i', 'last_t_p', 'last_t_start', 'last_t_stop', 'last_t_sim',)
                not in st.session_state):
            st.session_state.last_U_in = stabilizer.U_in
            st.session_state.last_U_out = stabilizer.U_out
            st.session_state.last_delta_U_out = stabilizer.delta_U_out
            st.session_state.last_I_n = stabilizer.I_n
            st.session_state.last_LIR = stabilizer.LIR
            st.session_state.last_F = stabilizer.F
            st.session_state.last_L = stabilizer.L
            st.session_state.last_C = stabilizer.C
            st.session_state.last_R = stabilizer.R
            st.session_state.last_t_i = stabilizer.t_i
            st.session_state.last_t_p = stabilizer.t_p
            st.session_state.last_t_start = stabilizer.t_start
            st.session_state.last_t_stop = stabilizer.t_stop
            st.session_state.last_t_sim = stabilizer.t_sim

        if 'auto_calc_param' not in st.session_state:
            st.session_state.auto_calc_param = True

        # Ввод параметров схемы через боковую панель
        with st.sidebar.expander("Номинальные исходные параметры схемы", expanded=True):
            stabilizer.U_in = st.number_input("Входное напряжение (Uвх), В", key='last_U_in',
                                              on_change=on_change_init_param, args=(stabilizer,))
            stabilizer.U_out = st.number_input("Выходное напряжение (Uвых), В", key='last_U_out',
                                               on_change=on_change_init_param, args=(stabilizer,))
            stabilizer.delta_U_out = st.number_input("Размах пульсаций выходного напряжения, В", key='last_delta_U_out',
                                                     on_change=on_change_init_param, args=(stabilizer,))
            stabilizer.I_n = st.number_input("Ток нагрузки (Iн), A", key='last_I_n',
                                             on_change=on_change_init_param, args=(stabilizer,))
            stabilizer.LIR = st.number_input("Коэффициент тока дросселя", key='last_LIR',
                                             on_change=on_change_init_param, args=(stabilizer,))
            stabilizer.F = st.number_input("Частота преобразования (fпр), Гц", key='last_F',
                                           on_change=on_change_init_param, args=(stabilizer,))
            st.checkbox("Автоматически рассчитывать параметры схемы", key='auto_calc_param')

        with st.sidebar.expander("Расчетные параметры схемы", expanded=False):
            stabilizer.L = st.number_input("Индуктивность (L), Гн", key='last_L', format="%0.6f",
                                           on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.C = st.number_input("Емкость (C), Ф", key='last_C', format="%0.6f",
                                           on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.R = st.number_input("Сопротивление нагрузки (R), Ом", key='last_R', format="%0.2f",
                                           on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.t_i = st.number_input("Время импульса (t_i), с", key='last_t_i', format="%0.6f",
                                             on_change=on_change_calc_param, args=(stabilizer,))
            stabilizer.t_p = st.number_input("Время интервала (t_p), с", key='last_t_p', format="%0.6f",
                                             on_change=on_change_calc_param, args=(stabilizer,))
            if st.button("Пересчитать по исходным параметрам"):
                stabilizer.calc_param()
                stabilizer.clear_arr()
                stabilizer.modeling()

        stabilizer.t_sim = st.sidebar.number_input("Время моделирования (t_sim), с", key='last_t_sim', format="%0.6f",
                                                   on_change=on_change_t_sim, args=(stabilizer,))

        st.header("Исследование импульсного стабилизатора напряжения понижающего типа")
        st.image(image_file)

        st.subheader("Результаты моделирования работы схемы")

        # График тока через катушку
        st.markdown("**Ток через катушку, входной ток и ток через диод**")
        fig1, ax1 = plt.subplots(figsize=(12, 3))

        ax1.plot(stabilizer.t, stabilizer.I_L_arr, label='Ток через катушку (I_L)', color='blue')
        ax1.plot(stabilizer.t, stabilizer.I_in_arr, label='Входной ток (I_in)', color='green', linestyle='--')
        ax1.plot(stabilizer.t, stabilizer.I_D_arr, label='Ток через диод (I_D)', color='red', linestyle='-.')

        ax1.set_xlabel('Время (с)')
        ax1.set_ylabel('Ток (А)')
        # ax1.set_title('Ток через катушку индуктивности')
        # Добавляем сетку
        ax1.grid(True)
        ax1.legend()
        # Отображаем график
        st.pyplot(fig1)

        # График напряжения на нагрузке
        st.markdown("**Напряжение на нагрузке и напряжение на диоде**")
        fig3, ax3 = plt.subplots(figsize=(12, 4))

        ax3.plot(stabilizer.t, stabilizer.U_C_arr, label='Напряжение на нагрузке (U_C)', color='blue')
        ax3.plot(stabilizer.t, stabilizer.U_D_arr, label='Напряжение диоде U_VD', color='red', linestyle='-.')

        ax3.set_xlabel('Время (с)')
        ax3.set_ylabel('Напряжение (В)')
        #ax3.set_title('Напряжение на нагрузке')
        # Добавляем сетку
        ax3.grid(True)
        ax3.legend()
        # Отображаем график
        st.pyplot(fig3)

        with st.expander("Нажмите, чтобы задать временной фрагмент для просмотра графиков"):
            st.markdown("**Данный функционал находится в разработке**")

    else:
        st.title("Контрольные вопросы")
