use tomato;

--
-- Tables deletion
--
DROP TABLE IF EXISTS idtorasp;
DROP TABLE IF EXISTS plantdata;
DROP TABLE IF EXISTS greenhouselight;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS resettokens;

--
-- Tables creation
--

CREATE TABLE users (
    username VARCHAR(20),
    clearpass VARCHAR(64),
    email VARCHAR(250),
    
    PRIMARY KEY (username)
);

CREATE TABLE resettokens (
	id INT,
    email VARCHAR(100),
    token VARCHAR(64),
    expiration DATETIME,
    createdAt DATETIME,
    updatedAt DATETIME,
    used INT,
    
    PRIMARY KEY (id)
);

CREATE TABLE plantdata (
	plantid INT auto_increment,
    ip CHAR(15),
    username CHAR(30),
    planttype VARCHAR(20),
    irrigation INT,
    photoperiod INT,
    luxgoal INT,
    blue INT,
    white INT,
    hred INT,
    nightbegin VARCHAR(10) DEFAULT NULL,
    nightend VARCHAR(10) DEFAULT NULL,
    pins VARCHAR(20),
    intensity INT,
    development DECIMAL(5,4),
    firsttomato DATETIME DEFAULT NULL,
    firstripe DATETIME DEFAULT NULL,
    lasttomato DATETIME DEFAULT NULL,
    image VARCHAR(200),
    
    PRIMARY KEY (plantid),
    FOREIGN KEY (username) REFERENCES users (username)
);

CREATE TABLE idtorasp (
	id INT,
    ip CHAR(15),
	mac CHAR(17),
    
    FOREIGN KEY (id) REFERENCES plantdata (plantid)
);

CREATE TABLE greenhouselight (
	building VARCHAR(50),
    logdata INT,
    logdate DATETIME
);

--
-- Procedures
-- 
DROP PROCEDURE IF EXISTS show_raspis;
DELIMITER ;;
CREATE PROCEDURE show_raspis(
	a_user VARCHAR(30)
)
BEGIN
	SELECT
		*
	FROM
		plantdata
    WHERE
		username = a_user
	;
END
;;
DELIMITER ;

DROP PROCEDURE IF EXISTS new_raspi;
DELIMITER ;;
CREATE PROCEDURE new_raspi(
    a_ip CHAR(15),
    a_planttype VARCHAR(50),
    a_username CHAR(30),
    a_luxgoal INT,
    a_blue INT,
    a_white INT,
    a_hred INT,
    a_nightbegin VARCHAR(10),
    a_nightend VARCHAR(10),
    a_pins VARCHAR(20),
    a_intensity INT,
    a_img VARCHAR(200)
)
BEGIN
	INSERT INTO plantdata
		(ip, planttype, username, luxgoal, blue, white, hred, nightbegin, nightend, pins, intensity, image)
	VALUES
		(a_ip, a_planttype, a_username, a_luxgoal, a_blue, a_white, a_hred, a_nightbegin, a_nightend, a_pins, a_intensity, a_img)
	;
END
;;
DELIMITER ;

DROP PROCEDURE IF EXISTS log_light;
DELIMITER ;;
CREATE PROCEDURE log_light (
	a_lightval INT,
    a_logdate DATETIME
)
BEGIN
	INSERT INTO
		greenhouselight(building, logdata, logdate)
	VALUES(1, a_lightval, DATE_FORMAT(a_logdate, "%Y-%c-%d %T"))
	;
END
;;
DELIMITER ;

DROP PROCEDURE IF EXISTS get_light_ratio;
DELIMITER ;;
CREATE PROCEDURE get_light_ratio (
	a_ip CHAR(15)
)
BEGIN
	SELECT
		luxgoal,
		blue,
        white,
        hred,
		nightbegin,
        nightend,
        pins,
        intensity
	FROM
		plantdata
	WHERE
        a_ip = ip
	;
END
;;
DELIMITER ;

DROP PROCEDURE IF EXISTS get_all_ip;
DELIMITER ;;
CREATE PROCEDURE get_all_ip ()
BEGIN
	SELECT
		ip
	FROM
		plantdata
	;
END
;;
DELIMITER ;

DROP PROCEDURE IF EXISTS tomato_firsts;
DELIMITER ;;
CREATE PROCEDURE tomato_firsts(
	a_ripe INT,
    a_noripe INT,
    a_ip CHAR(15)
)
Hello:BEGIN
-- Hämta id från idtorasp ( @id )
	SELECT
		id
	INTO
		@id
	FROM
		idtorasp
	WHERE
		a_ip = ip
	;
    
    SELECT
		firsttomato,
        firstripe,
        lasttomato
	INTO
		@first,
        @ripe,
        @last
	FROM
		plantdata
	WHERE
		@id = plantid
	;
    
    if (@first is not null) then
		if (@ripe is not null) then
			if (@last is not null) then
				leave Hello;
			elseif (a_noripe = 0 and a_ripe = 0) then
				UPDATE plantdata 
				SET lasttomato = NOW()
                WHERE plantid = @id;
			end if;
		elseif (a_ripe != 0) then
			update plantdata
            SET firstripe = NOW()
            WHERE plantid = @id;
		end if;
	elseif (a_noripe != 0) then
		update plantdata
		SET firsttomato = NOW()
		WHERE plantid = @id;
    end if;
END
;;
DELIMITER ;

--
-- Functions
-- 
DROP FUNCTION IF EXISTS idrasp;
DELIMITER ;;
CREATE FUNCTION idrasp(
	a_ip CHAR(15)
)
RETURNS INT
DETERMINISTIC
BEGIN
	SELECT
		id
	INTO
		@r_id
	FROM
		idtorasp
	WHERE
		a_ip = ip
	;
    IF @r_id IS NOT NULL THEN
		return @r_id;
	ELSE
		return NULL;
    END IF;
END
;;
DELIMITER ;
