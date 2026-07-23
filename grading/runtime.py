from __future__ import annotations

import math
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from scipy import stats

from lab_utils import clean_flights, load_flights


def close(a, b, atol=1e-6, rtol=1e-5) -> bool:
    try:
        return bool(np.isclose(float(a), float(b), atol=atol, rtol=rtol, equal_nan=False))
    except Exception:
        return False


def valid_identity(ns: dict) -> bool:
    bad = {"", "REPLACE WITH YOUR FULL NAME", "REPLACE WITH YOUR GITHUB USERNAME", None}
    return ns.get("student_name") not in bad and ns.get("github_username") not in bad


def figure_ok(obj: Any, minimum_traces: int = 1) -> bool:
    return hasattr(obj, "data") and len(obj.data) >= minimum_traces


def text_ok(value: Any, minimum: int) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum and "TODO" not in value.upper() and "REPLACE" not in value.upper()


def check(results, name: str, points: int, condition: bool, feedback: str):
    earned = points if bool(condition) else 0
    results.append({"task": name, "earned": earned, "possible": points, "feedback": "Passed" if condition else feedback})


def grade_day1(ns: dict) -> list[dict]:
    r = []
    check(r, "Task 1: course variables", 10,
          ns.get("course_title") == "Python Data Analysis" and ns.get("training_days") == 5 and ns.get("training_is_hands_on") is True,
          "Set the three required values exactly.")
    check(r, "Task 2: average delay", 10, close(ns.get("average_delay"), np.mean([0,12,45,-5,30])), "Calculate the arithmetic mean.")
    check(r, "Task 3: airline dictionary", 10,
          ns.get("airline_lookup") == {"AA":"American","DL":"Delta","WN":"Southwest"},
          "Build the exact code-to-name dictionary.")
    fn = ns.get("classify_delay")
    fn_ok = callable(fn)
    if fn_ok:
        try:
            fn_ok = [fn(x) for x in [-4, 0, 1, 15, 16, 60]] == ["Early/On time","Early/On time","Minor delay","Minor delay","Major delay","Major delay"]
        except Exception:
            fn_ok = False
    check(r, "Task 4: delay classifier", 10, fn_ok, "Implement all three branches and boundary values.")
    arr = ns.get("delay_array"); pos = ns.get("positive_delays")
    check(r, "Task 5: NumPy filtering", 10,
          isinstance(arr, np.ndarray) and isinstance(pos, np.ndarray) and np.array_equal(pos, np.array([12,45,30])),
          "Create a NumPy array and use a Boolean mask.")
    expected_df = pd.DataFrame({"flight":["AA101","DL202","WN303","AA404","DL505"],"airline":["AA","DL","WN","AA","DL"],"delay":[0,18,45,-7,12],"distance":[950,1200,620,430,1500]})
    fdf = ns.get("flights_df")
    check(r, "Task 6: DataFrame", 10, isinstance(fdf,pd.DataFrame) and fdf.equals(expected_df), "Construct the DataFrame from flight_data.")
    delayed = ns.get("delayed_flights")
    check(r, "Task 7: filter", 10,
          isinstance(delayed,pd.DataFrame) and list(delayed["flight"]) == ["DL202","WN303"],
          "Filter delay > 15.")
    grouped = ns.get("airline_mean_delay")
    expected_grouped = expected_df.groupby("airline")["delay"].mean().sort_values(ascending=False)
    check(r, "Task 8: grouped mean", 10,
          isinstance(grouped,pd.Series) and grouped.index.tolist()==expected_grouped.index.tolist() and np.allclose(grouped.values, expected_grouped.values),
          "Group by airline, average delay and sort descending.")
    enriched = ns.get("flights_enriched")
    expected_cats = ["Early/On time","Major delay","Major delay","Early/On time","Minor delay"]
    check(r, "Task 9: analytical column", 10,
          isinstance(enriched,pd.DataFrame) and "delay_category" in enriched and enriched["delay_category"].tolist()==expected_cats,
          "Create a copy and apply classify_delay.")
    check(r, "Task 10: Plotly chart", 10, figure_ok(ns.get("fig_airline_delay")), "Create a non-empty Plotly figure.")
    return r


