## Lambda Wvw Bot

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

## CI/CD and IaC

A GitHub pipeline is created which runs tests, packages all lambda functions and finally: runs Terraform to 
provision the infrastructure in AWS. Slash commands are also registered by the pipeline.

## Invite links

Staging bot. You cannot add it, not public.

```https://discord.com/api/oauth2/authorize?client_id=968767607501115462&permissions=2048&scope=applications.commands%20bot```

Live bot. TODO

