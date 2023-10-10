# telegram-bot

Scripts for running a Dialoguem blind assembly on Telegram

Per executar-ho, feu:

```sh
python main.py config.json
```

On `config.json` és un fitxer amb el mateix format que `config_example.json`.
Ha de contenir el token del bot de Telegram;
el títol, descripció i escala del tema de l'assemblea;
i exactament un avatar per cada participant, ni més ni menys.
Cal que el nombre sigui exacte perquè
el bot ho farà servir per determinar si tothom ha respost i, per tant,
si es pot passar a la ronda següent.