def grade_day2(ns: dict) -> list[dict]:
    r=[]; raw=ns.get("df_raw")
    if not isinstance(raw,pd.DataFrame):
        raw=load_flights()
    check(r,"Task 1: shape",10, ns.get("dataset_shape")==raw.shape,"Store df_raw.shape.")
    check(r,"Task 2: columns",10, ns.get("column_names")==list(raw.columns),"Convert df_raw.columns to a list.")
    ms=ns.get("missing_summary"); exp=raw.isna().sum().sort_values(ascending=False)
    check(r,"Task 3: missing values",10,isinstance(ms,pd.Series) and ms.equals(exp),"Count missing values and sort descending.")
    check(r,"Task 4: duplicates",10,ns.get("duplicate_count")==int(raw.duplicated().sum()),"Use duplicated().sum().")
    clean=ns.get("df_clean"); base=raw.drop_duplicates().copy()
    check(r,"Task 5: remove duplicates",10,isinstance(clean,pd.DataFrame) and len(clean)==len(base) and clean.duplicated().sum()==0,"Remove exact duplicates.")
    date_ok=isinstance(clean,pd.DataFrame) and "FLIGHT_DATE" in clean and pd.api.types.is_datetime64_any_dtype(clean["FLIGHT_DATE"])
    if date_ok:
        expected_date=pd.to_datetime(dict(year=base.YEAR,month=base.MONTH,day=base.DAY),errors='coerce')
        date_ok=clean["FLIGHT_DATE"].reset_index(drop=True).equals(expected_date.reset_index(drop=True))
    check(r,"Task 6: flight date",10,date_ok,"Create a correct datetime FLIGHT_DATE.")
    delay_ok=isinstance(clean,pd.DataFrame) and "DELAYED_15" in clean
    if delay_ok:
        delay_ok=clean["DELAYED_15"].astype(bool).reset_index(drop=True).equals(base["DEPARTURE_DELAY"].gt(15).fillna(False).reset_index(drop=True))
    check(r,"Task 7: delay indicator",10,delay_ok,"Create DELAYED_15 from DEPARTURE_DELAY > 15.")
    label_ok=isinstance(clean,pd.DataFrame) and "CANCELLATION_REASON_LABEL" in clean
    if label_ok:
        m={"A":"Airline/Carrier","B":"Weather","C":"National Air System","D":"Security"}
        ex=base["CANCELLATION_REASON"].map(m).fillna("Not cancelled")
        label_ok=clean["CANCELLATION_REASON_LABEL"].reset_index(drop=True).equals(ex.reset_index(drop=True))
    check(r,"Task 8: cancellation labels",10,label_ok,"Map A–D and fill missing with Not cancelled.")
    rep=ns.get("cleaning_report",{})
    rep_ok=isinstance(rep,dict) and rep.get("raw_rows")==len(raw) and rep.get("duplicate_rows_removed")==raw.duplicated().sum() and rep.get("clean_rows")==len(base)
    if isinstance(clean,pd.DataFrame) and "DELAYED_15" in clean:
        rep_ok=rep_ok and rep.get("cancelled_flights")==int(clean["CANCELLED"].sum()) and rep.get("delayed_15_flights")==int(clean["DELAYED_15"].sum())
    check(r,"Task 9: cleaning report",10,rep_ok,"Complete every report value from the data.")
    path=Path("outputs/day2_clean_flights.csv")
    export_ok=bool(ns.get("export_complete")) and path.exists()
    if export_ok:
        try: export_ok=len(pd.read_csv(path))==len(base)
        except Exception: export_ok=False
    check(r,"Task 10: export",10,export_ok,"Export df_clean without the index and set export_complete=True.")
    return r


