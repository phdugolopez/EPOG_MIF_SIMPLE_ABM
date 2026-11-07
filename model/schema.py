"""One schema for every output table: each column's name, meaning, unit, step, mechanism
and phase, as in section 3 of docs/design/collector-brief.md.

Step is the step of the period at which the value is final: 0 run start, 1 Pricing,
2 Demand, 3 Production and accounts, 4 Scrapping, 5 Investment, 6 Entry and exit,
7 collector; None for identifiers. Phase: "v1" (needed for 6 and 20 November) or
"later". Names with {label}, {tech} or {parameter} are templates, expanded by `columns`
with the labels (sorted keys of HURDLE_RULES), the techniques (keys of SHAIKH_PLANTS) and
the parameters of a configuration. docs/design/collector.md is generated from this file
(python -m analysis.schema_doc); tests/test_schema.py checks that the tables written by
run.py and this schema have exactly the same columns.
"""

from typing import NamedTuple


class Column(NamedTuple):
    name: str
    meaning: str
    unit: str
    step: int | None
    mechanism: str
    phase: str = "v1"


TABLES = ("runs", "macro", "groups", "firms", "plants", "events", "flows")

# Parameters stored in `runs` under the brief's name rather than their lower-case name.
RUN_ALIASES = {"SEED": "seed", "PRICING_ANCHOR": "anchor", "MENU": "menu"}

RUN_ID = Column("run_id", "experiment, cell, population and seed in one string: "
                "{experiment}_{cell}_{population}_s{seed}", "text", 0, "run.py")

PA, DE, PR, SC, IN, EE = ("Pricing", "Demand", "Production and accounts", "Scrapping",
                          "Investment", "Entry and exit")
CO = "collector"
Q, M, P, R = "units/period", "w.u.", "w.u./unit", "per period"
KAPPA = "w.u. per unit/period"

