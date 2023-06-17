import mysql.connector
import datetime
# # Establish a connection to the database
from dateutil.relativedelta import relativedelta
import random

def update_interest_earn():
    # Establish a new MySQL connection
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="bank"
    )
    print("Checking for updates...")

    # Get the current date
    current_date = datetime.datetime.now().date()
   
    formatted_date = current_date.strftime("%d-%m-%y")
    


    cursor = db.cursor()

    # Retrieve all details from the deposit account table
    cursor.execute("SELECT deposit_type, interest_amt, acc_no, last_transaction_date, maturity_date, tenure, deposit_amt,ifsccode FROM depositacc")
    deposit_accounts = cursor.fetchall()

    updates_made = False

    for account in deposit_accounts:
        deposit_type = account[0]
        interest_amt = account[1]
        acc_no = account[2]
        last_transaction_date = datetime.datetime.strptime(account[3], "%d-%m-%y").date()
        maturity_date = datetime.datetime.strptime(account[4], "%d/%m/%y").date()
        tenure = account[5]
        deposit_amt = account[6]
        ifsccode = account[7]
        formatted_date1 = current_date.strftime("%d-%m-%y")
        last_transaction_date1 = last_transaction_date.strftime("%d-%m-%y")
        maturity_date1= maturity_date.strftime("%d-%m-%y")
        trans_no = str(random.randint(1000000000000000, 9999999999999999))

        if deposit_type == 'monthly':
            days_diff = (last_transaction_date - current_date).days
            if days_diff >= 30:
                # Calculate the interest earned based on the interest amount
                interest_earned = interest_amt

                # Update the interest_earn field in the table
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s and acc_status='active'"
                cursor.execute(update_query, (interest_earned, formatted_date, acc_no))
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))
                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s)"
                transaction_values = (cid,deposit_id,bid,trans_no,interest_earned,formatted_date)
                cursor.execute(transaction, transaction_values)
                print("Interest earnings updated ",interest_amt,"successfully for account:", acc_no)
                updates_made = True
            # Check if additional month has passed after maturity date
                # additional_month_date = maturity_date + datetime.timedelta(days=30)
            # formatted_date1 = datetime.datetime.strptime(formatted_date1, "%d-%m-%y").date()
            
            if last_transaction_date >= maturity_date:
        # Update the interest_earn field with interest_earn + deposit_amt
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + deposit_amt,acc_status='closed' WHERE acc_no = %s"
                cursor.execute(update_query, (acc_no,))
                print("Interest earnings updated with deposit amount for account:", acc_no)

        elif deposit_type == 'yearly' and maturity_date >= last_transaction_date:
            print('yearly')
            years_diff = last_transaction_date.year - current_date.year
            if years_diff >= 1:
                # Calculate the interest earned based on the interest amount
                interest_earned = interest_amt * years_diff

                # Update the interest_earn field in the table
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s"
                cursor.execute(update_query, (interest_earned, formatted_date, acc_no))
                print("Interest earnings updated successfully for account:", acc_no)
                updates_made = True

        elif deposit_type == 'quarterly' and maturity_date >= last_transaction_date:
            quarters_diff = (last_transaction_date.year-current_date.year) * 4 + (last_transaction_date.month -current_date.month ) // 3
            if quarters_diff >= 1:
                # Calculate the interest earned based on the interest amount
                interest_earned = interest_amt * quarters_diff

                # Update the interest_earn field in the table
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s"
                cursor.execute(update_query, (interest_earned, formatted_date, acc_no))
                print("Interest earnings updated successfully for account:", acc_no)
                updates_made = True

        elif deposit_type == 'maturity_date':
            if current_date >= maturity_date:
                # Calculate the total interest amount
                total_interest_amt = interest_amt * tenure

                # Calculate the interest earned based on the total interest amount and deposit amount
                interest_earned = total_interest_amt + deposit_amt
                print(interest_earned)

                # Update the interest_earn field in the table
                update_query = "UPDATE depositacc SET interest_earn = %s, last_transaction_date = %s WHERE acc_no = %s"
                cursor.execute(update_query, (interest_earned, formatted_date, acc_no))
                print("Interest earnings updated successfully for account:", acc_no)
                updates_made = True

    db.commit()  # Commit the changes to the database
    cursor.close()
    db.close()

    return updates_made




   

    




# import datetime
# import mysql.connector

# # Establish a new MySQL connection
# db = mysql.connector.connect(
#     host="localhost",
#     user="root",
#     password="",
#     database="bank"
# )

# def update_interest_earn():
#     # Get the current date
#     current_date = datetime.datetime.now().date()

#     cursor = db.cursor()

#     # Retrieve all details from the deposit account table
#     cursor.execute("SELECT deposit_type, interest_amt, acc_no, last_transaction_date FROM depositacc")
#     deposit_accounts = cursor.fetchall()

#     updates_made = False

#     for account in deposit_accounts:
#         deposit_type = account[0]
#         interest_amt = account[1]
#         acc_no = account[2]
#         last_transaction_date_str = account[3]

#         # Convert the last_transaction_date string to a datetime.date object
#         last_transaction_date = datetime.datetime.strptime(last_transaction_date_str, '%Y-%m-%d').date()

#         if deposit_type == 'monthly':
#             # Calculate the difference in days between the last transaction date and the current date
#             days_diff = (last_transaction_date - current_date).days

#             if days_diff >= 30:
#                 # Calculate the interest earned based on the interest amount
#                 interest_earned = interest_amt

#                 # Update the interest_earn field in the table
#                 update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s WHERE acc_no = %s"
#                 cursor.execute(update_query, (interest_earned, acc_no))
#                 print(f"Interest earnings updated for account {acc_no}")

#                 # Set the flag to indicate updates were made
#                 updates_made = True

#     db.commit()  # Commit the changes to the database
#     cursor.close()

#     # Close the database connection
#     db.close()

#     return updates_made
