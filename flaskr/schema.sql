DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS bookings;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    number VARCHAR(11) NOT NULL,
    email TEXT NOT NULL,
    admin BIT NOT NULL
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    datetime DATETIME NOT NULL,
    booked BIT NOT NULL,
    patient_id INTEGER,
    reason TEXT,
    FOREIGN KEY (patient_id) REFERENCES user (id)
);