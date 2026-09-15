DELIMITER //

CREATE PROCEDURE IF NOT EXISTS sp_load_dim_employee()
BEGIN
    INSERT INTO hr_analytics_warehouse.dim_employee (
        business_key, employee_name, department, role_name, salary, start_date, end_date, is_current
    )
    SELECT
        employee_id,
        employee_name,
        department,
        role,
        salary,
        CAST(start_date AS DATE),
        CAST(end_date AS DATE),
        is_current
    FROM hr_analytics_oltp.employee_history_stage;
END //

CREATE PROCEDURE IF NOT EXISTS sp_load_fact_reviews()
BEGIN
    INSERT INTO hr_analytics_warehouse.fact_performance_reviews (
        employee_sk, project_sk, date_sk, review_id, performance_score, department, rating, review_year, employee_name, department_name
    )
    SELECT
        NULL,
        NULL,
        NULL,
        review_id,
        performance_score,
        department,
        CASE
            WHEN performance_score >= 90 THEN 'Excellent'
            WHEN performance_score >= 75 THEN 'Good'
            ELSE 'Needs Improvement'
        END,
        YEAR(review_date),
        NULL,
        department
    FROM hr_analytics_oltp.reviews;
END //

CREATE PROCEDURE IF NOT EXISTS sp_scd2_department_update(
    IN p_employee_id INT,
    IN p_new_department VARCHAR(100),
    IN p_new_role VARCHAR(100),
    IN p_new_salary DECIMAL(12,2),
    IN p_effective_date DATE
)
BEGIN
    UPDATE hr_analytics_warehouse.dim_employee
    SET end_date = DATE_SUB(p_effective_date, INTERVAL 1 DAY),
        is_current = FALSE
    WHERE business_key = p_employee_id AND is_current = TRUE;

    INSERT INTO hr_analytics_warehouse.dim_employee (
        business_key, employee_name, department, role_name, salary, start_date, end_date, is_current
    )
    SELECT
        employee_id,
        employee_name,
        p_new_department,
        p_new_role,
        p_new_salary,
        p_effective_date,
        '9999-12-31',
        TRUE
    FROM hr_analytics_oltp.employee_history_stage
    WHERE employee_id = p_employee_id
    LIMIT 1;
END //

DELIMITER ;
