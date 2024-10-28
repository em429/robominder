## Robominder

```
Available commands:
- remind <time><h|m> <message>: Set a reminder (e.g., 'remind 1.5h take out laundry')
- list: Show all active reminders
- cancel <number>: Cancel reminder by number (get number from list command)
- help: Show this help message
```

```bash
git clone https://github.com/em429/robominder
cd robominder
docker build . -t robominder

cp .env.example .env
# Update .env with your credentials
docker run -d --restart always --env-file .env robominder
```