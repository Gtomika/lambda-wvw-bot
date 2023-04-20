## Lambda WvW Bot setup

### Invite

You may invite the bot to your guilds (Discord servers) with the following link:

```
https://discord.com/api/oauth2/authorize?client_id=972523867270705172&permissions=2048&scope=bot%20applications.commands
```

This bot does not require any permissions other than sending messages to work.

### Initial setup for a guild (a.k.a. Discord server)

When the bot has joined a new server (using the link above), the following actions are recommended to be performed:

 - At first, only server administrators can change bot behaviour. The `/manager_role add` command can be used to 
authorize up to 3 roles to change bot behaviour.
 - Select the preferred locale of the guild (`/preferred_locale set`). By default, the bot will try to determine the locale from the 
user's profile who issued the command, but sometimes this is not possible: in these cases, the guild's preferred locale is used.
 - Select up to 3 "wvw roles" using `/wvw_role add`. Members with such roles will get the pings about WvW reminders.
 - Choose a home world for the guild with `/home_world set`. This world will act as a default value for all commands 
where a world is required. Population of this world is also tracked.

It is recommended you set up to 3 announcement channels (using `/announcement_channel add`). These channels 
will be used to post reminders about events and WvW related actions. You will notice that the second parameter 
of this command expects a "webhook URL". You can generate one for the selected channel at your server settings:

```Server settings -> Integrations -> Webhooks -> Create new -> Select the channel and 'copy URL'```

Without this webhook URL, the bot will not be able to post to the selected channel.

Any of these actions may be skipped, but it will hinder the bots full potential.

### Initial setup for user

The bot relies heavily on the GW2 API to read in-game data. Many API endpoints are protected with an API key. If 
you would like to use commands that require protected GW2 API, you must add your API key to the bot.

 - Keys can be generated at: https://account.arena.net/applications
 - Select at least the following permissions: **account, inventories, characters, wallet, unlocks, progression**.
Some commands may not work without these permissions.
 - Use the `/api_key set` command to give your key to the bot. It will be saved for future use. You may always 
view or delete it with `/api_key view` or `/api_key delete`, respectively.

**Please note that using API keys is safe, as it only grants read-only access to your account.**

## Lambda Wvw Bot technical info

This Discord bot performs actions related to Guild Wars 2 World versus World game mode. It runs on serverless 
architecture powered by AWS Lambda, DynamoDB, EventBridge Scheduler, API gateway and S3.

## High level overview

### Discord side

Discord key features that make this bot work:

 - Slash commands: user-friendly bot commands that that trigger **interactions** (see `commands` directory for definitions)
 - Interaction URL: A URL to which Discord will *HTTP POST* the interactions.
 - Webhooks: Allow to post messages to Discord channel through *HTTP POST*

### Bot side

 1. An API gateway is defined which listens on the interaction URL: it receives all slash command interactions.
 2. The interaction is forwarded to a Lambda function which I call `discord_interaction_lambda_function`. This function 
    acknowledges the interaction, and forwards it to a command handler lambda.
 3. Each slash command has its own lambda function: they receive interaction data from `discord_interaction_lambda_function`.
    After processing the interaction, they respond to Discord.

This architecture has the advantage that you pay only for the compute time your bot uses. No need to maintain a 
gateway that is up all the time. However, a disadvantage is that this kind of bot can only respond (to interactions, initiated 
by a user).

To send messages without an interaction, scheduled lambda functions are used, which trigger **Discord webhooks** 
to write messages to the specified channels.

### GW2 API side

The GW2 API is used to read data about the game and the users who provided API keys to the bot. Including but not limited to:

 - WvW matchup data.
 - Items in player bank or characters.
 - Achievement details and progress.

## CI/CD and IaC

A GitHub pipeline is created which runs tests, packages all lambda functions and finally: runs Terraform to 
provision the infrastructure in AWS. Slash commands are also registered by the pipeline.

Deployment to staging is an automatic action, but deployment to production or destruction of any environment 
are manual actions, that must be authorized.

## Additional invite links

Staging bot. You cannot add it, not public, just a reminder for me.

```https://discord.com/api/oauth2/authorize?client_id=968767607501115462&permissions=2048&scope=applications.commands%20bot```
