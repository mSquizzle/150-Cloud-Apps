# Populate database with demo data 

USE mrs;


# Donors
INSERT INTO donor (first_name, last_name, phone, email, blood_type, zipcode, last_Donation) 
  VALUES('sonal', 'c', '9786174567', 'abcd@gmail.com', 'O+', '02155', '2017-12-30');
  
  INSERT INTO donor (first_name, last_name, phone, email, zipcode) 
  VALUES ('Cardinal', 'Rose', '1239874567', 'hello@world.com', '02143');


  INSERT INTO donor (first_name, last_name, phone, email, zipcode) 
  VALUES ('Jon', 'Snow', '1239874567', 'jsnow@thewall.com', '01742');

  INSERT INTO donor (first_name, last_name, phone, email, zipcode, blood_type) 
  VALUES ('Jaqen', 'H’ghar', '1239193567', 'jhghar@faceless.com', '90064', 'B+');

  INSERT INTO donor (first_name, last_name, phone, email, zipcode) 
  VALUES ('Sirius', 'Black', '6739874567', 'sblack@padfoot.com', '02153');


# Banks
INSERT INTO bank (hashed, name, phone, email, address_1, city, state, zipcode, O_neg, O_pos, A_neg, A_pos, B_neg, B_pos, AB_neg, AB_pos)
VALUES ('password_hash', 'Beautiful Blood', '9784309876', 'admin@bblood.org', '123 Main St', 'Boston', 'MA', '01274', 10, 10, 10, 1000, 100, 1000, 100, 100);

INSERT INTO bank (hashed, name, phone, email, address_1, city, state, zipcode, O_neg, O_pos, A_neg, A_pos, B_neg, B_pos, AB_neg, AB_pos)
VALUES ('password_hash', 'Medford Red Cross', '6174309876', 'admin@mdrc.org', '123 College Ave', 'Medford', 'MA', '02155', 100, 100, 10, 100, 100, 1000, 100, 100);


# Hospitals 
INSERT INTO hospital (hashed, name, phone, email, address_1, city, state, zipcode, O_neg, O_pos, A_neg, A_pos, B_neg, B_pos, AB_neg, AB_pos)
VALUES ('password_hash', 'Massachusetts General Hospital', '6173458920', 'admin@mgh.org', '55 Fruit St', 'Boston', 'MA', '02111', 100, 100, 100, 100, 100, 100, 100, 100);
