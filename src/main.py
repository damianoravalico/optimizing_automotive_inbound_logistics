import gurobipy as gp
from gurobipy import quicksum
from src.notation.sets_and_params import *

model = gp.Model()

# Decision variables
# Indicating if supplier i ∈ L uses transportation mode m ∈ M
v_i_m = model.addVar(vtype=gp.GRB.BINARY, name="v_i_m", column=[(i, m) for i in L for m in M])

# Indicating if supplier i ∈ L uses transportation mode m ∈ M on day j ∈ D
p_ij_m = model.addVar(vtype=gp.GRB.BINARY, name="p_ij_m", column=[(i, j, m) for i in L for j in D for m in M])

# Indicating if delivery of supplier i ∈ L on day j ∈ D is above the daily demand
tau_ij = model.addVar(vtype=gp.GRB.BINARY, name="tau_ij", column=[(i, j) for i in L for j in D])

# Indicating if a single delivery in the planning horizon is chosen for supplier i ∈ L
gamma_i = model.addVar(vtype=gp.GRB.BINARY, name="gamma_i", column=[i for i in L])

# Percentage order quantity of the horizon demand for supplier i ∈ L using transportation mode m ∈ M on day j ∈ D
q_ij_m = model.addVar(lb=0, ub=1, vtype=gp.GRB.CONTINUOUS, name="q_ij_m",
                      column=[(i, j, m) for i in L for j in D for m in M])

# Percentage order quantity of the horizon demand for supplier i ∈ L using transportation mode m ∈ M on day j ∈ D
s_ij = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name="s_ij",
                    column=[(i, j) for i in L for j in [0, D]])

# Indicating if order frequency o ∈ O is selected for supplier i ∈ L
beta_io = model.addVar(vtype=gp.GRB.BINARY, name="beta_io", column=[(o, i) for o in O for i in L])

# Number of trucks of supplier i ∈ L on day j ∈ D for FTL / FTL empty load carrier return
n_ij = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.INTEGER, name="n_ij",
                    column=[(i, j) for i in L for j in D])

# Number of trucks of supplier i ∈ L on day j ∈ D for FTL / FTL empty load carrier return
n_ij_ec = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.INTEGER, name="n_ij_ec",
                       column=[(i, j) for i in L for j in D])

# Number of trucks for zone z ∈ Z on day j ∈ D for transport mode LTL
n_jz_LTL = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.INTEGER, name="n_jz_LTL",
                        column=[(z, j) for z in Z for j in D])

# Weight of the order quantity for a weight range (B_b, B_b+1) from supplier, i ∈ L using LTL / LTL empty load carrier
# return on day j ∈ D
w_bij = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name="w_bij",
                     column=[(b, i, j) for b in Q for i in L for j in D])

# Weight of the order quantity for a weight range (B_b, B_b+1) from supplier, i ∈ L using LTL / LTL empty load carrier
# return on day j ∈ D
w_bij_ec = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name="w_bij_ec",
                        column=[(b, i, j) for b in Q for i in L for j in D])

# Weight of the order quantity for weight range (B_k−1_CES, B_k_CES) from supplier i ∈ L using CES on day j ∈ D
w_kij_CES = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, name="w_bij_CES",
                         column=[(k, i, j) for k in K for i in L for j in D])

# Weight of carriers to satisfy one days demand for supplier i ∈ L
omega_i_ec = model.addVar(lb=0, ub=gp.GRB.INFINITY, vtype=gp.GRB.CONTINUOUS, column=[i for i in L])

# Indicator for weight range b ∈ Q selected for LTL/LTL empty load carrier returns from supplier i ∈ L on day j ∈ D
alpha_bij = model.addVar(vtype=gp.GRB.BINARY, name="alpha_bij", column=[(b, i, j) for b in Q for i in L for j in D])

# Indicator for weight range b ∈ Q selected for LTL/LTL empty load carrier returns from supplier i ∈ L on day j ∈ D
alpha_bij_ec = model.addVar(vtype=gp.GRB.BINARY, name="alpha_bij_ec",
                            column=[(b, i, j) for b in Q for i in L for j in D])

# Indicator for weight range k ∈ K selected for CES from supplier i ∈ L on day j ∈ D
delta_kij = model.addVar(vtype=gp.GRB.BINARY, name="delta_kij", column=[(k, i, j) for k in K for i in L for j in D])

