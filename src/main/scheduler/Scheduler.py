from model.Vaccine import Vaccine
from model.Caregiver import Caregiver
from model.Patient import Patient
from util.Util import Util
from db.ConnectionManager import ConnectionManager
import pymssql
import datetime
import re


'''
objects to keep track of the currently logged-in user
Note: it is always true that at most one of currentCaregiver and currentPatient is not null
        since only one user can be logged-in at a time
'''
current_patient = None

current_caregiver = None


def create_patient(tokens):
    """
    TODO: Part 1
    """
    # create_patient <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_patient(username):
        print("Username taken, try again!")
        return
    
    if not check_password(password):  
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the patient
    patient = Patient(username, salt=salt, hash=hash)

    # save to patient information to our database
    try:
        patient.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)


def create_caregiver(tokens):
    # create_caregiver <username> <password>
    # check 1: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Failed to create user.")
        return

    username = tokens[1]
    password = tokens[2]
    # check 2: check if the username has been taken already
    if username_exists_caregiver(username):
        print("Username taken, try again!")
        return

    if not check_password(password):  
        return

    salt = Util.generate_salt()
    hash = Util.generate_hash(password, salt)

    # create the caregiver
    caregiver = Caregiver(username, salt=salt, hash=hash)

    # save to caregiver information to our database
    try:
        caregiver.save_to_db()
    except pymssql.Error as e:
        print("Failed to create user.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Failed to create user.")
        print(e)
        return
    print("Created user ", username)

def check_password(password):  # Extra credit option using regex to check various password requirements
    if len(password) < 8:
        print("Password must have at least 8 characters!")
        return False
    if any(letter.islower() for letter in password) and any(letter.isupper() for letter in password) == False:
        print("Password must have a mixture of both uppercase and lowercase letters")
        return False
    if re.search(r"[\d]+", password) is None:
        print("Password must have a mixture of letters and numbers")
        return False
    if re.search(r"[!@#?]+", password) is None:
        print("Password must include of at least one special character, from !, @, #, ?")
        return False
    return True

