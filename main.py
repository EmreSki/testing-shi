import asyncio
import discord
from discord.ext import tasks
import json
import os
from datetime import datetime, timedelta
import signal
import sys

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

class DiscordBumpBot:
    def __init__(self):
        self.client = discord.Client(intents=discord.Intents.default())
        self.token = config['token']
        self.servers = config['servers']
        self.bump_task = None
        
        # Setup event handlers
        self.client.event(self.on_ready)
        self.client.event(self.on_error)

    async def on_ready(self):
        print(f'✅ Logged in as {self.client.user} (ID: {self.client.user.id})')
        print('------')
        self.bump_task = self.bump_loop.start()

    async def on_error(self, event, *args, **kwargs):
        print(f'❌ Error in event {event}: {args} {kwargs}')

    async def send_bump_command(self, channel_id):
        try:
            channel = self.client.get_channel(channel_id)
            if channel is None:
                channel = await self.client.fetch_channel(channel_id)
            
            print(f'📢 Sending bump command in channel: {channel.name} (Server: {channel.guild.name})')
            
            # Using application commands - this is the modern way to send slash commands
            # Note: Self-bots can't officially use slash commands due to Discord's restrictions
            # This is an alternative approach
            await channel.send('/bump')
            print(f'✅ Bump command sent successfully in {channel.guild.name}')
            
        except discord.Forbidden:
            print(f'❌ Missing permissions in server: {channel.guild.name}')
        except discord.NotFound:
            print(f'❌ Channel not found: {channel_id}')
        except Exception as e:
            print(f'❌ Failed to send bump command: {e}')

    @tasks.loop(minutes=135)  # 2 hours 15 minutes = 135 minutes
    async def bump_loop(self):
        print(f'\n🔄 Starting bump cycle at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        for server in self.servers:
            print(f'\n📝 Processing server: {server["name"]}')
            await self.send_bump_command(server["channel_id"])
            
            # Wait 5 seconds between servers (unless it's the last one)
            if server != self.servers[-1]:
                print('⏳ Waiting 5 seconds before next server...')
                await asyncio.sleep(5)
        
        next_bump = datetime.now() + timedelta(hours=2, minutes=15)
        print(f'\n✅ All servers have been processed.')
        print(f'⏰ Next bump cycle at: {next_bump.strftime("%Y-%m-%d %H:%M:%S")}')

    @bump_loop.before_loop
    async def before_bump_loop(self):
        print('⏳ Waiting for client to be ready...')
        await self.client.wait_until_ready()

    async def start(self):
        try:
            await self.client.start(self.token)
        except KeyboardInterrupt:
            print('\n🛑 Received interrupt signal. Shutting down...')
        except Exception as e:
            print(f'❌ Failed to start client: {e}')
        finally:
            if self.bump_task:
                self.bump_task.cancel()
            await self.client.close()

# Alternative approach using discord.py-self (if needed)
class SimpleBumpBot:
    def __init__(self):
        self.token = config['token']
        self.servers = config['servers']

    async def send_bump(self):
        client = discord.Client(intents=discord.Intents.default())
        
        @client.event
        async def on_ready():
            print(f'✅ Logged in as {client.user}')
            
            for server in self.servers:
                try:
                    channel = client.get_channel(server["channel_id"])
                    if channel is None:
                        channel = await client.fetch_channel(server["channel_id"])
                    
                    print(f'📢 Sending bump in {channel.guild.name}')
                    # Try different bump command variations
                    await channel.send('!d bump')
                    await asyncio.sleep(2)
                    print(f'✅ Bump sent in {channel.guild.name}')
                    
                except Exception as e:
                    print(f'❌ Failed in {server["name"]}: {e}')
                
                # Wait between servers
                if server != self.servers[-1]:
                    await asyncio.sleep(5)
            
            await client.close()

        try:
            await client.start(self.token)
        except Exception as e:
            print(f'❌ Login failed: {e}')

    async def run_loop(self):
        print('🚀 Starting automatic bump loop...')
        
        while True:
            await self.send_bump()
            
            next_bump = datetime.now() + timedelta(hours=2, minutes=15)
            print(f'💤 Waiting 2 hours 15 minutes. Next bump: {next_bump.strftime("%Y-%m-%d %H:%M:%S")}')
            await asyncio.sleep(8100)  # 2 hours 15 minutes in seconds

def signal_handler(sig, frame):
    print('\n🛑 Received shutdown signal. Exiting...')
    sys.exit(0)

async def main():
    # Choose which bot to use
    bot = SimpleBumpBot()
    await bot.run_loop()

if __name__ == '__main__':
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Run the bot
    asyncio.run(main())
