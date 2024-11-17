import os

import streamlit as st
from pathlib import Path

from datalist import Datalist

# Создаем экземпляр класса списка дисциплин
disciplines = Datalist('disciplines.json')


# Создание страницы лабораторной работы по выбранной дисциплине
def create_page_lab(discipline_name):
    col1, col2 = st.columns([1, 4])
    with col1:
        st.write("Дисциплина:")
    with col2:
        st.write(discipline_name)


# Чтение списка лабораторных работ по выбранной дисциплине
#   labdirectory    - директория с лабораторными работами
#   pattern         - фильтр выбора файлов лабораторных работ
def read_list_lab(labdirectory, pattern):
    current_lab_dir = os.path.join(os.getcwd(), 'lab_dir', labdirectory)
    filtered_files = [f.name.split('.')[0] for f in Path(current_lab_dir).glob(pattern)]
    return filtered_files


def path_to_lab_work(labdirectory, labwork):
    return os.path.join(os.getcwd(), 'lab_dir', labdirectory, labwork)


st.title("Лабораторные работы")

# Получаем список названий дисциплин
list_discipline = []
for data in disciplines:
    list_discipline.append(data['name'])

# Добавление списка дисциплин
discipline = st.selectbox("Выберите дисциплину", list_discipline)

# получаем имя директории для выбранной дисциплины
directories = disciplines.get_directories(discipline)
labs_work = read_list_lab(directories, 'lab*')

# Добавление списка лабораторных работ по выбранной дисциплине
lab_work = st.selectbox("Выберите лабораторную работу", labs_work)

if st.sidebar.button("Приступить к работе"):
    if all([directories, lab_work]):
        st.session_state.current_lab_info = [directories, lab_work]
        st.session_state.current_lab_name = f'{directories}_{lab_work}'

        st.session_state.go_to_current_lab = True

        st.rerun()
