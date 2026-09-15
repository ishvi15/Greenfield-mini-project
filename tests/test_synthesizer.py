import pandas as pd

from src.hr_analytics.data_synthesizer import EmployeeHistorySynthesizer


def test_generate_employee_history_has_expected_columns():
    synthesizer = EmployeeHistorySynthesizer()
    df = synthesizer.generate_employee_history(total_employees=25)

    assert isinstance(df, pd.DataFrame)
    assert {"employee_id", "department", "review_date", "performance_score"}.issubset(df.columns)
    assert len(df) > 0
    assert df["performance_score"].between(0, 100).all()


def test_generate_employee_history_uses_real_dataset_rows():
    synthesizer = EmployeeHistorySynthesizer()
    df = synthesizer.generate_employee_history(total_employees=10)

    assert len(df) == 10
    assert df["employee_id"].nunique() == 10
    assert df["department"].notna().all()


def test_generate_scd2_employee_history_tracks_versions():
    synthesizer = EmployeeHistorySynthesizer()
    df = synthesizer.generate_scd2_employee_history(total_employees=25)

    required = {"employee_id", "department", "role_name", "salary", "effective_start_date", "effective_end_date", "is_current"}
    assert required.issubset(df.columns)
    assert len(df) > 0
    assert df["is_current"].isin([True, False]).all()
    assert df[df["is_current"] == True].shape[0] > 0
