CREATE DATABASE banksystem;
USE banksystem;
CREATE TABLE Admin
(
  Admin_ID INT AUTO_INCREMENT NOT NULL,
  Admin_name VARCHAR(20) NOT NULL,
  Contact_no NUMERIC(10, 0) NOT NULL,
  Address VARCHAR(50),
  Total_user INT,
  Email VARCHAR(50) NOT NULL,
  PRIMARY KEY (Admin_ID)
);

CREATE TABLE Admin_login_system
(
  Login_ID VARCHAR(20) UNIQUE NOT NULL,
  Login_Password VARCHAR(20) NOT NULL,
  Admin_ID INT NOT NULL,
  PRIMARY KEY (Login_ID),
  FOREIGN KEY (Admin_ID) REFERENCES Admin(Admin_ID)
);

CREATE TABLE Accounts
(
  Account_no INT NOT NULL auto_increment,
  Account_status VARCHAR(20) ,
  Account_name VARCHAR(20) NOT NULL,
  Balance INT NOT NULL,
  Interest_rate INT NOT NULL,
  Admin_ID INT,
  Phone_no NUMERIC(10) NOT NULL,
  Address VARCHAR(50) NOT NULL,
  DOB VARCHAR(20) NOT NULL,
  Aadhaar_no NUMERIC(12) NOT NULL UNIQUE,
  Voter_ID INT UNIQUE, 
  Email VARCHAR(50) NOT NULL UNIQUE,  
  Account_type VARCHAR(20),
  Pan_card VARCHAR(10) UNIQUE,
  PRIMARY KEY (Account_no),  
  FOREIGN KEY (Admin_ID) REFERENCES Admin(Admin_ID)
);

CREATE TABLE Transaction_History
( 
  Transaction_status VARCHAR(20),
  Amount INT NOT NULL,
  ToAccount_ID INT ,
  Transaction_date DATETIME NOT NULL,
  Transaction_ID INT AUTO_INCREMENT NOT NULL,
  Transaction_type VARCHAR(200),
  Account_no INT NOT NULL,
  PRIMARY KEY (Transaction_ID),
  FOREIGN KEY (Account_no) REFERENCES Accounts(Account_no)
);

CREATE TABLE Loan
(
  Interest INT NOT NULL,
  Amount INT NOT NULL,
  Loan_ID INT NOT NULL AUTO_INCREMENT,
  Account_no INT NOT NULL,
  Loan_status VARCHAR(20),
  period VARCHAR(20),
  request_date DATE,
  loan_pass_on DATE,
  amount_passed INT,
  PRIMARY KEY (Loan_ID),
  FOREIGN KEY (Account_no) REFERENCES Accounts(Account_no)
);

CREATE TABLE Account_login_system
(
  Login_ID INT NOT NULL AUTO_INCREMENT,
  Login_password VARCHAR(20) NOT NULL,
  Account_no INT NOT NULL,
  PRIMARY KEY (Login_ID),
  FOREIGN KEY (Account_no) REFERENCES Accounts(Account_no)
);

INSERT INTO Admin(Admin_name, Contact_no, Address,Total_user, Email)
values('Ram', 9934569889, '23-Behargao Street',0, 'Ram2334@gmail.com'),
('Preeti', 9877654438, '456 Shakti Khand-I Ghaziabad',0, 'Preeti1234@gmail.com'),
('Shyam', 7650432240, '56-Rajeev Khand Dholpur',0, 'Shyam1234@gmail.com');

INSERT INTO Admin_login_system(Login_ID, Login_password, admin_ID)
VALUES('Ramop', 'Ram@3000', '1'),
('Preet', 'Pr6854', '2'),
('Shyamxp', 'ss7849', '3');
/*
some commands to check the data in the databases
    SELECT* FROM Admin;
    SELECT* FROM Admin_login_system;
    SELECT* FROM Account_login_system;
    SELECT* FROM Accounts;
    DROP DATABASE banksystem;

*/