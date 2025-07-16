# Portainer Stack Auto-Updater

A simple tool to automate stack updates on one or more [Portainer](https://www.portainer.io/) instances. It supports Git-integrated stack updates, Portainer version upgrades, automatic cleanup of services/images, and flexible logging (console, Discord, Slack, Telegram).

Download Last Release [here](https://github.com/DiogoMarques2003/portainerStackUpdate/releases)

---

## Features

- Manage multiple Portainer instances  
- Automatically update stacks with Git integration  
- Optionally update Portainer version itself  
- Clean up unused services and Docker images  
- Ignore specific stacks from update  
- Configurable logging: Console, Discord, Slack, Telegram  
- YAML-based configuration  
- Precompiled binaries for Linux and Windows  

---

## Download

Download the latest version for your OS from the [Releases page](https://github.com/DiogoMarques2003/portainerStackUpdate/releases):  

- Linux binary: `portainerStackUpdate`  
- Windows binary: `portainerStackUpdate.exe`

Make sure the binary is executable.

Linux example usage:  
`chmod +x portainerStackUpdate`  
`./portainerStackUpdate --config path/to/config.yml`

Windows example usage (Command Prompt or PowerShell):  
`portainerStackUpdate.exe --config path\to\config.yml`

---

## Usage

Run with a configuration file:  
`./portainerStackUpdate --config path/to/config.yml`

Generate a default configuration file (optionally specifying output path):  
`./portainerStackUpdate --init-config`  
or  
`./portainerStackUpdate --init-config --config path/to/output/config.yml`

---

## Configuration (`config.yml`)

**Example:**
```yml
logging:  
  type: console                            # Options: console (default), discord, slack, telegram

  # For Discord:  
  # webhookUrl: https://discord.com/api/webhooks/...

  # For Slack:  
  # webhookUrl: https://hooks.slack.com/services/...

  # For Telegram:  
  # botToken: YOUR_BOT_TOKEN  
  # chatId: YOUR_CHAT_ID

instances:  
  - name: example  
    host: https://localhost:9443  
    accessToken: your_access_token_here  
    verifySSL: false  
    updatePortainerVersion: false  
    updateStacksWithGitIntegration: false  
    pruneServices: false  
    deleteUnusedImages: false  
    ignoreStacks:  
      - stack1  
      - stack2  
```
---

## Instances Configuration Parameters

Each item in the `instances` list represents a Portainer instance to manage. Below is a description of each parameter:

- **name** (string)  
  A friendly name to identify the Portainer instance.

- **host** (string)  
  The full URL of the Portainer API endpoint (e.g., `https://localhost:9443`).

- **accessToken** (string)  
  The access token used for authenticating with the Portainer API.

- **verifySSL** (boolean, default: false)  
  Whether to verify the SSL certificate of the Portainer host.  
  Set to `false` if using self-signed certificates.

- **updatePortainerVersion** (boolean, default: false)  
  Whether to automatically update the Portainer version on this instance.

- **updateStacksWithGitIntegration** (boolean, default: false)  
  Enables updating stacks that are linked with Git integration.

- **pruneServices** (boolean, default: false) 
  Whether to prune Docker services that are no longer referenced by any stack.

- **deleteUnusedImages** (boolean, default: false)  
  Delete unused Docker images after updating stacks to free disk space.

- **ignoreStacks** (list of strings)  
  A list of stack names to exclude from automatic updates.

---

## Logging Options

Type       | Required Config Fields  
-----------|------------------------  
console    | None  
discord    | webhookUrl  
slack      | webhookUrl  
telegram   | botToken, chatId  

---

## How to Obtain Required Credentials

### Portainer Access Token

To use the Portainer API, you need an access token. You can obtain it by logging into your Portainer instance and creating an API key or via the API directly. For detailed instructions, check the [official Portainer documentation](https://docs.portainer.io/api/access#creating-an-access-token).

### Discord Webhook URL

If you want to send notifications to Discord, you need to create an incoming webhook in your Discord server. You can learn how to do this by following [this Discord webhook guide](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

### Slack Webhook URL

To post messages to Slack, create an incoming webhook in your Slack workspace. For a step-by-step explanation, see [Slack’s official webhook documentation](https://api.slack.com/messaging/webhooks#getting_started).

### Telegram Bot Token and Chat ID

For Telegram notifications, you must create a bot using BotFather to get a bot token. You will also need the chat ID of your chat or channel. Detailed instructions for creating a bot can be found [here](https://core.telegram.org/bots#how-do-i-create-a-bot), and you can find out how to get your chat ID by checking [this StackOverflow answer](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id).

---

## Contributing

Pull requests and issues are welcome! Help improve the tool by contributing or suggesting new features.
