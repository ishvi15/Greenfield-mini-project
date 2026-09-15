CREATE DATABASE IF NOT EXISTS hr_analytics_warehouse;
USE hr_analytics_warehouse;

CREATE TABLE IF NOT EXISTS dim_department (
    department_sk INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL,
    start_date DATE,
    end_date DATE,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_employee (
    employee_sk INT AUTO_INCREMENT PRIMARY KEY,
    business_key INT NOT NULL,
    employee_name VARCHAR(200) NOT NULL,
    department VARCHAR(100) NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    salary DECIMAL(12,2) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS dim_project (
    project_sk INT AUTO_INCREMENT PRIMARY KEY,
    project_id INT NOT NULL,
    project_name VARCHAR(200) NOT NULL,
    department VARCHAR(100),
    priority_level VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_sk INT AUTO_INCREMENT PRIMARY KEY,
    full_date DATE NOT NULL,
    year_num INT NOT NULL,
    month_num INT NOT NULL,
    quarter_num INT NOT NULL,
    is_current_year BOOLEAN DEFAULT FALSE,
    UNIQUE KEY uq_dim_date_full_date (full_date)
);

CREATE TABLE IF NOT EXISTS fact_performance_reviews (
    fact_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    employee_sk INT,
    project_sk INT,
    date_sk INT,
    review_id INT,
    performance_score DECIMAL(5,2),
    department VARCHAR(100),
    rating VARCHAR(50),
    review_year INT,
    employee_name VARCHAR(200),
    department_name VARCHAR(100),
    DENSE_RANK_ANALYSIS INT,
    FOREIGN KEY (employee_sk) REFERENCES dim_employee(employee_sk),
    FOREIGN KEY (project_sk) REFERENCES dim_project(project_sk),
    FOREIGN KEY (date_sk) REFERENCES dim_date(date_sk)
);