def expected_day3(df):
    monthly=df.groupby("MONTH").size().sort_index()
    summary=df.groupby("AIRLINE").agg(
        flights=("AIRLINE","size"),
        mean_departure_delay=("DEPARTURE_DELAY","mean"),
        delayed_rate=("DELAYED_15","mean"),
        cancellation_rate=("CANCELLED","mean"),
    )
    routes=df["ROUTE"].value_counts().head(10)
    hour=(df.dropna(subset=["SCHEDULED_HOUR"]).groupby("SCHEDULED_HOUR").agg(
        flights=("AIRLINE","size"), mean_delay=("DEPARTURE_DELAY","mean"), delayed_rate=("DELAYED_15","mean")
    ).sort_index())
    route_perf=df.groupby("ROUTE").agg(flights=("ROUTE","size"),mean_delay=("DEPARTURE_DELAY","mean"),delayed_rate=("DELAYED_15","mean"))
    route_perf=route_perf[route_perf.flights>=20]
    return monthly,summary,routes,hour,route_perf


def frame_close(a,b,cols=None):
    if not isinstance(a,pd.DataFrame) or not isinstance(b,pd.DataFrame): return False
    try:
        aa=a.sort_index(); bb=b.sort_index()
        if cols: aa=aa[cols]; bb=bb[cols]
        return aa.index.tolist()==bb.index.tolist() and aa.columns.tolist()==bb.columns.tolist() and np.allclose(aa.to_numpy(float),bb.to_numpy(float),equal_nan=True)
    except Exception: return False


def series_close(a,b):
    try:
        return isinstance(a,pd.Series) and a.index.tolist()==b.index.tolist() and np.allclose(a.to_numpy(float),b.to_numpy(float),equal_nan=True)
    except Exception: return False


def grade_day3(ns):
    r=[]; df=ns.get("df");
    if not isinstance(df,pd.DataFrame): df=clean_flights(load_flights())
    monthly,summary,routes,hour,route_perf=expected_day3(df)
    check(r,"Task 1: monthly volume",10,series_close(ns.get("monthly_volume"),monthly),"Count by month and sort index.")
    check(r,"Task 2: airline summary",15,frame_close(ns.get("airline_summary"),summary),"Create the four specified airline metrics.")
    tr=ns.get("top_routes")
    check(r,"Task 3: top routes",10,isinstance(tr,pd.Series) and tr.equals(routes),"Use ROUTE.value_counts().head(10).")
    check(r,"Task 4: hourly profile",15,frame_close(ns.get("delay_by_hour"),hour),"Create the three hourly metrics.")
    check(r,"Task 5: monthly chart",10,figure_ok(ns.get("fig_monthly_volume")),"Create a non-empty Plotly line chart.")
    check(r,"Task 6: airline chart",10,figure_ok(ns.get("fig_airline_delay")),"Create a non-empty Plotly bar chart.")
    check(r,"Task 7: distribution",10,figure_ok(ns.get("fig_delay_distribution")),"Create a non-empty histogram.")
    rp=ns.get("route_performance")
    check(r,"Task 8: route analysis",10,frame_close(rp,route_perf) and figure_ok(ns.get("fig_route_performance")),"Calculate route performance and create the scatter plot.")
    check(r,"Task 9: findings",5,text_ok(ns.get("eda_findings"),180),"Write at least 180 characters with evidence.")
    p=Path("outputs/day3_airline_summary.csv")
    export_ok=bool(ns.get("export_complete")) and p.exists()
    if export_ok:
        try: export_ok=len(pd.read_csv(p))==len(summary)
        except Exception: export_ok=False
    check(r,"Task 10: export",5,export_ok,"Export the airline summary and set export_complete=True.")
    return r


