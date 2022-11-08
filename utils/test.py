from pyrogram import Client, filters

app = Client("History grabber", api_id=14823047, api_hash="e962db8176f1c7b85eab97ac8acde1e3")

async def create_group():
    async with app:
        await app.create_supergroup("Group Title2")

def main():
    app.run(create_group())


if __name__ == "__main__":
	main()
