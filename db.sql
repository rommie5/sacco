
-- SACCO App Database Schema (PostgreSQL)

-- USERS & MEMBERSHIP MANAGEMENT
CREATE TABLE users_user (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_admin BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users_memberprofile (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users_user(id) ON DELETE CASCADE,
    national_id VARCHAR(50) UNIQUE,
    phone_number VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    membership_status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users_document (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES users_memberprofile(id) ON DELETE CASCADE,
    doc_type VARCHAR(50),
    file_path VARCHAR(255),
    verified BOOLEAN DEFAULT FALSE,
    uploaded_at TIMESTAMP DEFAULT NOW()
);

-- SAVINGS & CONTRIBUTIONS
CREATE TABLE savings_account (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES users_memberprofile(id) ON DELETE CASCADE,
    account_number VARCHAR(20) UNIQUE NOT NULL,
    balance NUMERIC(12,2) DEFAULT 0.00,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE savings_contribution (
    id SERIAL PRIMARY KEY,
    account_id INT REFERENCES savings_account(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    payment_method VARCHAR(50),
    transaction_ref VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW()
);

-- TRANSACTIONS & PAYMENT
CREATE TABLE transactions_transaction (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES users_memberprofile(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    transaction_type VARCHAR(50),
    gateway_ref VARCHAR(100),
    status VARCHAR(30) DEFAULT 'Initiated',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE transactions_ledgerentry (
    id SERIAL PRIMARY KEY,
    transaction_id INT REFERENCES transactions_transaction(id) ON DELETE CASCADE,
    debit_account VARCHAR(50),
    credit_account VARCHAR(50),
    amount NUMERIC(12,2),
    narration TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- LOANS
CREATE TABLE loans_loanapplication (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES users_memberprofile(id) ON DELETE CASCADE,
    amount NUMERIC(12,2) NOT NULL,
    interest_rate NUMERIC(5,2) DEFAULT 10.00,
    tenure_months INT,
    purpose TEXT,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE loans_loanapproval (
    id SERIAL PRIMARY KEY,
    loan_id INT REFERENCES loans_loanapplication(id) ON DELETE CASCADE,
    approved_by INT REFERENCES users_user(id),
    approval_date TIMESTAMP DEFAULT NOW(),
    comments TEXT
);

CREATE TABLE loans_loanrepayment (
    id SERIAL PRIMARY KEY,
    loan_id INT REFERENCES loans_loanapplication(id) ON DELETE CASCADE,
    amount_paid NUMERIC(12,2),
    payment_date TIMESTAMP DEFAULT NOW(),
    transaction_id INT REFERENCES transactions_transaction(id),
    balance_remaining NUMERIC(12,2)
);

-- REPORTS & REGULATORY
CREATE TABLE reports_regulatoryreport (
    id SERIAL PRIMARY KEY,
    report_type VARCHAR(100),
    generated_by INT REFERENCES users_user(id),
    generated_on TIMESTAMP DEFAULT NOW(),
    validated BOOLEAN DEFAULT FALSE,
    submission_status VARCHAR(50) DEFAULT 'Draft',
    regulator_feedback TEXT
);

-- AUDIT LOGS
CREATE TABLE audit_auditlog (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users_user(id),
    action VARCHAR(255),
    entity VARCHAR(100),
    entity_id INT,
    timestamp TIMESTAMP DEFAULT NOW(),
    ip_address VARCHAR(50)
);

-- NOTIFICATIONS
CREATE TABLE notifications_notification (
    id SERIAL PRIMARY KEY,
    member_id INT REFERENCES users_memberprofile(id) ON DELETE CASCADE,
    message TEXT,
    notification_type VARCHAR(50),
    sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
