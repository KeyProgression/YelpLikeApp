DROP TABLE if exists YelpTip;
DROP TABLE if exists Friends;
DROP TABLE if exists HasCategory;
DROP TABLE if exists YelpCheckIn;
DROP TABLE if exists HasHours;
DROP TABLE if exists Business CASCADE;
DROP TABLE if exists Users;

CREATE TABLE Users(
    user_id CHAR(22) PRIMARY KEY,
    user_name VARCHAR(100),
    yelping_since VARCHAR(20),
    user_avg_stars FLOAT,
	num_of_fans INT,
	tip_count INT DEFAULT 0,
	totalLikes INT DEFAULT 0,
	useful INT,
	funny INT,
	cool INT,
	user_latitude DECIMAL,
	user_longitude DECIMAL
);

CREATE TABLE Friends(
  user_id CHAR(22),
  friend_id CHAR(22),
  PRIMARY KEY (user_id,friend_id),
  FOREIGN KEY (user_id) REFERENCES Users(user_id),
  FOREIGN KEY (friend_id) REFERENCES Users(user_id)
);

CREATE TABLE Business (
    business_id CHAR(22) PRIMARY KEY,
    business_name VARCHAR(225),
    address VARCHAR(225),
    city VARCHAR(50),
	state_name CHAR(2),
	zip_code INT,
	latitude DECIMAL,
	longitude DECIMAL,
	business_avg_star FLOAT,
	review_count INT,
	is_open BOOL,
	num_of_tips INT DEFAULT 0,
	num_of_checkins INT DEFAULT 0
);

CREATE TABLE YelpTip (
	business_id CHAR(22),
	user_id CHAR(22),
	tip_date TIMESTAMP,
	num_of_likes INT,
	tip_text TEXT,
	PRIMARY KEY (business_id,user_id,tip_date),
	FOREIGN KEY (business_id) REFERENCES Business(business_id),
	FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE YelpCheckIn(
	business_id CHAR(22),
	checkin_year INT,
	checkin_month INT,
	checkin_day INT,
	checkin_time VARCHAR(8),
	PRIMARY KEY (business_id, checkin_year, checkin_month, checkin_day,checkin_time),
	FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE HasCategory(
	business_id CHAR(22),
	category_type VARCHAR(255),
	PRIMARY KEY (business_id, category_type),
	FOREIGN KEY (business_id) REFERENCES Business(business_id)
);

CREATE TABLE HasHours(
	business_id CHAR(22),
	dayofweek VARCHAR(50),
	open_hour VARCHAR(5),
	close_hour VARCHAR(5),
	PRIMARY KEY (business_id, dayofweek),
	FOREIGN KEY (business_id) REFERENCES Business(business_id)
);