PRAGMA foreign_keys = ON;

CREATE TABLE participants (
    participant_id TEXT PRIMARY KEY,
    cohort TEXT NOT NULL CHECK (cohort IN ('breast','nerve','wound')),
    age_band TEXT NOT NULL CHECK (age_band IN ('18-39','40-59','60+')),
    enrolled_on TEXT NOT NULL
);

CREATE TABLE procedures (
    procedure_id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL UNIQUE REFERENCES participants(participant_id),
    cohort TEXT NOT NULL CHECK (cohort IN ('breast','nerve','wound')),
    procedure_on TEXT NOT NULL,
    procedure_type TEXT NOT NULL
);

CREATE TABLE breast_module (
    procedure_id TEXT PRIMARY KEY REFERENCES procedures(procedure_id),
    intent TEXT NOT NULL CHECK (intent IN ('reconstruction','aesthetic')),
    laterality TEXT NOT NULL CHECK (laterality IN ('left','right','bilateral')),
    implant_used INTEGER NOT NULL CHECK (implant_used IN (0,1))
);
CREATE TABLE nerve_module (
    procedure_id TEXT PRIMARY KEY REFERENCES procedures(procedure_id),
    injury_level TEXT NOT NULL CHECK (injury_level IN ('plexus','peripheral')),
    technique TEXT NOT NULL CHECK (technique IN ('transfer','graft','primary repair')),
    target_function TEXT NOT NULL CHECK (target_function IN ('shoulder','elbow','hand'))
);
CREATE TABLE wound_module (
    procedure_id TEXT PRIMARY KEY REFERENCES procedures(procedure_id),
    region TEXT NOT NULL CHECK (region IN ('upper limb','lower limb','trunk')),
    coverage TEXT NOT NULL CHECK (coverage IN ('local flap','free flap','skin graft')),
    defect_size TEXT NOT NULL CHECK (defect_size IN ('small','medium','large'))
);

CREATE TABLE followups (
    followup_id TEXT PRIMARY KEY,
    participant_id TEXT NOT NULL REFERENCES participants(participant_id),
    day_target INTEGER NOT NULL CHECK (day_target IN (30,90,180,365)),
    due_on TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('completed','missed')),
    visit_on TEXT,
    function_score INTEGER CHECK (function_score BETWEEN 0 AND 100),
    UNIQUE(participant_id, day_target)
);
CREATE TABLE adverse_events (
    event_id TEXT PRIMARY KEY,
    procedure_id TEXT NOT NULL REFERENCES procedures(procedure_id),
    event_on TEXT NOT NULL,
    term TEXT NOT NULL CHECK (term IN ('infection','hematoma','wound dehiscence','other')),
    severity TEXT NOT NULL CHECK (severity IN ('mild','moderate','severe')),
    serious INTEGER NOT NULL CHECK (serious IN (0,1)),
    notified_on TEXT
);

CREATE TABLE discrepancy_queries (
    query_id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    record_key TEXT NOT NULL,
    severity TEXT NOT NULL CHECK (severity IN ('critical','major','minor')),
    query_status TEXT NOT NULL CHECK (query_status IN ('open','resolved')),
    description TEXT NOT NULL,
    disposition TEXT
);

CREATE TABLE audit_log (
    audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action_utc TEXT NOT NULL,
    actor TEXT NOT NULL,
    table_name TEXT NOT NULL,
    record_key TEXT NOT NULL,
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    reason TEXT NOT NULL
);
