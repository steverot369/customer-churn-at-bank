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
    
    


    cursor = db.cursor()

    # Retrieve all details from the deposit account table
    cursor.execute("SELECT deposit_type, interest_amt, acc_no, last_transaction_date, maturity_date, tenure, deposit_amt,ifsccode,acc_to FROM depositacc where acc_status='active'")
    deposit_accounts = cursor.fetchall()

    updates_made = False

    for account in deposit_accounts:
        deposit_type = account[0]

        interest_amt = account[1]
        acc_no = int(account[2])
        last_transaction_date = datetime.datetime.strptime(account[3], "%d-%m-%y").date()
        maturity_date = datetime.datetime.strptime(account[4], "%d-%m-%y").date()
        tenure = int(account[5])
        deposit_amt = int(account[6])
        ifsccode = account[7]
        acc_payable = account[8]
        
    
        print("account payabe===",acc_payable)
        cursor.execute("select balance from savingsacc where acc_no=%s",(acc_payable,))
        account_payable = cursor.fetchone()
        print("balance=====",account_payable)
        if account_payable is not None:
            balance = account_payable[0]
            # Perform further processing with the balance
        else:
            balance='0'
        
        trans_no = str(random.randint(1000000000000000, 9999999999999999))

        if deposit_type == 'monthly':
           
            days_diff = last_transaction_date


            print("days differnece===",days_diff)
            if current_date == days_diff:
                # Calculate the interest earned based on the interest amount
                interest_earned = interest_amt
                updated_balance=balance+interest_earned
                # Update the interest_earn field in the table
                maturity_date = current_date + datetime.timedelta(days=30)
                formatted_maturity_date = maturity_date.strftime("%d-%m-%y")
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s and acc_status='active'"
                cursor.execute(update_query, (interest_earned, formatted_maturity_date, acc_no))
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))
                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance,current_date)
                cursor.execute(transaction, transaction_values)
                update_query1 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query1, (interest_earned,acc_payable,))
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                print("1)Interest earnings updated ",interest_amt,"successfully for account:", acc_no)
                updates_made = True
           
            
            if last_transaction_date >= maturity_date:
                interest_earned = interest_amt
        # Update the interest_earn field with interest_earn + deposit_amt
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))

                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + deposit_amt,acc_status='closed' WHERE acc_no = %s"
                cursor.execute(update_query, (acc_no,))
                update_query2 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query2, (deposit_amt,acc_payable,))
                cursor.execute("select balance from savingsacc where acc_no=%s",(acc_payable,))
                updated_balance1=cursor.fetchone()[0]
                cursor.fetchall()
                transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values1 = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance1,current_date)
                cursor.execute(transaction1, transaction_values1)
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                
                print("2.Interest earnings updated with deposit amount for account:", acc_no)


        elif deposit_type == 'yearly':
            print('===================yearly================')
            # years_diff = last_transaction_date.year - current_date.year
            years_diff = last_transaction_date
            if current_date == years_diff:
                cursor.execute("SELECT acc_to FROM depositacc where acc_status='active'")
                deposit_accounts1 = cursor.fetchone()
                acc_to=deposit_accounts1[0]
                cursor.fetchall()

                

                
                interest_earned = interest_amt * 12
               

                updated_balance=int(balance)+int(interest_earned)
                # Update the interest_earn field in the table
                maturity_date = current_date + datetime.timedelta(days=365)
                formatted_maturity_date = maturity_date.strftime("%d-%m-%y")
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s and acc_status='active'"
                cursor.execute(update_query, (interest_earned, formatted_maturity_date, acc_no))
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))
                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                update_query1 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query1, (interest_earned,acc_to,))
                transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance,current_date)
                cursor.execute(transaction, transaction_values)
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                
                print("1)Interest earnings updated ",interest_amt,"successfully for account:", acc_no)
                updates_made = True

            if last_transaction_date >= maturity_date:
                cursor.execute("SELECT acc_to FROM depositacc where acc_status='active'")
                deposit_accounts1 = cursor.fetchone()
                acc_to=deposit_accounts1[0]
                cursor.fetchall()
                interest_earned = interest_amt
                
        # Update the interest_earn field with interest_earn + deposit_amt
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))

                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + deposit_amt,acc_status='closed' WHERE acc_no = %s"
                cursor.execute(update_query, (acc_no,))
                update_query2 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query2, (deposit_amt,acc_to,))
                cursor.execute("select balance from savingsacc where acc_no=%s", (acc_to,))
                updated_balance1_row = cursor.fetchone()
                print("balance new=====",updated_balance1_row)

                if updated_balance1_row is not None:
                    updated_balance1 = updated_balance1_row[0]
                    # Rest of your code that uses updated_balance1
                else:
                    updated_balance1=0
                cursor.fetchall()
                transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values1 = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance1,current_date)
                cursor.execute(transaction1, transaction_values1)
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                
                print("2.Interest earnings updated with deposit amount for account:", acc_no)
            

        elif deposit_type == 'quarterly':
            print('===================yearly================')
            # years_diff = last_transaction_date.year - current_date.year
            cursor.execute("SELECT acc_to FROM depositacc where acc_status='active'")
            deposit_accounts1 = cursor.fetchone()
            acc_to=deposit_accounts1[0]
            cursor.fetchall()

            years_diff = last_transaction_date
            if current_date == years_diff:
                # Calculate the interest earned based on the interest amount
                # interest_earned = interest_amt * years_diff
                interest_earned = interest_amt * 3

                updated_balance=int(balance)+int(interest_earned)
                # Update the interest_earn field in the table
                maturity_date = current_date + datetime.timedelta(days=90)
                formatted_maturity_date = maturity_date.strftime("%d-%m-%y")
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + %s, last_transaction_date = %s WHERE acc_no = %s and acc_status='active'"
                cursor.execute(update_query, (interest_earned, formatted_maturity_date, acc_no))
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))
                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                transaction = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance,current_date)
                cursor.execute(transaction, transaction_values)
                update_query1 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query1, (interest_earned,acc_to,))
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                print("1)Interest earnings updated ",interest_amt,"successfully for account:", acc_no)
                updates_made = True

            if last_transaction_date >= maturity_date:
                cursor.execute("SELECT acc_to FROM depositacc where acc_status='active'")
                deposit_accounts1 = cursor.fetchone()
                acc_to=deposit_accounts1[0]
                cursor.fetchall()

                
                interest_earned = interest_amt
        # Update the interest_earn field with interest_earn + deposit_amt
                cursor.execute("select customer_id from depositacc where acc_no=%s",(acc_no,))

                cid=cursor.fetchone()[0]
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                cursor.execute("select deposit_id from depositacc where acc_no=%s",(acc_no,))
                deposit_id=cursor.fetchone()[0]
                update_query = "UPDATE depositacc SET interest_earn = interest_earn + deposit_amt,acc_status='closed' WHERE acc_no = %s"
                cursor.execute(update_query, (acc_no,))
                update_query2 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query2, (deposit_amt,acc_to,))
                cursor.execute("select balance from savingsacc where acc_no=%s",(acc_to,))
                updated_balance1=cursor.fetchone()[0]
                cursor.fetchall()
                transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values1 = (cid,deposit_id,bid,trans_no,interest_earned,updated_balance1,current_date)
                cursor.execute(transaction1, transaction_values1)
                
                print("2.Interest earnings updated with deposit amount for account:", acc_no)

        elif deposit_type == 'maturity':
            print('===================Maturity payment================')
            cursor.execute("SELECT acc_to FROM depositacc where acc_status='active'")
            deposit_accounts1 = cursor.fetchone()
            acc_to=deposit_accounts1[0]
            cursor.fetchall()

            
            if last_transaction_date >= maturity_date:
                # Calculate the total interest amount
                interest_earned = interest_amt * tenure

                # Calculate the interest earned based on the total interest amount and deposit amount
                # interest_earned = total_interest_amt + deposit_amt
                print(interest_earned)
                cursor.execute("select customer_id,deposit_id,acc_to,deposit_amt from depositacc where acc_no=%s",(acc_no,))
                deposit_details=cursor.fetchone()
                cid=deposit_details[0]
                
                deposit_id=deposit_details[1]
                
                deposit_amt1=int(deposit_details[3])
                print("deposit amouny===========",deposit_amt1)

                
                cursor.execute("SELECT branch_id FROM branch WHERE ifsc_code = (SELECT ifsccode FROM depositacc WHERE ifsccode = %s and acc_no=%s)", (ifsccode,acc_no,))
                bid = cursor.fetchone()[0]

                

                update_query = "UPDATE depositacc SET interest_earn = interest_earn + deposit_amt + %s,acc_status='closed' WHERE acc_no = %s"
                cursor.execute(update_query, (interest_earned,acc_no,))
                update_query2 = "UPDATE savingsacc SET balance = balance + %s  WHERE acc_no = %s"
                cursor.execute(update_query2, (deposit_amt1,acc_to,))
                # cursor.fetchall()
                # cursor.execute("select balance from savingsacc where acc_no=%s",(acc_payable1,))
                # updated_balance1=cursor.fetchone()
                # balance_new=updated_balance1[0]
                # print("balace==========",updated_balance1)
                cursor.fetchall()
                transaction1 = "INSERT INTO transaction (customer_id,acc_id,branch_id,t_no,t_type,amount,balance, date_time) VALUES (%s, %s,%s, %s, 'fixed deposit',%s,%s,%s)"
                transaction_values1 = (cid,deposit_id,bid,trans_no,interest_earned,deposit_amt1,current_date)
                cursor.execute(transaction1, transaction_values1)
                messages=f"you have recieved your interest amount Rs {interest_earned} for account number : {acc_no}"
                bank_messages="INSERT INTO bank_messages(customer_id,branch_id,messages,user_type,message_type,date)  VALUES ( %s, %s, %s,'customer','bank',%s)"
                bank_messages_values = (cid, bid,messages,current_date)
                cursor.execute(bank_messages, bank_messages_values)
                print("2.Interest earnings updated with deposit amount for account:", acc_no)


    db.commit()  # Commit the changes to the database
    cursor.close()
    db.close()

    return updates_made




   
