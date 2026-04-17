-- Flaskr core tables
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS post;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE post (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  title TEXT NOT NULL,
  body TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);

-- Stage 2: Lead capture
DROP TABLE IF EXISTS lead;

CREATE TABLE lead (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  name TEXT NOT NULL,
  email TEXT NOT NULL,
  company TEXT,
  message TEXT NOT NULL,
  webhook_fired INTEGER NOT NULL DEFAULT 0  -- 1 if Make was notified
);

-- Stage 3: Gated case studies
DROP TABLE IF EXISTS case_study;
DROP TABLE IF EXISTS case_study_request;

CREATE TABLE case_study (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  summary TEXT NOT NULL,
  industry TEXT NOT NULL,
  file_url TEXT  -- The URL Make will send to approved requesters
);

CREATE TABLE case_study_request (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  case_study_id INTEGER NOT NULL,
  requester_name TEXT NOT NULL,
  requester_email TEXT NOT NULL,
  requester_company TEXT,
  status TEXT NOT NULL DEFAULT 'pending',  -- pending | approved | declined
  webhook_fired INTEGER NOT NULL DEFAULT 0,
  FOREIGN KEY (case_study_id) REFERENCES case_study (id)
);

-- Seed case studies so the demo works immediately
INSERT INTO case_study (title, summary, industry, file_url) VALUES
  (
    'Zero-Trust Network Rollout at Regional Bank',
    'How Sentinel Security helped a mid-size regional bank implement zero-trust architecture across 42 branches with zero downtime.',
    'Financial Services',
    'https://example.com/case-studies/bank-zero-trust.pdf'
  ),
  (
    'Incident Response: Manufacturing Plant Ransomware',
    'A step-by-step account of how Sentinel''s IR team contained a ransomware attack at a 500-person manufacturing facility within 6 hours.',
    'Manufacturing',
    'https://example.com/case-studies/manufacturing-ransomware.pdf'
  ),
  (
    'HIPAA Compliance Audit & Remediation',
    'Full remediation of 23 HIPAA findings at a healthcare provider, completed in 90 days with no regulatory penalty.',
    'Healthcare',
    'https://example.com/case-studies/hipaa-remediation.pdf'
  );
