# Estimands and source-variable glossary

| Display term | Meaning / internal variable |
|---|---|
| M | Binary measured outcome, using the disease/analysis-specific definition in the source |
| S | Binary reported-diagnosis outcome |
| U | Observable discordant state M=1, S=0 |
| V | Observable discordant state M=0, S=1 |
| 00, 11 | M=0/S=0 and M=1/S=1 concordant states |
| OR(M), OR(S) | Exposure odds ratios for the corresponding binary outcome |
| Δc | Paired conditional difference log OR(S) − log OR(M), with within-person covariance |
| Δm | Difference in marginal standardized log odds ratios, using a shared target population |
| C_U, C_V | Symmetric two-order allocations of Δm to the observed U and V state modifications; C_U + C_V = Δm |
| `delta` | Context-dependent source column: Δm in joint/simulation outputs, Δc in the conditional programme scan |
| `CU`, `CV` | Legacy simulation column keys for C_U and C_V, not CVAI |
| `unreported_component` | Legacy internal key for C_U; its name does not establish underdiagnosis |
| `history_normal_component` | Legacy internal key for C_V; its name does not establish overdiagnosis or treatment failure |
| `risk_M0`, `risk_M1` | Standardized M probabilities under the specified exposure levels 0 and 1 |
| `risk_S0`, `risk_S1` | Corresponding standardized S probabilities |
| `logOR_M`, `logOR_S` | Marginal log odds ratios in joint outputs |
| `RD_M`, `RD_S` | Standardized risk difference within each outcome definition; do not interchange with log-OR differences |
| CVAI | Chinese visceral adiposity index; it is unrelated to the allocation C_V |
| `estimable_rate` | Number of successful estimator fits divided by attempted replicates |
| `coverage_conditional` | Covering intervals divided by estimable replicates |
| `coverage_all` | Covering intervals divided by all attempted replicates, counting failures as noncoverage |
| `coverage_mcse` | Monte Carlo standard error on the proportion scale; multiply by 100 for percentage points |
| `bias`, `rmse` | On the estimand's native scale (here log OR differences/allocations), not percentage points |
| `edu`, `edu3` | Programme-specific education encoding; consult the relevant builder. They are not globally identical education variables |

The estimator's joint-state order is **[00, V, U, 11]**. Some simulation generating anchors are written in [00, U, V, 11] order and explicitly permuted by the source. Do not reorder them manually.

Exposure level definitions depend on the selected contrast. Current-versus-never excludes former smokers; current-versus-noncurrent groups former and never smokers in the comparator. Model fitting weights and target-standardization weights define separate choices in the HRS application.

The separate China-focused risk-difference manuscript uses D = RD(M) − RD(S). It is not the sign convention or estimand used for the JCE log-OR allocation. Historical filenames or shared survey inputs do not make these quantities interchangeable.
