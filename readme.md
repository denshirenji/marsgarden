Marsgarden
Video Demo: https://www.youtube.com/watch?v=3A_kZRshA5g
Description:
Here is my CS50x project! Thank you a million times to CS50x for being totally awesome.

This app queries the Nasa Insight mars lander API for weather from mars. Then, you can buy and sell mars garden plants. The weather affects how the plants grow, then if you're lucky, you can sell the plants for more than you bought them.

Here is a breakdown of what's in the app:

1. The app queries the NASA insight mars lander API https://api.nasa.gov/assets/insight/InSight%20Weather%20API%20Documentation.pdf for the weather on mars. You can see this function in helpers.py. The function name is weatherCheck(). The information comes as a dictionary of dictionaries. Based on the Sol (sol means the day on mars), you can get average temperature, max temperature, average temperature, and the same for wind speed and pressure.

2. Marsgarden allows you to buy and sell mars plants. Each mars plant has it's own attributes. You can see the list of attributes for each garden item in the dictionary of dictionaries starting on line 32 called gardenItems2. You can see the min temperature each plant can withstand, the max windspeed, and so on. You can also see other attributes, such as the picture name that is associated with the plant so we can automatically load up the associated picture by calling the dictionary.

3. The home page, at / or "index.html", shows the most recent mars weather and a brief summary of the app.

4. Browse shows a catalogue of all of the plants you can buy in a responsive table. The table automatically resizes and has a scroll bar when displayed on smaller screens or mobile.

5. Mygarden is the most interesting page. Whenever you load my garden, it queries the date and the mars weather. It then runs through all of the garden items in your garden and evaluates weather or not they are affected by the time and weather changes. If it's been longer than a day on earth since you last loaded the page "/mygarden", your garden item gets another level. If it's been longer than a day on mars since you last loaded the page "/mygarden", your garden item gets another level. If you have new mars data then your plants get evaluated against the weather. If you don't have new data, the plants don't get reevaluated. Then, all of the up-to-date listings are shown on the dynamic table. On the table you can see your plant's petname, the selling price, and the level. The selling price is calculated as a multiplier of the plant's level, where each unique plant type has it's own price multiplier.

6. My account is where you can see how much marscoin you have left, as well as change your password for security reasons. The "post" method will update your password in the user table.

- The mars weather API only updates about once a week. I'm excited for when they can update it more often.

- All of the data is held in two SQL tables "users" and "garden" joined by a primary/foreign key. Every garden item is unique, as they all have unique ages and levels. As a result, each row in the garden table has a quantity of 1. 

- Passwords are created using hash_password from werkzeug.security.

- The app is built on flask, python, and bootstrap. Bootstrap enables Mobile browsing. 

- A major success of this project was learning to develop an app via VS code rather than on an IDE.

Next steps: 
1. host it on AWS via github
2. Learn about segment()
3. Improve mobile browsing