def grade_day4(ns):
    r=[]; df=clean_flights(load_flights()); adf=df.loc[(df.CANCELLED==0)&df.ARRIVAL_DELAY.notna()].copy(); arr=adf.ARRIVAL_DELAY.dropna()
    mean=arr.mean(); sem=stats.sem(arr); ci=stats.t.interval(.95,df=len(arr)-1,loc=mean,scale=sem)
    prop=(arr>15).mean(); se=math.sqrt(prop*(1-prop)/len(arr)); pci=(prop-1.96*se,prop+1.96*se)
    check(r,"Task 1: mean",10,close(ns.get("mean_arrival_delay"),mean),"Calculate ARRIVAL_DELAY.mean().")
    val=ns.get("ci_mean_arrival_delay"); check(r,"Task 2: mean CI",15,isinstance(val,(tuple,list,np.ndarray)) and len(val)==2 and np.allclose(val,ci,rtol=1e-4),"Use a 95% t interval.")
    v=ns.get("ci_arrival_delayed_proportion")
    check(r,"Task 3: proportion CI",10,close(ns.get("arrival_delayed_proportion"),prop) and isinstance(v,(tuple,list,np.ndarray)) and np.allclose(v,pci,rtol=1e-4),"Calculate the proportion and normal interval.")
    top=adf.AIRLINE.value_counts().head(2).index.tolist(); a=adf.loc[adf.AIRLINE==top[0],"ARRIVAL_DELAY"].dropna(); b=adf.loc[adf.AIRLINE==top[1],"ARRIVAL_DELAY"].dropna(); tres=stats.ttest_ind(a,b,equal_var=False)
    check(r,"Task 4: Welch t-test",15,close(ns.get("t_statistic"),tres.statistic,rtol=1e-4) and close(ns.get("p_value_ttest"),tres.pvalue,rtol=1e-4),"Use stats.ttest_ind(..., equal_var=False).")
    pooled=math.sqrt(((len(a)-1)*a.var(ddof=1)+(len(b)-1)*b.var(ddof=1))/(len(a)+len(b)-2)); d=(a.mean()-b.mean())/pooled
    check(r,"Task 5: Cohen d",10,close(ns.get("cohens_d"),d,rtol=1e-4),"Use pooled standard deviation.")
    top5=df.AIRLINE.value_counts().head(5).index; cdf=df[df.AIRLINE.isin(top5)]; table=pd.crosstab(cdf.AIRLINE,cdf.DELAYED_15)
    ct=ns.get("contingency_table"); check(r,"Task 6: contingency",10,isinstance(ct,pd.DataFrame) and ct.equals(table),"Create the AIRLINE by DELAYED_15 crosstab.")
    chi2,p,_,_=stats.chi2_contingency(table); n=table.to_numpy().sum(); vcr=math.sqrt(chi2/(n*min(table.shape[0]-1,table.shape[1]-1)))
    check(r,"Task 7: chi-square and V",15,close(ns.get("chi2_statistic"),chi2,rtol=1e-4) and close(ns.get("p_value_chi2"),p,rtol=1e-4) and close(ns.get("cramers_v"),vcr,rtol=1e-4),"Calculate chi-square and Cramér's V.")
    corr=adf[["DEPARTURE_DELAY","ARRIVAL_DELAY"]].corr().iloc[0,1]
    check(r,"Task 8: correlation",5,close(ns.get("delay_correlation"),corr,rtol=1e-4),"Calculate Pearson correlation.")
    rng=np.random.default_rng(42); vals=arr.to_numpy(); meds=np.array([np.median(rng.choice(vals,size=len(vals),replace=True)) for _ in range(1000)]); bci=np.percentile(meds,[2.5,97.5]); bv=ns.get("bootstrap_median_ci")
    check(r,"Task 9: bootstrap",5,isinstance(bv,(tuple,list,np.ndarray)) and np.allclose(bv,bci,rtol=1e-4),"Use seed 42, 1000 bootstrap medians and percentile endpoints.")
    check(r,"Task 10: conclusion",5,text_ok(ns.get("statistical_conclusion"),160),"Write a substantive interpretation.")
    return r


