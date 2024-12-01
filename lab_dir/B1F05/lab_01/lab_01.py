import random
import os

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd


def run_lab():
    info_file = os.path.join(os.getcwd(), 'lab_dir', 'B1F05', 'lab_01', 'about_lab_01.txt')
    # content = '123'
    with open(info_file, 'r', encoding='utf-8') as file:
        content = file.read()  # Читаем весь файл

    # Добавляем радио-кнопки на боковую панель
    option = st.sidebar.radio(
        "",
        ("Теоретические сведения", "Исследование нагрузочной характеристики", "Контрольные вопросы")
    )

    # Проверяем выбранную опцию и выводим соответствующий контент
    if option == "Теоретические сведения":
        st.write(content)  # Выводим содержимое файла
    elif option == "Исследование нагрузочной характеристики":
        # Генерируем новое рандомное число и сохраняем в переменной
        random_number = random.uniform(-0.1, 0.1)

        # Выводим рандомное число
        # st.write(f'Ваше рандомизированное число: {random_number}')

        # Инициализируем массив в сессионном состоянии
        if 'data_array' not in st.session_state:
            st.session_state.data_array = []

        # Ввод значения напряжения переменного тока
        Uinput = st.number_input('Введите Входное напряжение преобразователя', min_value=160, max_value=220,
                                 value="min", step=1)
        st.write('Uвх ПЧ-50/25 = ', Uinput, ' В')
        U0 = 0.083 * Uinput + 16.74  # Пересчет выходного напряжения ПЧ
        # st.write('Uвых ПЧ-50/25 = ', U0, ' В')
        U01 = U0 + random_number
        # st.write('Uвых R ПЧ-50/25 = ', U01, ' В')

        # Добавляем слайдер с сопротивлением нагрузки
        RLoad = st.slider("Сопротивление нагрузки", 6.50, 25.00, 8.50)
        Rvn = 0.5

        ILoad1 = U01 / (RLoad + Rvn)
        Udiod = 0.2 * ILoad1 + 0.1
        ULoad1 = RLoad * ILoad1 - Udiod
        ILoad = round(ILoad1, 2)
        ULoad = round(ULoad1, 2)
        # st.write("Напряжение диода", Udiod, 'В')
        st.write("Ток нагрузки", ILoad, 'А')
        st.write("Напряжение на нагрузке", ULoad, 'В')
        # Вычисляем второе значение (половину значения слайдера)
        # half_slider_value = RLoad / 2

        # Обработчик событий для слайдера
        if st.button("Добавить в массив"):
            # Добавляем кортеж в массив
            st.session_state.data_array.append((ILoad, ULoad))
            st.success(f"Добавлено в массив: ({ILoad}, {ULoad})")

        # Выводим все значения массива
        # st.table({"Двумерный массив данных:": st.session_state.data_array})

        # Выводим все значения массива Вариант 1
        # st.text("Массив данных:")
        # for value in st.session_state.data_array:
        #    st.text(value)

        # Выводим все значения массива Вариант 2
        st.write("Значения массива:", ", ".join([f"({x}, {y})" for x, y in st.session_state.data_array]))

        # Построение графика
        if st.button("Построить график"):
            # Извлекаем значения из массива для построения графика
            x_values = [item[0] for item in st.session_state.data_array]
            y_values = [item[1] for item in st.session_state.data_array]

            # Строим график
            fig, ax = plt.subplots()
            ax.plot(x_values, y_values, marker='o')
            ax.set_ylabel('Напряжение на нагрузке')
            ax.set_xlabel('Ток нагрузки')
            ax.set_title('Нагрузочная характеристика')
            # Добавляем сетку
            ax.grid(True)
            # Отображаем график
            st.pyplot(fig)
    else:
        st.title("Контрольные вопросы")
