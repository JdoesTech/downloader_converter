from backend.functions import *

while True:
    print("Welcome to my downloader")
    print("Choose what you would want to download: 1. MP4  2. MP3")
    
    try:
        choice = int(input("Enter your choice: "))          

        if choice == 1:
            url= input("Enter the URL of your desired video")
            download_mp4(url, output_path)
        elif choice == 2:
            url= input("Enter the URL of your desired audio")
            download_mp3(url, output_path)  
        else:
                print("Invalid choice. Please enter 1 or 2.") 
    except ValueError:
        print("Invalid input. Please enter a number.")   
    
    print("Would you like to exit the program? (q to quit, any other to continue)")
    exit_choice = input("Enter your choice: ")
    if exit_choice.lower() == "q":
        print("Exiting the program.")
        break
    else:
        continue    
        

        