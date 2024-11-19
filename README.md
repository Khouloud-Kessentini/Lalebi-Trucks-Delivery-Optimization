# Lalebi-Trucks-Delivery-Optimization

In this project, we study the routing of delivery trucks for Lablebi, a popular and incredibly delicious Tunisian dish. Since Lablebi is best enjoyed hot, it is essential to optimize the routing for maximum efficiency. The routing task in this project is formulated as a Capacitated Vehicle Routing Problem (CVRP) and is expressed through the following mathematical model.

## Problem Formulation

### Decision Variables

- Let \( x_{ij}^k \in \{0, 1\} \) be a binary variable:
  - \( x_{ij}^k = 1 \) if vehicle \( k \) travels directly from node \( i \) to node \( j \), and 
  - \( x_{ij}^k = 0 \) otherwise.
- Let \( u_i \) be a continuous variable representing the cumulative demand served when reaching node \( i \).

### Mathematical Model

$$
\begin{align}
\min & \sum_{k = 1}^{|K|} \sum_{i = 0}^{|N|} \sum_{j = 0}^{|N|} d_{ij}x_{ij}^k, \label{eq:objectivecvrp}\\
\text{s.t.} & \sum_{i = 0}^{|N|} x_{ij}^k = \sum_{i = 0}^{|N|} x_{ji}^k \qquad \forall j \in N, \enspace k \in K, \label{eq:cvrpflowinflowout} \\
& \sum_{k = 1}^{|K|} \sum_{i = 0}^{|N|} x_{ij}^k = 1 \qquad \forall j \in N \setminus \{0\}, \label{eq:cvrpenteredonce}\\
& \sum_{j = 1}^{|N|} x_{0j}^k = 1 \qquad \forall k \in K, \label{eq:cvrpleavedepot}\\
& \sum_{i = 0}^{|N|} \sum_{j = 1}^{|N|} q_{j} x_{ij}^k \leq Q \qquad \forall k \in K, \label{eq:cvpcapacity}\\
& x_{ii}^k = 0 \qquad \forall k \in K, \enspace i \in N, \label{eq:cvrpnodetonode} \\
& u_{j} - u_{i} \geq q_{j} - Q (1 - x_{ij}^k) \qquad \forall i, j \in N \setminus \{0\}, \enspace i \neq j, \label{subtour1}\\
& q_{i} \leq u_{i} \leq Q \qquad \forall i \in N \setminus \{0\}, \label{subtour2}\\
& x_{ij}^k \in \{0, 1\} \qquad \forall i, j \in N, \enspace k \in K. \label{eq:cvrpintegrity}
\end{align}
$$

### Explanation

- **Objective Function** \eqref{eq:objectivecvrp}: Minimize the total traveled distance by the vehicles.
- **Constraints**:
  1. \eqref{eq:cvrpflowinflowout}: Flow conservation ensures that for every node, the number of incoming routes equals the number of outgoing routes for each vehicle.
  2. \eqref{eq:cvrpenteredonce}: Every node (except the depot) is visited exactly once by any vehicle.
  3. \eqref{eq:cvrpleavedepot}: Each vehicle leaves the depot exactly once.
  4. \eqref{eq:cvpcapacity}: The total demand served by each vehicle cannot exceed its capacity \( Q \).
  5. \eqref{eq:cvrpnodetonode}: Prevents self-loops (a vehicle visiting the same node twice in succession).
  6. \eqref{subtour1}: Subtour elimination constraints using continuous variables \( u_i \).
  7. \eqref{subtour2}: Bounds on the continuous variables \( u_i \) corresponding to demands \( q_i \) and vehicle capacity \( Q \).
  8. \eqref{eq:cvrpintegrity}: Binary decision variables indicate whether an edge is traversed by a vehicle.
