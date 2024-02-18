from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit import Aer, execute
from qiskit.quantum_info import partial_trace
from qiskit.providers.fake_provider import FakeVigo
from qiskit_aer import AerSimulator
from qiskit.visualization import plot_bloch_multivector
import pandas as pd
import rustworkx as rx
import csv
from rustworkx.visualization import graphviz_draw
from qiskit.quantum_info import state_fidelity,partial_trace
from qiskit_experiments.library import StateTomography
from qiskit_ibm_provider import IBMProvider,least_busy
provider = IBMProvider()
aer_sim = AerSimulator()
vigo = FakeVigo()


#量子回路制作コード
def makeU_telepo_curcit(num1, num2, num3):
    qr = QuantumRegister(3)
    a_0 = ClassicalRegister(1)
    a_1 = ClassicalRegister(1)
    b_0 = ClassicalRegister(1)
    qc = QuantumCircuit(qr, a_0, a_1, b_0)
    qc.u(num1, num2, num3, 0)
    qc.barrier()
    qc.h(1)
    qc.cx(1, 2)
    qc.barrier()
    qc.cx(0, 1)
    qc.h(0)
    qc.measure(1, a_1)
    qc.measure(0, a_0)
    qc.barrier()
    with qc.if_test((a_1, 1)):
        qc.x(2)
    with qc.if_test((a_0, 1)):
        qc.z(2)
    qc.barrier()
    qc.measure(2, b_0)
    return qc

def return_least_busy():
    backend = least_busy(provider.backends
                         (
    simulator=False,
    operational=True,
    open_pulse=True,
    dynamic_reprate_enabled = True,
    filters=lambda b: b.max_shots > 5000
))
    backend_config = backend.configuration()
    backend_property = backend.properties()
    threshold = 0.01
    # 2量子ゲートデータ
    data = [["gate", "tuple", "error"]]
    for tuple_i in backend.coupling_map.get_edges():
        data.append(["cx gate",tuple_i,backend_property.gate_error(backend.basis_gates[0],tuple_i)])
    # CSVファイルへの書き込み
    with open("errors.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    filtered_data = [row for row in data if isinstance(row[2], float) and row[2] <= threshold]
    meta_data = ["gate", "tuple", "error"]
    # CSVファイルへの書き込み
    with open("f_errors.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(meta_data)
        writer.writerows(filtered_data)
    #フィルターリストの制作
    import ast
    df = pd.read_csv("f_errors.csv", encoding="SHIFT_JIS")
    filtered_list = list(df["tuple"])
    filtered_list_2 =[]
    for tuple_i in filtered_list:
        newtuple=ast.literal_eval(tuple_i)
        filtered_list_2.append(newtuple)
    #coupling_map
    G2 =rx.PyDiGraph()
    G2.add_nodes_from(range(backend_config.n_qubits))
    for tuple_i in filtered_list_2:
        G2.add_edge(tuple_i[0],tuple_i[1],backend_property.gate_error(backend.basis_gates[0],tuple_i)*100)
    graphviz_draw(G2,image_type="jpeg",method="neato",filename="image/result/coupling_map.png")
    return backend.name

def reset_coupling_map(input):
    backend = least_busy(provider.backends
                         (
    simulator=False,
    operational=True,
    open_pulse=True,
    dynamic_reprate_enabled = True,
    filters=lambda b: b.max_shots > 5000
))
    backend_config = backend.configuration()
    backend_property = backend.properties()
    threshold = input
    # 2量子ゲートデータ
    data = [["gate", "tuple", "error"]]
    for tuple_i in backend.coupling_map.get_edges():
        data.append(["cx gate",tuple_i,backend_property.gate_error(backend.basis_gates[0],tuple_i)])
    # CSVファイルへの書き込み
    with open("errors.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(data)
    filtered_data = [row for row in data if isinstance(row[2], float) and row[2] <= threshold]
    meta_data = ["gate", "tuple", "error"]
    # CSVファイルへの書き込み
    with open("f_errors.csv", 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(meta_data)
        writer.writerows(filtered_data)
    #フィルターリストの制作
    import ast
    df = pd.read_csv("f_errors.csv", encoding="SHIFT_JIS")
    filtered_list = list(df["tuple"])
    filtered_list_2 =[]
    for tuple_i in filtered_list:
        newtuple=ast.literal_eval(tuple_i)
        filtered_list_2.append(newtuple)
    #coupling_map
    G2 =rx.PyDiGraph()
    G2.add_nodes_from(range(backend_config.n_qubits))
    for tuple_i in filtered_list_2:
        G2.add_edge(tuple_i[0],tuple_i[1],backend_property.gate_error(backend.basis_gates[0],tuple_i)*100)
    graphviz_draw(G2,image_type="jpeg",method="neato",filename="image/result/coupling_map.png")

def process_numbers_prefect(num1, num2, num3):
    num1=float(num1)
    num2=float(num2)
    num3=float(num3)
    qc = makeU_telepo_curcit(num1, num2, num3)
    # 回路を描画
    qc.draw(output="mpl", filename="image/result/qc")
    qc.save_density_matrix()
    perfect_result=aer_sim.run(qc).result().data()['density_matrix']
    perfect_state = partial_trace(perfect_result,[0,1])
    # 結果を取得
    plot_bloch_multivector(perfect_state, filename="image/result/vector")
    ###
    return "done"

def process_numbers_Fake(num1, num2, num3):
    num1=float(num1)
    num2=float(num2)
    num3=float(num3)
    qc = makeU_telepo_curcit(num1, num2, num3)
    qc.save_density_matrix()
    perfect_result=aer_sim.run(qc).result().data()['density_matrix']
    sim_result = vigo.run(qc).result().data()['density_matrix']
    perfect_state = partial_trace(perfect_result,[0,1])
    sim_state = partial_trace(sim_result,[0,1])
    plot_bloch_multivector(sim_state, filename="image/result/Fake_state")
    Fake_to_prefect_fidelity = round(state_fidelity(perfect_state,sim_state),3)
    return Fake_to_prefect_fidelity

def process_numbers_real(num1, num2, num3, num5, num6, num7, str8):
    num1=float(num1)
    num2=float(num2)
    num3=float(num3)
    qc =makeU_telepo_curcit(num1, num2, num3)
    #statevector
    # fidelity
    real_backend = provider.get_backend(str8)
    st = StateTomography(qc,physical_qubits=[num5,num6,num7])
    stdata = st.run(real_backend).block_for_results()
    state_result = stdata.analysis_results("state")

    backend1 = Aer.get_backend('aer_simulator')
    st1 = StateTomography(qc)
    stdata1 = st1.run(backend1).block_for_results()
    state_result1 = stdata1.analysis_results("state")

    U_real_state = partial_trace(state_result.value,[0,1])
    U_prefect_state = partial_trace(state_result1.value,[0,1])
    plot_bloch_multivector(U_real_state, filename="image/result/real_state")
    real_to_prefect_fidelity = round(state_fidelity(U_real_state,U_prefect_state),3)
    return real_to_prefect_fidelity
