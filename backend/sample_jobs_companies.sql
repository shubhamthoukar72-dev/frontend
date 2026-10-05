CREATE TABLE IF NOT EXISTS companies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    industry TEXT NOT NULL,
    size TEXT NOT NULL,
    location TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    location TEXT NOT NULL,
    salary TEXT NOT NULL,
    required_skills TEXT NOT NULL,
    company_id INTEGER NOT NULL REFERENCES companies(id)
);

INSERT INTO companies (id, name, industry, size, location) VALUES
    (1, 'Northstar Labs', 'Software Development', '51-200 employees', 'Bengaluru, India'),
    (2, 'CloudHarbor Systems', 'Cloud Computing', '201-500 employees', 'Hyderabad, India'),
    (3, 'Brightpath AI', 'Artificial Intelligence', '51-200 employees', 'Pune, India'),
    (4, 'Greenbyte Tech', 'Clean Technology', '11-50 employees', 'Chennai, India'),
    (5, 'PixelForge Studio', 'Product Design', '11-50 employees', 'Remote, India');

INSERT INTO jobs (id, title, location, salary, required_skills, company_id) VALUES
    (1, 'Frontend Developer', 'Bengaluru, India', '₹12,00,000 - ₹18,00,000 per year', '["React", "TypeScript", "JavaScript", "CSS"]', 1),
    (2, 'Backend Engineer', 'Hyderabad, India', '₹15,00,000 - ₹22,00,000 per year', '["Node.js", "PostgreSQL", "REST APIs", "Docker"]', 2),
    (3, 'Data Scientist', 'Pune, India', '₹14,00,000 - ₹20,00,000 per year', '["Python", "SQL", "Machine Learning", "Pandas"]', 3),
    (4, 'Cloud Engineer', 'Remote, India', '₹16,00,000 - ₹24,00,000 per year', '["AWS", "Terraform", "Kubernetes", "Linux"]', 2),
    (5, 'Product Designer', 'Chennai, India', '₹10,00,000 - ₹16,00,000 per year', '["Figma", "User Research", "Prototyping", "Accessibility"]', 5);