def username_exists_caregiver(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Caregivers WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False

def username_exists_patient(username):
    cm = ConnectionManager()
    conn = cm.create_connection()

    select_username = "SELECT * FROM Patients WHERE Username = %s"
    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute(select_username, username)
        #  returns false if the cursor is not before the first record or if there are no rows in the ResultSet.
        for row in cursor:
            return row['Username'] is not None
    except pymssql.Error as e:
        print("Error occurred when checking username")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when checking username")
        print("Error:", e)
    finally:
        cm.close_connection()
    return False



def login_patient(tokens):
    """
    TODO: Part 1
    """
    # login_patient <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_patient
    if current_patient is not None or current_caregiver is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    patient = None
    try:
        patient = Patient(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if patient is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_patient = patient


def login_caregiver(tokens):
    # login_caregiver <username> <password>
    # check 1: if someone's already logged-in, they need to log out first
    global current_caregiver
    if current_caregiver is not None or current_patient is not None:
        print("User already logged in.")
        return

    # check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Login failed.")
        return

    username = tokens[1]
    password = tokens[2]

    caregiver = None
    try:
        caregiver = Caregiver(username, password=password).get()
    except pymssql.Error as e:
        print("Login failed.")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Login failed.")
        print("Error:", e)
        return

    # check if the login was successful
    if caregiver is None:
        print("Login failed.")
    else:
        print("Logged in as: " + username)
        current_caregiver = caregiver


def search_caregiver_schedule(tokens):
    """
    TODO: Part 2(finished)
    """
    if current_caregiver == None and current_patient == None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please try again!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        date_whole = tokens[1].split("-")
        month = int(date_whole[0])
        day = int(date_whole[1])
        year = int(date_whole[2])
        d = datetime.datetime(year, month, day)

        get_available_dates = "SELECT Time, Username FROM Availabilities WHERE Time = %s ORDER BY Username"
        get_vaccines = "SELECT Name, Doses FROM Vaccines"

        cursor.execute(get_available_dates, d)
        avail_rows = cursor.fetchall()
        cursor.execute(get_vaccines)
        vacci_rows = cursor.fetchall()

        if len(avail_rows) == 0:  
            print("There are no appointments available on ", tokens[1])
            return

        print("{} ".format("Caregiver"), end="")
        for i in range(0, len(vacci_rows)):
            print("{} ".format(vacci_rows[i]["Name"]), end="")
        print("\n", end="")

        for row in avail_rows:
            print("{} ".format(row['Username']), end="")
            for i in range(len(vacci_rows)):
                print("{} ".format(vacci_rows[i]["Doses"]), end="")
            print("")

        #cursor.execute(get_available_dates, d)
    except pymssql.Error:
        print("Please try again!")
        return
    except ValueError:
        print("Please try again!")
        return
    except Exception:
        print("Please try again!")
        return
    finally:
        cm.close_connection()


def reserve(tokens):
    """
    TODO: Part 2(finished)
    """
    if current_patient == None and current_caregiver == None:
        print("Please login first!")
        return
    if current_patient == None:
        print("Please login as a patient!")
        return
    if len(tokens) != 3:
        print("Please try again!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)

    try:
        date_whole = tokens[1].split("-")
        month = int(date_whole[0])
        day = int(date_whole[1])
        year = int(date_whole[2])
        d = datetime.datetime(year, month, day)
        get_available_dates =  "SELECT TOP 1 Time, Username \
                                FROM Availabilities \
                                WHERE Time = %s \
                                ORDER BY Username"

        cursor.execute(get_available_dates, d)
        aval_date = cursor.fetchall()

        if len(aval_date) == 0:
            print("No Caregiver is available!")
            return
        booked_time = aval_date[0]["Time"]
        booked_caregiver = aval_date[0]["Username"]
        V_name = tokens[2]
        get_vaccine = Vaccine(V_name, available_doses = None)
        get_vaccine = get_vaccine.get()

        if get_vaccine is None:
            print("Please try again!")
            return
        if get_vaccine.available_doses == 0:    
            print("Not enough available doses!")
            return
        get_vaccine.decrease_available_doses(1)

        book_appointment = "INSERT INTO Appointments VALUES (%d, %s, %s, %s, %s)"

        _cursor = conn.cursor()
        _cursor.execute(   "SELECT MAX(Id) \
                            FROM Appointments")
        current_id = _cursor.fetchone()[0]
        if current_id == None:
            cursor.execute(book_appointment, (1, booked_time, current_patient.username,
                                              booked_caregiver, V_name))
        else:
            cursor.execute(book_appointment, (current_id+1, booked_time, current_patient.username,
                                              booked_caregiver, V_name))
        drop_availability = "DELETE FROM Availabilities \
                             WHERE Time = %s AND Username = %s"
        cursor.execute(drop_availability, (d, booked_caregiver))
        conn.commit()
        #print("success")
        booked_appointments = "SELECT Id, C_name \
                              FROM appointments \
                              WHERE C_name = %s AND Time = %s"
        cursor.execute(booked_appointments, (booked_caregiver, booked_time))
        booked_appointment = cursor.fetchall()
        for i in range(len(booked_appointment)):
                print("{} {}".format(booked_appointment[i]["Id"],
                                            booked_appointment[i]["C_name"]), end="\n")
    except pymssql.Error as e:
        print("Please try again!")
        print("DBError:", e)
        return
    except ValueError as e:
        print("Please try again!")
        print("Error:", e)
        return
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
        return
    finally:
        cm.close_connection()        

def upload_availability(tokens):
    #  upload_availability <date>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    # check 2: the length for tokens need to be exactly 2 to include all information (with the operation name)
    if len(tokens) != 2:
        print("Please try again!")
        return

    date = tokens[1]
    # assume input is hyphenated in the format mm-dd-yyyy
    date_tokens = date.split("-")
    month = int(date_tokens[0])
    day = int(date_tokens[1])
    year = int(date_tokens[2])
    try:
        d = datetime.datetime(year, month, day)
        current_caregiver.upload_availability(d)
    except pymssql.Error as e:
        print("Upload Availability Failed")
        print("Db-Error:", e)
        quit()
    except ValueError:
        print("Please enter a valid date!")
        return
    except Exception as e:
        print("Error occurred when uploading availability")
        print("Error:", e)
        return
    print("Availability uploaded!")


def cancel(tokens):
    """
    TODO: Extra Credit
    """
    if current_patient == None and current_caregiver == None:
        print("Please login first!")
        return
    if len(tokens) != 2:
        print("Please try again!")
        return
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    id = tokens[1]
    
    try:
        get_appointment =  "SELECT Id, Time, P_name, C_name, V_name \
                            FROM Appointments \
                            WHERE Id = %d"
        cursor.execute(get_appointment, id)
        appointment = cursor.fetchall()
        cancel = False
        if current_patient:
            if appointment[0]['P_name'] == current_patient.username:
                cancel = True
            else:
                print("Please try again!")
        else:
            if appointment[0]['C_name'] == current_caregiver.username:
                cancel = True
            else:
                print("Please try again!")

        if cancel:
            delete_appointment =   "DELETE FROM Appointments \
                                    WHERE Id = %d"
            vaccine = Vaccine(appointment[0]["V_name"], None).get()
            cursor.execute(delete_appointment, id)
            conn.commit()
            vaccine.increase_available_doses(1)
            print("Cancel Successfully! Available doses:{}".format(vaccine.get_available_doses()))
        else:
            return
    except pymssql.Error as e:
        print("Please try again!")
        print("DBError:", e)
    except Exception as e:
        print("Please try again!")
    finally:
        cm.close_connection()


def add_doses(tokens):
    #  add_doses <vaccine> <number>
    #  check 1: check if the current logged-in user is a caregiver
    global current_caregiver
    if current_caregiver is None:
        print("Please login as a caregiver first!")
        return

    #  check 2: the length for tokens need to be exactly 3 to include all information (with the operation name)
    if len(tokens) != 3:
        print("Please try again!")
        return

    vaccine_name = tokens[1]
    doses = int(tokens[2])
    vaccine = None
    try:
        vaccine = Vaccine(vaccine_name, doses).get()
    except pymssql.Error as e:
        print("Error occurred when adding doses")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Error occurred when adding doses")
        print("Error:", e)
        return

    # if the vaccine is not found in the database, add a new (vaccine, doses) entry.
    # else, update the existing entry by adding the new doses
    if vaccine is None:
        vaccine = Vaccine(vaccine_name, doses)
        try:
            vaccine.save_to_db()
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    else:
        # if the vaccine is not null, meaning that the vaccine already exists in our table
        try:
            vaccine.increase_available_doses(doses)
        except pymssql.Error as e:
            print("Error occurred when adding doses")
            print("Db-Error:", e)
            quit()
        except Exception as e:
            print("Error occurred when adding doses")
            print("Error:", e)
            return
    print("Doses updated!")


def show_appointments(tokens):
    '''
    TODO: Part 2(finished)
    '''
    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return

    if len(tokens) != 1:
        print("Please try again!")
        return
    
    cm = ConnectionManager()
    conn = cm.create_connection()
    cursor = conn.cursor(as_dict=True)
    try:
        if current_patient is not None:
            get_patient_appointments = "SELECT Id, V_name, Time, C_name \
                                        FROM Appointments WHERE  \
                                        P_name = %s ORDER BY Id" 
            cursor.execute(get_patient_appointments, current_patient.username)
            patient_appointments = cursor.fetchall()
            print("{} {} {} {}".format("Appointment_ID", "Vaccine_name", "Date", "Caregiver_name"), end="\n")
            for i in range(len(patient_appointments)):
                print("{} {} {} {}".format(patient_appointments[i]["Id"],
                                            patient_appointments[i]["V_name"], 
                                            str(patient_appointments[i]["Time"]),
                                            patient_appointments[i]["C_name"]))
        else:
            get_caregiver_appointments = "SELECT Id, V_name, Time, P_name \
                                        FROM Appointments WHERE  \
                                        C_name = %s ORDER BY Id" 
            cursor.execute(get_caregiver_appointments, current_patient.username)
            caregiver_appointments = cursor.fetchall()
            print("{} {} {} {}".format("Appointment_ID", "Vaccine_name", "Date", "Patient_name"),end="\n")
            for i in range(len(caregiver_appointments)):
                print("{} {} {} {}".format(caregiver_appointments[i]["Id"],
                                            caregiver_appointments[i]["V_name"], 
                                            str(caregiver_appointments[i]["Time"]),
                                            caregiver_appointments[i]["P_name"]))
    except pymssql.Error as e:
        print("Please try again!")
        print("Db-Error:", e)
        quit()
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
    finally:
        cm.close_connection()                                                            

    


def logout(tokens):
    """
    TODO: Part 2(finished)
    """
    global current_caregiver
    global current_patient

    if current_caregiver is None and current_patient is None:
        print("Please login first.")
        return
    
    if len(tokens) != 1:
        print("Please try again!")
        return
    
    try:
        current_caregiver = None
        current_patient = None
        print("Successfully logged out!")
    except Exception as e:
        print("Please try again!")
        print("Error:", e)
        return





def start():
    stop = False
    print()
    print(" *** Please enter one of the following commands *** ")
    print("> create_patient <username> <password>")  # //TODO: implement create_patient (Part 1)
    print("> create_caregiver <username> <password>")
    print("> login_patient <username> <password>")  # // TODO: implement login_patient (Part 1)
    print("> login_caregiver <username> <password>")
    print("> search_caregiver_schedule <date>")  # // TODO: implement search_caregiver_schedule (Part 2)
    print("> reserve <date> <vaccine>")  # // TODO: implement reserve (Part 2)
    print("> upload_availability <date>")
    print("> cancel <appointment_id>")  # // TODO: implement cancel (extra credit)
    print("> add_doses <vaccine> <number>")
    print("> show_appointments")  # // TODO: implement show_appointments (Part 2)
    print("> logout")  # // TODO: implement logout (Part 2)
    print("> Quit")
    print()
    while not stop:
        response = ""
        print("> ", end='')

        try:
            response = str(input())
        except ValueError:
            print("Please try again!")
            break
        
        tokens = response.split(" ")
        tokens[0] = tokens[0].lower()
        
        if len(tokens) == 0:
            ValueError("Please try again!")
            continue
        operation = tokens[0]
        if operation == "create_patient":
            create_patient(tokens)
        elif operation == "create_caregiver":
            create_caregiver(tokens)
        elif operation == "login_patient":
            login_patient(tokens)
        elif operation == "login_caregiver":
            login_caregiver(tokens)
        elif operation == "search_caregiver_schedule":
            search_caregiver_schedule(tokens)
        elif operation == "reserve":
            reserve(tokens)
        elif operation == "upload_availability":
            upload_availability(tokens)
        elif operation == "cancel":
            cancel(tokens)
        elif operation == "add_doses":
            add_doses(tokens)
        elif operation == "show_appointments":
            show_appointments(tokens)
        elif operation == "logout":
            logout(tokens)
        elif operation == "quit":
            print("Bye!")
            stop = True
        else:
            print("Invalid operation name!")


if __name__ == "__main__":
    '''
    // pre-define the three types of authorized vaccines
    // note: it's a poor practice to hard-code these values, but we will do this ]
    // for the simplicity of this assignment
    // and then construct a map of vaccineName -> vaccineObject
    '''

    # start command line
    print()
    print("Welcome to the COVID-19 Vaccine Reservation Scheduling Application!")

    start()