# Objective function
model.setObjective(
    quicksum(C_i_D[i] * (n_ij[i, j] + n_ij_ec[i, j]) for i in L for j in D) +
    quicksum(B_k_pCES[k] * delta_kij[k, i, j] for i in L for j in D for k in K) +
    quicksum(B_ib_p[i, b] * (w_bij[b, i, j] + w_bij_ec[b, i, j]) for i in L for j in D for b in Q) +
    A * quicksum(p_ij_m[i, j, m] for i in L for j in D for m in M) +
    len(D) * quicksum(
        C_i_dR[i] * u_io_R[i, o] * beta_io[i, o] + C_i_dI[i] * u_io_I[i, o] * beta_io[i, o] for i in L for o in O),
    gp.GRB.MINIMIZE
)

# Constraints
for i in L:
    for k in D:
        model.addConstr(quicksum(q_ij_m[i, j, m] + s_i0[i] for m in M for j in range(k)) >= k / len(D), name="2")

for i in L:
    model.addConstr(quicksum(q_ij_m[i, j, m] for m in M for j in D) == 1, name="3")

for i in L:
    for j in D:
        model.addConstr(quicksum(p_ij_m[i, j, m] for m in M) <= 1, name="4")

for i in L:
    for j in D:
        for m in M:
            model.addConstr(q_ij_m[i, j, m] <= p_ij_m[i, j, m], name="5")

for i in L:
    for j in D:
        for m in [0, 1]:
            model.addConstr(q_ij_m[i, j, m] >= Q_min / d_i[i] * p_ij_m, name="6")

for i in L:
    for j in D:
        model.addConstr(q_ij_m[i, j, 2] >= 1 / len(D) * p_ij_m[i, j, 2], name="7")

for i in L:
    model.addConstr(quicksum(v_i_m[i, m] for m in M) == 1, name="8")

for i in L:
    for j in D:
        for m in M:
            model.addConstr(p_ij_m[i, j, m] <= v_i_m[i, m], name="9")

for i in L:
    for j in range(len(D) // 2):
        for m in M:
            model.addConstr(p_ij_m[i, j, m] + gamma_i[i] >= p_ij_m[i, j + len(D) // 2, m], name="10")

for i in L:
    for j in range(len(D) // 2):
        for m in M:
            model.addConstr(p_ij_m[i, j, m] <= p_ij_m[i, j + len(D) // 2, m] + gamma_i[i], name="11")

for i in L:
    model.addConstr(quicksum(p_ij_m[i, j, m] for j in D for m in M) <= 1 + len(D) * (1 - gamma_i[i]), name="12")

for i in L:
    model.addConstr(quicksum(q_ij_m[i, j, 2] for j in range(len(D) // 2)) <=
                    quicksum(q_ij_m[i, j + len(D) // 2, 2] for j in range(len(D) // 2)) + gamma_i[i], name="13")

for j in D:
    model.addConstr(quicksum(n_ij[i, j] for i in L) + quicksum(n_jz_LTL[j, z] for z in Z) <= Cap_GI, name="14")

for j in D:
    model.addConstr(quicksum(p_ij_m[i, j, 1] for i in L) <= Cap_WK, name="15")

for i in L:
    for j in D[1:]:
        model.addConstr(s_ij[i, j - 1] + quicksum(q_ij_m[i, j, m] for m in M) - 1 / len(D) == s_ij[i, j], name="16")

for i in L:
    model.addConstr(s_i0[i] + SS_i[i] + quicksum(q_ij_m[i, 0, m] for m in M) - 1 / len(D) == s_ij[i, 0], name="17")

for h in H:
    for j in D:
        model.addConstr(quicksum(f_hi_qp[h, i] * d_i[i] * s_ij[i, j] for i in L) <= Cap_h, name="18")

for i in L:
    for j in D:
        model.addConstr(quicksum(q_ij_m[i, j, m] for m in M) >= tau_ij[i, j] / len(D), name="19")

for i in L:
    model.addConstr(quicksum(tau_ij[i, j] for j in D) == quicksum(o * beta_io[i, o] for o in O), name="20")

for i in L:
    model.addConstr(quicksum(beta_io[i, o] for o in O) == 1, name="21")