SCHEMA: dict[str, list[Column]] = {
    "runs": [
        RUN_ID,
        Column("seed", "master seed of the single random stream random.Random(SEED)",
               "integer", 0, "parameters.py"),
        Column("code_version", "git commit hash, with -dirty if tracked files had "
               "uncommitted changes; unknown if git is not available", "text", 0, "run.py"),
        Column("param_hash", "sha256 of the JSON of every upper-case parameter, sorted",
               "text", 0, "run.py"),
        Column("experiment", "selection, invasion, aggregate, neutral_control, "
               "swapped_labels, identical (default baseline)", "text", 0, "run.py"),
        Column("population", "starting mix: S50_O50, S95_O5, ... (default baseline)",
               "text", 0, "run.py"),
        Column("cell", "treatment cell: BASE, WAR+, CHI-, CRED or a grid code "
               "(default baseline)", "text", 0, "run.py"),
        Column("anchor", "normal price rule, PRICING_ANCHOR: target_return or markup",
               "text", 0, PA),
        Column("okishio_price", "price at which Okishio firms evaluate techniques; always "
               "own (the firm's own price) in the code", "text", 0, IN),
        Column("menu", "techniques on offer for new plants, MENU, as JSON", "text", 0, IN),
        Column("horizon", "periods actually run (len of the macro table)", "periods", 7,
               "run.py"),
        Column("burn_in", "periods discarded by the analysis; 0, no burn-in yet", "periods",
               0, "run.py"),
        Column("n_check_fail", "periods in which a check failed (CHECKS_RAISE = False); "
               "must be 0", "count", 7, CO),
        Column("wall_seconds", "run time of Industry.run, to budget the seeds", "seconds",
               7, "run.py"),
        Column("python_version", "Python version of the run", "text", 0, "run.py"),
        Column("{parameter}", "every other parameter of parameters.py under its "
               "lower-case name; tuples and dicts as JSON", "as defined", 0,
               "parameters.py"),
    ],
    "macro": [
        RUN_ID,
        Column("t", "period", "period", None, "scheduler"),
        Column("demand", "industry demand D_t", Q, 2, DE),
        Column("sales_total", "sum of sales", Q, 2, DE),
        Column("unmet_total", "demand no firm could serve, after reallocation", Q, 2, DE),
        Column("unmet", "sum of the firms' unmet demand l_i, before reallocation", Q, 2, DE),
        Column("hhi", "Herfindahl index on the shares after step 6", "0-1", 6, CO),
        Column("hhi_sales", "Herfindahl index on sales shares; None without sales", "0-1",
               2, CO),
        Column("n_firms", "firms in the industry at the end of the period", "count", 6, EE),
        Column("n_active", "firms active at step 1 (that produced this period)", "count",
               1, CO),
        Column("price_avg", "sales-weighted mean price", P, 2, DE),
        Column("min_price", "lowest posted price", P, 1, PA),
        Column("max_price", "highest posted price", P, 1, PA),
        Column("price_lead", "lowest posted price p^lead_t, the leader for next period", P,
               1, PA),
        Column("leader_ids", "ids of every firm posting the lowest price (math.isclose), "
               "sorted, as JSON", "ids", 1, CO),
        Column("n_leaders", "number of tied leaders", "count", 1, CO),
        Column("leader_id", "the leader's id when there is one leader, -1 on a tie", "id",
               1, CO),
        Column("lowest_uc_ids", "ids of every firm with the lowest capacity-weighted uc, "
               "sorted, as JSON", "ids", 3, CO),
        Column("n_lowest_uc", "number of tied lowest-cost firms", "count", 3, CO),
        Column("lowest_uc_id", "the lowest-cost firm's id when unique, -1 on a tie", "id",
               3, CO),
        Column("price_cv", "unweighted coefficient of variation of prices across firms",
               "ratio", 1, CO),
        Column("uc_cv", "unweighted coefficient of variation of uc across firms", "ratio",
               3, CO),
        Column("price_cv_w", "sales-weighted coefficient of variation of prices (brief "
               "4.4)", "ratio", 2, CO),
        Column("uc_cv_w", "capacity-weighted coefficient of variation of uc (brief 4.4)",
               "ratio", 3, CO),
        Column("leader_is_lowest_cost", "the sets of leaders and of lowest-cost firms "
               "intersect", "bool", 3, CO),
        Column("war_on", "at least one firm in cut mode", "bool", 1, PA),
        Column("n_cutting", "firms in cut mode", "count", 1, PA),
        Column("capacity_total", "capacity of the plants that produced", Q, 3, PR),
        Column("util", "capacity-weighted utilisation", "ratio", 2, DE),
        Column("profit", "sum of profits after depreciation and interest", M, 3, PR),
        Column("gos_total", "operating surplus, revenue - operating cost (overtime premium "
               "included)", M, 3, PR),
        Column("profit_rate", "capital-weighted average of the firms' r_avg", R, 3, PR),
        Column("profit_rate_newest", "capacity-weighted realised rate (profit / purchase "
               "cost) of the newest vintage's plants", R, 3, PR),
        Column("incremental_rate", "net incremental rate: change in profit over last "
               "period's investment; None when that is 0", R, 3, CO),
        Column("incremental_rate_gross", "Shaikh (2016, eq. 7.7): change in gos_total over "
               "last period's invest_total; None when that is 0", R, 3, CO),
        Column("r_new", "profit rate on plants built in the last ENTRY_WINDOW periods", R,
               6, EE),
        Column("p_entry", "entry probability given r_new", "0-1", 6, EE),
        Column("cash", "firms' cash at the end of the period", M, 6, PR),
        Column("debt", "firms' debt at the end of the period", M, 6, PR),
        Column("net_worth", "firms' net worth at the end of the period", M, 6, PR),
        Column("dividends", "dividends paid", M, 3, PR),
        Column("write_offs", "book value written off (retirements and exits)", M, 6, SC),
        Column("invest_total", "investment spending, entrants included", M, 6, IN),
        Column("capacity_retired", "capacity retired at step 4, replacements included", Q,
               4, SC),
        Column("replacements", "plants replaced at step 4", "count", 4, SC),
        Column("entries", "entrants", "count", 6, EE),
        Column("entries_{label}", "entrants with this label", "count", 6, EE),
        Column("exits", "firms that left", "count", 6, EE),
        Column("exits_bankruptcy", "exits on negative net worth, or on negative cash "
               "(CASH_SHORTFALL = bankruptcy)", "count", 6, EE),
        Column("exits_share", "exits on a share below MIN_SHARE", "count", 6, EE),
        Column("exits_non_renewal", "exits on non-renewal of the last plant", "count", 6,
               EE),
        Column("roe_balance", "cash of the rest of the economy", M, 6, PR),
        Column("roe_loans", "loans held by the rest of the economy", M, 6, PR),
        Column("loan_losses", "cumulated debt lost on defaults", M, 6, EE),
        Column("unpaid_bills", "cumulated bills of bankrupt firms borne by the rest of the "
               "economy (CASH_SHORTFALL = bankruptcy)", M, 6, EE),
        Column("n_{label}", "firms with this label at the end of the period", "count", 6,
               CO),
        Column("share_{label}", "shares after step 6 of the firms with this label", "0-1",
               6, CO),
        Column("sales_{label}", "sales of the firms with this label", Q, 2, CO),
        Column("capacity_{label}", "producing capacity of the firms with this label", Q, 3,
               CO),
        Column("profit_rate_{label}", "capital-weighted r_avg of the firms with this label",
               R, 3, CO),
        Column("unit_cost_{label}", "capacity-weighted uc of the producing plants of the "
               "firms with this label", P, 3, CO),
        Column("capacity_{label}_{tech}", "producing capacity of this technique at firms "
               "with this label", Q, 3, CO),
        Column("capacity_{tech}", "producing capacity of this technique", Q, 3, CO),
        Column("capacity_designs", "producing capacity of plants built with designs drawn "
               "under TECH_DRAWS (techniques not on the menu)", Q, 3, CO),
        Column("designs_offered", "designs drawn this period (design events)", "count", 5,
               IN),
        Column("designs_adopted", "designs the hurdle preferred this period (adopt "
               "events); built ones show as orders", "count", 5, IN),
        Column("check_tol", "tolerance of the money checks this period: 1e-9 max(1, "
               "scale)", M, 7, CO),
        Column("money_resid", "firms' cash + rest-of-economy cash - its value at t = 0", M,
               7, CO),
        Column("debt_resid", "firms' debt - loans of the rest of the economy", M, 7, CO),
        Column("nw_resid", "largest residual, over firms, of change in net worth - (profit "
               "- dividends - write-offs + equity in)", M, 7, CO),
        Column("tfm_row_resid", "largest row sum of the flow matrix", M, 7, CO),
        Column("tfm_col_resid", "largest column sum of the flow matrix minus the change in "
               "that sector's cash", M, 7, CO),
        Column("share_resid_demand", "sum of the shares after step 2 - 1", "0-1", 7, CO),
        Column("share_resid_end", "sum of the shares after step 6 - 1", "0-1", 7, CO),
        Column("share_min", "lowest share after steps 2 and 6 (must not be negative)",
               "0-1", 7, CO),
        Column("sales_resid", "sales_total + unmet_total - demand", Q, 7, CO),
        Column("util_max_viol", "firms producing above U_MAX capacity", "count", 7, CO),
        Column("cap_resid", "capacity identity K_t - retired - exit + ordered + entry - "
               "cancelled - K_t+1", Q, 7, CO),
        Column("cap_resid_group", "largest absolute residual of the capacity identity over "
               "the groups", Q, 7, CO),
        Column("floor_viol", "firms whose price is below their floor", "count", 7, CO),
        Column("check_fail", "number of failing checks this period", "count", 7, CO),
    ],
    "groups": [
        RUN_ID,
        Column("t", "period", "period", None, CO),
        Column("group", "label (a key of HURDLE_RULES)", "text", None, CO),
        Column("rule", "rule the label maps to: unit_cost or profit_rate (same under a "
               "label swap)", "text", 0, "parameters.py"),
        Column("n_firms", "firms active at step 1", "count", 1, CO),
        Column("capacity", "capacity used at step 3 (K_g,t)", Q, 3, PR),
        Column("capacity_next", "capacity in operation at the start of next period "
               "(K_g,t+1)", Q, 6, CO),
        Column("sales", "units sold", Q, 2, DE),
        Column("share_demand", "sum of the group's f_i from the replicator (brief: share)",
               "0-1", 2, DE),
        Column("share_end", "the same after exits and entries, entrants included", "0-1",
               6, EE),
        Column("cap_retired", "capacity retired by incumbents at step 4, replacements "
               "included", Q, 4, SC),
        Column("cap_replace", "part of cap_ordered placed at step 4 to replace retired "
               "plants", Q, 4, SC),
        Column("cap_ordered", "capacity ordered by every incumbent at steps 4 and 5, "
               "arriving at t + 1", Q, 5, IN),
        Column("cap_entry", "capacity of entrants' plants, arriving at t + 1", Q, 6, EE),
        Column("cap_exit", "capacity still in operation at firms that leave", Q, 6, EE),
        Column("cap_cancelled", "part of cap_ordered placed by firms that leave, written "
               "off", Q, 6, EE),
        Column("cap_resid", "capacity identity of the group (see macro.cap_resid)", Q, 7,
               CO),
        Column("n_replace", "working plants replaced by the hurdle inequality at step 4 "
               "(retire events with cause replacement)", "count", 4, SC),
        Column("n_entry", "entrants", "count", 6, EE),
        Column("n_exit", "leavers", "count", 6, EE),
        Column("n_exit_bankruptcy", "leavers on negative net worth", "count", 6, EE),
        Column("n_exit_share", "leavers on a share below MIN_SHARE", "count", 6, EE),
        Column("n_exit_non_renewal", "leavers on non-renewal", "count", 6, EE),
        Column("profit", "profit after depreciation and interest", M, 3, PR),
        Column("gos", "operating surplus, revenue - operating cost", M, 3, PR),
        Column("invest_spend", "investment spending, entrants included", M, 6, IN),
        Column("borrow", "sum of the firms' borrow", M, 5, IN),
        Column("cash", "cash at the end of the period", M, 6, PR),
        Column("debt", "debt at the end of the period", M, 6, PR),
        Column("net_worth", "net worth at the end of the period", M, 6, PR),
        Column("hurdle_mean", "mean h weighted by producing capacity; None without "
               "capacity (constant per rule until h evolves)", R, 4, IN),
        Column("ucs_mean", "capacity-weighted ucs of the group's producing plants; its "
               "fall over time is the realised labour saving (gamma); None without "
               "capacity", P, 3, CO),
        Column("kappa_mean", "capacity-weighted kappa of the group's producing plants; its "
               "rise over time is the realised capital using (chi); None without "
               "capacity", KAPPA, 3, CO),
        Column("n_designs_offered", "designs drawn by the group's firms this period "
               "(design events)", "count", 5, IN),
        Column("n_designs_adopted", "designs the group's firms adopted this period (adopt "
               "events)", "count", 5, IN),
        Column("capacity_{tech}", "producing capacity of this technique", Q, 3, CO),
        Column("capacity_designs", "producing capacity of plants built with designs drawn "
               "under TECH_DRAWS", Q, 3, CO),
    ],
    "firms": [
        RUN_ID,
        Column("t", "period", "period", None, CO),
        Column("firm_id", "firm", "id", None, CO),
        Column("type", "label (kept from the template; same as group)", "text", 0, EE),
        Column("group", "label used in the analysis", "text", 0, EE),
        Column("rule", "rule actually applied: unit_cost (Shaikh) or profit_rate "
               "(Okishio)", "text", 0, EE),
        Column("hurdle", "h_i used to choose techniques this period (set at step 4)", R, 4,
               IN),
        Column("born", "period of entry (0 for initial firms)", "period", 6, EE),
        Column("price", "posted price p_i", P, 1, PA),
        Column("p_normal", "anchor p^N_i used by pricing (PRICING_RULE = anchor); None "
               "under the version 2 rules, which have no anchor, and on the entrant's row",
               P, 1, PA),
        Column("p_floor", "the floor pricing used: ucs of the most expensive plant the "
               "firm needs to run (anchor rule, or PRICE_FLOOR = operating_cost), the "
               "best plant's uc (real_competition), (1 + FLOOR_MARKUP) x average uc "
               "(leader_follow); None on the entrant's row", P, 1, PA),
        Column("cutting", "in cut mode this period", "bool", 1, PA),
        Column("low_util", "consecutive periods below U_WAR before this period", "periods",
               1, PA),
        Column("share", "f_i read at step 7 (template column): share_end for a firm that "
               "stays, the share held before leaving for a leaver", "0-1", 6, EE),
        Column("share_demand", "f_i from the replicator, step 2; None on the entrant's row",
               "0-1", 2, DE),
        Column("share_end", "f_i after exits and entries; 0 for a firm that left", "0-1",
               6, EE),
        Column("sales", "units sold x_i", Q, 2, DE),
        Column("util", "utilisation x_i / capacity", "ratio", 2, DE),
        Column("unmet", "demand l_i the firm could not serve", Q, 2, DE),
        Column("capacity", "normal output of the plants it runs this period", Q, 3, PR),
        Column("capacity_next", "capacity of plants in operation and on order after step 6",
               Q, 6, CO),
        Column("output", "units produced, summed over plants (= sales)", Q, 3, PR),
        Column("ucs", "unit operating cost, output-weighted over running plants", P, 3, PR),
        Column("kappa", "capital per unit of normal output, capacity-weighted over plants "
               "in operation", KAPPA, 3, PR),
        Column("uc", "ucs_v + delta kappa_v, capacity-weighted over plants in operation", P,
               3, PR),
        Column("margin", "price - uc", P, 3, CO),
        Column("revenue", "price x sales", M, 3, PR),
        Column("op_cost", "wages and materials, overtime premium included", M, 3, PR),
        Column("gos", "revenue - op_cost", M, 3, PR),
        Column("depreciation", "depreciation summed over plants", M, 3, PR),
        Column("interest", "rho x debt at the start of the period", M, 3, PR),
        Column("profit", "profit after depreciation and interest", M, 3, PR),
        Column("dividends", "PAYOUT x max(0, profit)", M, 3, PR),
        Column("r_avg", "profit / k_cost", R, 3, PR),
        Column("r_newest", "(price - uc_v) / kappa_v at normal output on the plants in "
               "operation with the highest vintage, capacity-weighted", R, 3, PR),
        Column("r_best", "best profit rate on the menu at the firm's price, before the zero "
               "floor (Okishio's h)", R, 4, IN),
        Column("n_plants", "plants in operation this period", "count", 3, PR),
        Column("oldest_vintage", "lowest vintage of the plants in operation", "period", 3,
               PR),
        Column("newest_vintage", "highest vintage of the plants in operation", "period", 3,
               PR),
        Column("ucs_spread", "max / min ucs over running plants", "ratio", 3, PR),
        Column("newest_technique", "technique of the newest plant held, orders included",
               "id", 6, CO),
        Column("cap_retired", "capacity retired at step 4, replacements included", Q, 4, SC),
        Column("write_off", "book value written off (retirements and exit)", M, 6, SC),
        Column("exp_sales", "expected sales of the investment rule; None for entrants and "
               "non-renewal", Q, 5, IN),
        Column("cap_desired", "desired capacity; None as exp_sales", Q, 5, IN),
        Column("cap_ordered", "capacity ordered at steps 4 and 5, replacements included", Q,
               5, IN),
        Column("cap_replace", "part of cap_ordered replacing retired plants (step 4)", Q, 4,
               SC),
        Column("tech_new", "techniques of the plants ordered, joined by +; empty if none",
               "id", 5, IN),
        Column("tech_other", "technique the other rule would pick at the same price", "id",
               5, CO),
        Column("invest_spend", "spending on plants, replacements included", M, 5, IN),
        Column("borrow", "debt after step 5 - debt at the start of the period", M, 5, IN),
        Column("borrow_plants", "debt taken at steps 4 and 5 to pay for plants", M, 5, IN),
        Column("cash", "cash M_i at the end of the period", M, 6, PR),
        Column("debt", "debt B_i at the end of the period", M, 6, PR),
        Column("retained_earnings", "profit - dividends since birth, less spending on "
               "plants: the funds INVESTMENT_RULE = retained_earnings spends", M, 5, IN),
        Column("k_book", "book value of plants in operation and on order", M, 6, PR),
        Column("k_cost", "sum of kappa_v x capacity_v over the plants that produced", M, 3,
               PR),
        Column("net_worth", "cash + k_book - debt", M, 6, PR),
        Column("n_known", "techniques the firm can build: the menu plus its adopted "
               "designs (TECH_DRAWS)", "count", 5, IN),
        Column("exited", "left at step 6", "bool", 6, EE),
        Column("exit_cause", "bankruptcy, share or non-renewal; empty if the firm stays",
               "text", 6, EE),
    ],
    "plants": [
        RUN_ID,
        Column("plant_id", "plant", "id", None, CO),
        Column("ucs", "unit operating cost ucs_v", P, None, IN),
        Column("kappa", "capital per unit of normal output kappa_v", KAPPA, None, IN),
        Column("capacity", "normal output", Q, None, IN),
        Column("vintage", "first period in which the plant produces", "period", None, IN),
        Column("initial", "part of the initial endowment", "bool", 0, "model.py"),
        Column("age", "periods of operation completed, this one included", "periods", 3,
               PR),
        Column("output", "output in merit order", Q, 3, PR),
        Column("overtime_output", "part of output above normal capacity", Q, 3, PR),
        Column("profit", "(price - ucs) output - premium - depreciation", M, 3, PR),
        Column("lifetime_profit", "profit cumulated since arrival", M, 3, PR),
        Column("tech", "technique", "id", None, IN),
        Column("k_book", "book value after step 6 (0 once written off)", M, 6, PR),
        Column("below_cost", "consecutive periods with price below the plant's scrap cost: "
               "ucs_v, or uc_v with SCRAP_COST = unit_cost", "periods", 4, SC),
        Column("periods_idle", "consecutive periods the firm did not need the plant "
               "(IDLE_SCRAPPING)", "periods", 4, SC),
        Column("wear", "output so far in periods of normal output, sum of x_v / capacity; "
               "the plant's life under DEPRECIATION = use", "periods", 3, PR),
        Column("t", "period", "period", None, CO),
        Column("firm_id", "owner", "id", None, CO),
        Column("firm_type", "owner's label (kept from the template; same as group)",
               "text", None, CO),
        Column("group", "owner's label", "text", None, CO),
        Column("uc", "ucs_v + delta kappa_v", P, None, CO),
        Column("running", "ran this period (output > 0)", "bool", 3, PR),
        Column("r_plant", "(price - uc_v) / kappa_v at normal output", R, 3, CO),
        Column("profit_rate", "realised rate, profit / purchase cost", R, 3, CO),
        Column("retired", "retired at step 4", "bool", 4, SC),
        Column("retire_cause", "age, obsolescence, idle, replacement or exit; empty "
               "otherwise", "text", 6, SC),
        Column("exited_with_firm", "its owner left at step 6", "bool", 6, EE),
        Column("write_off", "book value written off this period", M, 6, SC),
    ],
    "events": [
        RUN_ID,
        Column("t", "period", "period", None, CO),
        Column("step", "step of the period at which the event happens", "step", None, CO),
        Column("event", "order, retire, exit, default, unpaid_bills, cancel, entry, "
               "design, adopt, public, war_start, war_end, cut_start, cut_end", "text",
               None, CO),
        Column("firm_id", "firm; -1 for an industry event", "id", None, CO),
        Column("plant_id", "plant; -1 if none", "id", None, CO),
        Column("group", "firm's label; empty for an industry event", "text", None, CO),
        Column("rule", "firm's rule; empty for an industry event", "text", None, CO),
        Column("hurdle", "firm's h when the event happens", R, None, IN),
        Column("tech", "technique of the plant; design and adopt: the design", "id", None,
               CO),
        Column("other_tech", "order: technique the other rule would pick; design and "
               "adopt: the reference technique the design was drawn from", "id", 5, CO),
        Column("capacity", "capacity of the plant, or capacity left at exit", Q, None, CO),
        Column("value", "order: cost; retire and cancel: book value written off; exit: net "
               "worth; default: unpaid debt; unpaid_bills: the bills left unpaid; entry: "
               "price; design and adopt: the design's unit cost; public: the period the "
               "design became known to every firm; war: price_avg; cut: price",
               "as defined", None, CO),
        Column("cause", "order: expansion, replacement, entry; retire: age, obsolescence, "
               "idle, replacement, exit; exit: bankruptcy, share, non-renewal; entry: "
               "inherited, mutated; design and adopt: the design's zone at the firm's "
               "price, both (both rules adopt it), unit_cost (only the unit-cost rule: "
               "the conflict zone), profit_rate (only the profit-rate rule) or none; "
               "war_end and cut_end: censored or exit", "text", None, CO),
        Column("other_id", "entry: parent firm; war: episode number; -1 otherwise", "id",
               None, CO),
    ],
    "flows": [
        RUN_ID,
        Column("t", "period", "period", None, CO),
        Column("item", "sales, wages and materials, interest, dividends, plants, loans, "
               "equity", "text", None, "markets.payments"),
        Column("firms", "net flow to all firms (+ receipt, - payment)", M, None,
               "markets.payments"),
        Column("roe", "net flow to the rest of the economy", M, None, "markets.payments"),
    ],
}


def parameter_columns(config) -> dict[str, str]:
    """Upper-case parameter -> its column in `runs` (lower case, or RUN_ALIASES)."""
    names = sorted(k for k in vars(config) if k.isupper())
    return {k: RUN_ALIASES.get(k, k.lower()) for k in names}


def _expand(name: str, values: dict[str, list[str]]) -> list[str]:
    names = [name]
    for key, options in values.items():
        if key in name:
            names = [n.replace(key, v) for n in names for v in options]
    return names


def columns(table: str, config) -> list[str]:
    """Column names of `table` for a configuration, templates expanded."""
    values = {
        "{label}": sorted(config.HURDLE_RULES),
        "{tech}": list(config.SHAIKH_PLANTS),
        "{parameter}": [c for k, c in parameter_columns(config).items()
                        if k not in RUN_ALIASES],
    }
    return [n for column in SCHEMA[table] for n in _expand(column.name, values)]
