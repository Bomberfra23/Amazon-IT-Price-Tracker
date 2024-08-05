import concurrent.futures
import datetime, time
from scripts.functions import task, read_data, urls, price_targets, telegram_alerts_settings, email_alerts_settings
from scripts.GUI import logo

# main functions contains the main menu and thread's pool
def main():
    print(logo)
    input("Press ENTER to starting configuration and reading data")
    read_data()
    number_of_threads = int(input("Insert the number of threads:   "))
    tasks_delay = int(input("Insert the number of seconds of delay:  "))
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}]  Action: Ready!")

    while True:
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=number_of_threads) as executor:
            results = executor.map(task, urls, price_targets, telegram_alerts_settings, email_alerts_settings) # parallelize product tasks using lists/dicts object as args
        print(f"[{timestamp}]  Info : Tasks completed in: {time.time()-start_time}")
        time.sleep(tasks_delay) # delay between tasks



if __name__ == "__main__":
  main()