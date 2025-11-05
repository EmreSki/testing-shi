import os
import json
import asyncio
from dotenv import load_dotenv
from discord_self import Client

# Load environment variables
load_dotenv()

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

async def bump_with_account(account):
    """Bump with a single account"""
    client = Client()
    
    @client.event
    async def on_ready():
        print(f"Logged in as {client.user} using token: {account['token'][:10]}...")
        
        try:
            channel = await client.fetch_channel(account['channelId'])
            
            # Send slash command using the proper method
            await channel.slash_command(bot_id='302050872383242240', command='bump')
            print(f"Bump command sent successfully by {client.user}")
            
        except Exception as error:
            print(f"Failed to send bump command for token {account['token'][:10]}: {str(error)}")
        
        finally:
            await client.close()
    
    try:
        await client.start(account['token'])
    except Exception as err:
        print(f"Failed to login for token {account['token'][:10]}: {str(err)}")

async def start_bump_loop():
    """Main loop for bumping with all accounts"""
    while True:
        for account in config['accounts']:
            print(f"Processing bump for token: {account['token'][:10]}...")
            await bump_with_account(account)
            print("Waiting 5 seconds before the next bump...")
            await asyncio.sleep(5)  # Wait 5 seconds
        
        # After all tokens have sent the bump command, wait 2 hours and 15 minutes
        print("All accounts have sent the bump. Waiting 2 hours and 15 minutes before restarting...")
        await asyncio.sleep(8100)  # 2 hours 15 minutes in seconds

if __name__ == "__main__":
    asyncio.run(start_bump_loop())
