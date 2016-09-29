#########################################
# CREATE SQLite DB ON PythonAnywhere
#########################################
from sqlalchemy import create_engine
import sqlite3
disk_engine = create_engine('sqlite:///passenger.db')
conn = sqlite3.connect('passenger.db')
c = conn.cursor()

# Create passenger table
c.execute("CREATE TABLE passenger \
	(\
		passengerID int, \ 			# 0
        picked_up_status int, \    # 1
        origin varchar(100), \      # 2
        destination varchar(100), \ # 3
        gender int, \              # 4
        vehicleID varchar(20), \    # 5
        seatingDemand int \         # 6
    );")
conn.commit()

# Create vehicle table
c.execute("CREATE TABLE vehicle \
	(\
		vehicleID varchar(20), \     # 0
        fuel_economy double, \       # 1
        data_loggerID varchar(20), \ # 2
        vehicleAlias varchar(20), \   # 3
        passengerCapacity int \
    );")
conn.commit()

# Add our taxi fleet in
c.execute("INSERT INTO vehicle VALUES ('1FADP5BU4EL513709', 4.349, 'OpenXC_Logger1', 'naanaa', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FADP3F21GL285457', 8.927, 'OpenXC_Logger2', 'qarfa', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FADP3F21GL285393', 1.462, 'OpenXC_Logger3', 'kamoun', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('3FADP4BJ5GM150984', 5.036, 'OpenXC_Logger4', 'kharqoum', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FADP3F21FL245135', 5.081, 'OpenXC_Logger5', 'skinjbir', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FMCU9J94GUC14197', 7.516, 'OpenXC_Logger6', 'libzar', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FADP3K29FL326275', 5.858, 'OpenXC_Logger7', 'elgouza', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('1FMCU9G94GUC63004', 4.623, 'OpenXC_Logger8', 'qesbour', 4)")
conn.commit()

c.execute("INSERT INTO vehicle VALUES ('3FADP4BJ5DM119777', 3.785, 'OpenXC_Logger9', 'fliyo', 4)")
conn.commit()