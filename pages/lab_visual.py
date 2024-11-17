import os

import streamlit as st
import importlib.util

module_dir = st.session_state.current_lab_info[0]
module_name = st.session_state.current_lab_info[1]
module_file_path = os.path.join(os.getcwd(), 'lab_dir', module_dir, module_name, f'{module_name}.py')

spec = importlib.util.spec_from_file_location(module_name, module_file_path)
lab_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab_module)

lab_module.run_lab()  # Вызов функции из загруженного модуля
