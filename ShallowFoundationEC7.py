import streamlit as st
import numpy as np

st.title("Cálculo da Capacidade de Carga de Fundação")

# ========= 1. ENTRADAS =========
st.header("Entradas")

gamma = st.number_input("Peso específico do solo γ (kN/m³)", value=20.0)
B = st.number_input("Largura da fundação B (m)", value=1.5)
L = st.number_input("Comprimento da fundação L (m)", value=1.0)
H = st.number_input("Força horizontal H (kN)", value=1.2)
V = st.number_input("Carga vertical V (kN)", value=1000.0)
c_ = st.number_input("Coesão c (kPa)", value=0.0)
phi_deg = st.number_input("Ângulo de atrito interno φ (graus)", value=30.0)
phi_rad = np.radians(phi_deg)
q_ = st.number_input("Pressão efetiva q (kPa)", value=21.6)

M_L = st.number_input("Momento em torno de L (kN·m)", value=200.0)
M_B = st.number_input("Momento em torno de B (kN·m)", value=150.0)

# ========= 2. EXCENTRICIDADES E ÁREA EFETIVA =========
e_B = M_L / V
e_L = M_B / V
B_ = B - 2 * e_B
L_ = L - 2 * e_L

if B_ <= 0 or L_ <= 0:
    st.error("B' ou L' inválido — verifique os momentos e a carga vertical.")
    st.stop()

A_ = B_ * L_

# ========= 3. FATORES DE CAPACIDADE DE CARGA =========
def N_q(phi): return np.exp(np.pi * np.tan(phi)) * (np.tan(np.radians(45) + phi / 2))**2
def N_c(N_q, phi): return (N_q - 1) / np.tan(phi)
def N_gamma(N_q, phi): return 2 * (N_q - 1) * np.tan(phi)

N_q_ = N_q(phi_rad)
N_c_ = N_c(N_q_, phi_rad)
N_gamma_ = N_gamma(N_q_, phi_rad)

# ========= 4. FATORES DE FORMA =========
def s_gamma(B_, L_): return 1 - 0.3 * (B_ / L_)
def s_q(B_, L_, phi): return 1 + (B_ / L_) * np.sin(phi)
def s_c(s_q, N_q): return s_q * (N_q - 1) / (N_q - 1)

s_gamma_ = s_gamma(B_, L_)
s_q_ = s_q(B_, L_, phi_rad)
s_c_ = s_c(s_q_, N_q_)

# ========= 5. FATORES DE DIREÇÃO (m) =========
def m_B(B_, L_): return (2 + B_ / L_) / (1 + B_ / L_)
m = m_B(B_, L_)  # Pode trocar para m_L se H for na outra direção

# ========= 6. FATORES DE PROFUNDIDADE =========
def i_gamma(H, V, A_, c_, phi, m):
    return (1 - (H / (V + A_ * c_ / np.tan(phi)))) ** (m + 1)

def i_q(H, V, A_, c_, phi, m):
    return (1 - (H / (V + A_ * c_ / np.tan(phi)))) ** m

def i_c(i_q, N_c, phi): return i_q - (1 - i_q) / (N_c * np.tan(phi))

i_gamma_ = i_gamma(H, V, A_, c_, phi_rad, m)
i_q_ = i_q(H, V, A_, c_, phi_rad, m)
i_c_ = i_c(i_q_, N_c_, phi_rad)

# ========= 7. CÁLCULO DE QR =========
def q_r(gamma, B_, N_gamma_, s_gamma_, i_gamma_,
        c_, N_c_, s_c_, i_c_,
        q_, N_q_, s_q_, i_q_):
    return (
        0.5 * gamma * B_ * N_gamma_ * s_gamma_ * i_gamma_ +
        c_ * N_c_ * s_c_ * i_c_ +
        q_ * N_q_ * s_q_ * i_q_
    )

q_r_ = q_r(
    gamma, B_, N_gamma_, s_gamma_, i_gamma_,
    c_, N_c_, s_c_, i_c_,
    q_, N_q_, s_q_, i_q_
)

# ========= 8. RESULTADOS =========
st.header("Resultados")
st.write(f"**e_B** = {e_B:.3f} m | **B'** = {B_:.3f} m")
st.write(f"**e_L** = {e_L:.3f} m | **L'** = {L_:.3f} m")
st.write(f"**Área efetiva A'** = {A_:.3f} m²")
st.write(f"**Fatores de capacidade de carga:** Nq = {N_q_:.2f}, Nc = {N_c_:.2f}, Nγ = {N_gamma_:.2f}")
st.write(f"**Capacidade de carga drenada q_r** = {q_r_:.2f} kPa")
st.write(f"**Capacidade de carga total R** = {q_r_ * A_:.2f} kN")
