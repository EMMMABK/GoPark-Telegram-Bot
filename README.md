# GoPark Bot 🚗🅿️

Welcome to the GoPark Bot README! 🎉

## Introduction ℹ️

The GoPark Bot is an AI-powered assistant built using Python and the aiogram library. It serves as an interface to the GoPark platform, an innovative service for carpooling and optimizing parking spaces.

## Features ✨

1. **Carpooling:** Find co-travelers for shared trips, reducing costs and environmental impact.
2. **Parking Optimization:** Get real-time information about available parking spaces in your area.

## Getting Started 🚀

To get started with the GoPark Bot, follow these steps:

1. Clone this repository to your local machine.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Set up environment variables:
   - `TOKEN`: Your Telegram Bot API token.
   - `ADMIN_ID`: Your Telegram user ID for admin functionalities.
   - `CLUSTER`: Connection string for your MongoDB cluster.
   - `MY_COLLECTION`: Name of the MongoDB collection.
4. Run the bot using `python bot.py`.

## Commands 🤖

- `/start`: Start the bot and register yourself.
- `/cancel`: Cancel the current action.
- `/about`: Learn more about the GoPark platform and bot.
- `/help`: Display all available bot commands.
- `/feedback`: Provide feedback, questions, or suggestions.
- `/mytrips`: View and manage your created trips.
- `/myapplies`: View and manage your trip applications.

## State Machines 🔄

The bot utilizes state machines for handling various user interactions, including:
- Registration
- Trip creation
- Trip search
- Providing feedback

## Additional Functionality 🌟

In addition to the previously mentioned features, the GoPark Bot also supports the following functionality:

- Creating trip posts
- Searching for drivers
- Viewing user account information

## Contributing 🤝

Contributions are welcome! If you have any suggestions, improvements, or bug fixes, feel free to open an issue or submit a pull request.

## About GoPark 🚙🌳

GoPark is an innovative platform aimed at making commuting convenient and environmentally sustainable. By connecting drivers and passengers, GoPark promotes shared mobility and helps users find available parking spaces in real-time.

Join us in making your city more accessible and sustainable with GoPark!

---

Thank you for choosing the GoPark Bot! If you have any questions or need assistance, feel free to reach out. Happy carpooling! 🚗👥