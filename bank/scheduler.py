from apscheduler.schedulers.background import BackgroundScheduler
from update_interest_earn import update_interest_earn

# Create a scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# Define the job for updating interest earnings
def update_interest_earn_job():
    update_interest_earn()

# Add the job to the scheduler
scheduler.add_job(update_interest_earn_job, trigger='interval', seconds=5, max_instances=1, misfire_grace_time=30)  # Run every 50 seconds
# import time
# from apscheduler.schedulers.background import BackgroundScheduler
# from update_interest_earn import update_interest_earn

# # Create the scheduler instance
# scheduler = BackgroundScheduler()

# # Flag to track if updates were made
# updates_made = False

# def check_updates():
#     global updates_made
#     updates_made = update_interest_earn()

#     # Stop the scheduler if updates were made
#     if updates_made:
#         scheduler.shutdown()

# # Add the job to the scheduler to run every 1 minute
# scheduler.add_job(check_updates, 'interval', seconds=5)

# try:
#     # Start the scheduler
#     scheduler.start()

#     while scheduler.running:
#         # Print a message indicating that the scheduler is running
#         print("Scheduler is running...")

#         # Sleep for 1 second before printing the message again
#         time.sleep(1)

#         # Check if updates were made
#         if updates_made:
#             print("Updates were made. Stopping the scheduler...")
#             scheduler.shutdown()
#             break

# except KeyboardInterrupt:
#     # Stop the scheduler if the program is interrupted
#     scheduler.shutdown()