def grade_day5(ns):
    r=[]
    required=["MONTH","DAY_OF_WEEK","AIRLINE","ORIGIN_AIRPORT","DESTINATION_AIRPORT","SCHEDULED_HOUR","DISTANCE"]
    features=ns.get("feature_columns")
    X=ns.get("X"); y=ns.get("y")
    t1=isinstance(features,list) and features==required and isinstance(X,pd.DataFrame) and isinstance(y,(pd.Series,np.ndarray)) and list(X.columns)==required and len(X)==len(y)
    check(r,"Task 1: predictors and target",10,t1,"Use the exact seven pre-departure features and Boolean target.")
    Xtr,Xte,ytr,yte=[ns.get(k) for k in ["X_train","X_test","y_train","y_test"]]
    split_ok=all(v is not None for v in [Xtr,Xte,ytr,yte]) and len(Xte)>0 and abs(len(Xte)/len(X)-.25)<.02 and abs(float(pd.Series(ytr).mean())-float(pd.Series(y).mean()))<.02
    check(r,"Task 2: split",10,split_ok,"Use test_size=.25, random_state=42 and stratify=y.")
    pre=ns.get("preprocessor"); cats=ns.get("categorical_features"); nums=ns.get("numeric_features")
    check(r,"Task 3: preprocessor",15,pre is not None and cats==["AIRLINE","ORIGIN_AIRPORT","DESTINATION_AIRPORT"] and nums==["MONTH","DAY_OF_WEEK","SCHEDULED_HOUR","DISTANCE"],"Build the categorical and numerical preprocessing pipelines.")
    pipe=ns.get("model_pipeline")
    check(r,"Task 4: model pipeline",10,pipe is not None and hasattr(pipe,"fit") and hasattr(pipe,"predict"),"Create a fitted-capable sklearn Pipeline.")
    pred=ns.get("y_pred"); prob=ns.get("y_probability")
    pred_ok=pred is not None and prob is not None and yte is not None and len(pred)==len(yte) and len(prob)==len(yte) and np.all((np.asarray(prob)>=0)&(np.asarray(prob)<=1))
    check(r,"Task 5: predictions",10,pred_ok,"Fit the pipeline and create class and probability predictions.")
    metrics=ns.get("model_metrics",{}); cm=ns.get("confusion_matrix_df")
    metric_ok=False
    if pred_ok and isinstance(metrics,dict):
        try:
            calc={"accuracy":__import__('sklearn.metrics').metrics.accuracy_score(yte,pred),"precision":__import__('sklearn.metrics').metrics.precision_score(yte,pred,zero_division=0),"recall":__import__('sklearn.metrics').metrics.recall_score(yte,pred,zero_division=0),"f1":__import__('sklearn.metrics').metrics.f1_score(yte,pred,zero_division=0),"roc_auc":__import__('sklearn.metrics').metrics.roc_auc_score(yte,prob)}
            metric_ok=all(close(metrics.get(k),v,rtol=1e-4) for k,v in calc.items()) and isinstance(cm,pd.DataFrame) and cm.shape==(2,2)
        except Exception: metric_ok=False
    check(r,"Task 6: metrics",15,metric_ok,"Calculate five metrics and a 2×2 confusion matrix DataFrame.")
    cv=ns.get("cv_roc_auc_scores")
    check(r,"Task 7: cross-validation",10,isinstance(cv,np.ndarray) and len(cv)==3 and np.all((cv>=0)&(cv<=1)),"Run three-fold ROC AUC cross-validation.")
    coef=ns.get("coefficient_table"); top=ns.get("top_model_coefficients")
    coef_ok=isinstance(coef,pd.DataFrame) and set(["feature","coefficient"]).issubset(coef.columns) and isinstance(top,pd.DataFrame) and len(top)==30
    check(r,"Task 8: coefficients",5,coef_ok,"Create the full coefficient table and retain 15 largest plus 15 smallest.")
    th=ns.get("threshold_results"); bt=ns.get("best_threshold")
    th_ok=isinstance(th,pd.DataFrame) and set(["threshold","precision","recall","f1"]).issubset(th.columns) and len(th)==13 and bt in th.threshold.to_list()
    if th_ok: th_ok=close(th.loc[th.f1.idxmax(),"threshold"],bt)
    check(r,"Task 9: threshold",10,th_ok,"Evaluate 0.20–0.80 by 0.05 and choose maximum F1.")
    gp=ns.get("airline_model_performance")
    group_ok=isinstance(gp,pd.DataFrame) and set(["flights","observed_delay_rate","recall"]).issubset(gp.columns)
    check(r,"Task 10: responsible recommendation",5,group_ok and text_ok(ns.get("model_recommendation"),220),"Create group metrics and write at least 220 characters.")
    return r


def grade_namespace(namespace: dict, day: int) -> dict:
    graders={1:grade_day1,2:grade_day2,3:grade_day3,4:grade_day4,5:grade_day5}
    results=graders[day](namespace)
    earned=sum(x["earned"] for x in results); possible=sum(x["possible"] for x in results)
    return {"day":day,"earned":earned,"possible":possible,"percentage":round(100*earned/possible,2),"tasks":results,"identity_complete":valid_identity(namespace)}
