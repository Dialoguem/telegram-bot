# telegram-bot

Scripts for running a Dialoguem blind assembly on Telegram

Per executar-ho, feu:

```sh
python main.py xxx avatars.json
```

On `xxx` és el token de Telegram
i `avatars.json` és un fitxer amb el mateix format que `avatars_example.json`.
Cal que `avatars.json` tingui exactament un avatar per cada participant,
ni més ni menys.
Perquè el bot ho farà servir per determinar si tothom ha respost i, per tant,
si es pot passar a la ronda següent.
