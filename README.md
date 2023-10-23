# telegram-bot

Scripts for running a Dialoguem blind assembly on Telegram

Per executar-ho, feu:

```sh
./main.py config.json
```

On `config.json` és un fitxer amb el mateix format que `config_example.json`.
Ha de contenir el token del bot de Telegram;
el títol, descripció i escala del tema de l'assemblea;
els segons que té l'usuari per escriure la seva opinió
abans que se li faci un recordatori;
i exactament un avatar per cada participant, ni més ni menys.
Cal que el nombre sigui exacte perquè
el bot ho farà servir per determinar si tothom ha respost i, per tant,
si es pot passar a la ronda següent.

Els avatars són parells de noms i emojis.
Els emojis són per posar-los a la conversa i als gràfics.
Als gràfics es fan servir les imatges dels emojis de Twitter,
que es descarreguen automàticament.
Per tal de comprovar que els emojis de `config.json`
són entre les imatges descarregades, podeu fer:

```sh
./check_emojis.py config.json
```

Si no surt cap error, és que hi són tots.

L'escala per puntuar opinions s'ha de redactat de dues maneres:
La primera perquè l'usuari puntuï la seva opinió.
La segona perquè l'usuari puntuï una opinió aliena.
En aquest últim cas, es pot escriure `{subject}`
allà on es vulgui posar l'emoji de l'usuari que ha escrit l'opinió.

En cas que un usuari vulgui anar-se'n de l'assemblea, pot escriure `\leave`.
Ara bé, si se'n va sense escriure-ho i, senzillament, deixa de respondre,
la resta d'usuaris no podran acabar perquè el bot l'esperarà.
En aquest cas, convindria expulsar l'usuari que ja no respon.
Si el seu avatar és _avatar_, es pot expulsar així:

```sh
./expel.py avatar
```

Finalment, per generar diverses visualitzacions amb les dades generades,
es pot fer:

```sh
./visualization.py config.json
```
