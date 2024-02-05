# telegram-bot

_Dialoguem_ és un bot de Telegram per fer assemblees anònimes
on un grup de gent opina sobre un tema concret,
veu les opinions dels altres
i pot canviar d'opinió diversos cops.
Les dades generades pel bot permeten visualitzar
tant els canvis d'opinió
com les percepcions que tenen els usuaris de les opinions dels altres.

## Ús

Per executar-ho, feu:

```sh
./main.py config.json
```

On `config.json` és un fitxer amb el mateix format que `config_example.json`.
Ha de contenir el token del bot de Telegram;
el títol i escala del tema de l'assemblea;
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

Algun cop ha passat que, per problemes d'Internet,
es perd algun missatge que envia el bot.
Llavors, el bot s'encalla perquè espera
que l'usuari respongui un missatge que no ha rebut.
Per sortir d'aquest atzucac, l'usuari pot escriure `\repeat`
i el bot tornarà a enviar el missatge.

Finalment, per generar diverses visualitzacions amb les dades generades,
es pot fer:

```sh
./visualization.py config.json
```

## Bot

Quan la conversa encara no ha començat, l'usuari veu un xat buit
amb un botó que diu _START_.
Quan l'usuari el prem, s'envia automàticament una comanda `/start`.
El bot dona la benvinguda a l'usuari,
li explica com s'utilitzaran les dades que generi
i li envia l'enllaç al codi.
També li demana quin avatar li ha estat assignat per tal de ser anònim.
Si l'usuari s'equivoca, li ho torna a demanar.

Quan l'usuari ja ha escrit l'avatar correctament,
el bot li explica el tema de debat i li demana que en doni l'opinió que té.
Si tarda massa en respondre, li envia un recordatori.
Un cop ha respost, que la puntuï en una escala del 0 al 10.

En aquest punt, l'assemblea ha d'esperar que tothom hagi opinat.
El bot ofereix als usuaris un botó per
provar de veure les opinions dels altres.
Si l'usuari el prem però algú encara no ha opinat,
el bot l'informa que les opinions encara no estan disponibles
i li mostra el botó per tornar-ho a provar més endavant.

Un cop ja ha respost tothom i l'usuari prem el botó,
el bot li mostra una opinió d'algú altre,
li demana que la puntuï
i, quan ho ha fet, li demana si voldria arribar a un compromís.
Això es repeteix per cada opinió del grup.

Un cop fet, el bot demana a l'usuari si vol canviar d'opinió.
En cas que digui que sí,
li demana l'opinió i que la puntuï, com abans.
Un cop fet això,
o en cas que l'usuari hagués dit que no volia canviar d'opinió,
el bot torna a esperar que tothom hagi canviat d'opinió
(o hagi decidit no fer-ho).
Un cop tothom ho ha fet,
el bot torna a mostrar les opinions dels altres
i demana el mateix que abans.

Tot aquest procediment es repeteix ronda per ronda
fins que tothom decideix mantenir l'opinió.

A part d'aquesta execució normal,
el bot està preparat per gestionar imprevistos.
Si un usuari envia una comanda que no toca,
com una consulta `/start` quan ja l'havia enviada anteriorment,
el bot l'avisa que no l'ha entès.

Un altre cas inesperat seria que el bot s'aturés inesperadament,
per exemple per un tall de corrent a l'ordinador que l'executa.
Si passa això, el bot es pot tornar a executar,
els usuaris poden tornar a enviar la comanda `/start`,
introduir l'avatar que tenien
i el bot els retornarà al punt on estaven de l'assemblea.

Si un usuari vol abandonar l'assemblea abans d'hora,
pot fer-ho amb la comanda `/leave`.
Així, el bot ja no esperarà la seva resposta per continuar amb la resta.

## Fitxers

El bot genera tres documents a `data/`:
`own_opinions.csv`, `other_opinions.csv` i `avatars_finished.csv`.
Els dos primers són necessaris per generar les visualitzacions i, per tant,
és recomanable copiar-los en algun lloc segur quan l'assemblea s'acaba.
Per començar una nova assemblea, cal esborrar-los tots tres.
Si on s'esborren, el bot continuarà allà on s'havia aturat abans.

## Visualitzacions

Amb les dades generades pel bot podem crear diferents tipus de gràfics:

* `ratings_r_g`:
  Mostra una taula on cada cel·la és
  la puntuació que ha donat el subjecte (amb l'eix a dalt)
  de l'opinió que ha escrit l'objecte (amb l'eix a l'esquerra)
  a la ronda `r`.
  Només es mostren els usuaris que pertanyen al mateix grup, `g`.

* `ratings_diff_r_g`:
  Mostra la mateixa taula, però restant de cada cel·la
  la puntuació que l'objecte s'havia donat a si mateix.
  Així doncs, ens permet veure les diferències entre
  la percepció que tenen els altres d'un usuari
  i la percepció que té ell de si mateix.

* `moves_subj_r_g`:
  Mostra els canvis d'opinió que hi ha hagut entre la ronda `r` i l'anterior.
  El punt de la fila d'un avatar, per exemple el tomàquet, mostra
  l'opinió del tomàquet a la ronda `r-1`.
  La fletxa mostra el moviment que ha fet fins la ronda `r`, és a dir,
  el final de la fletxa mostra l'opinió a la ronda `r`.

  Per entendre si aquest moviment té sentit,
  també s'inclouen les creus,
  que són les opinions que el tomàquet
  havia dit que volia arribar a un compromís.
  La creu de color és la mitjana de les creus.
  Així doncs, s'esperaria que la fletxa anés cap a la creu de color.

  Totes aquestes opinions que hem dit es posen a l'eix del 0 al 10 seguint
  com les ha puntuades l'avatar en qüestió.
  És a dir, a la fila del tomàquet, com les ha puntuades el tomàquet.

* `moves_mean_r_g`:
  Mostra el mateix gràfic que l'anterior.
  L'única diferència és que les opinions es posen a l'eix
  no com les ha puntuades cada avatar,
  sinó amb la mitjana de totes les puntuacions.
  Així doncs, una puntuació que aparegui en dues files
  (perquè dos avatars s'hi han volgut comprometre)
  apareixerà al mateix lloc a les dues files.

* `egonet_subj_r_g_avatar`:
  Mostra les opinions en funció de si l'usuari `avatar`
  s'hi ha volgut comprometre o no.
  Si si hi ha volgut comprometre,
  l'opinió està representada per un emoji gran
  que té un arc que el lliga amb el de l'usuari `avatar`.
  Si no, l'opinió està representada per un emoji petit i sense arc.

  Les opinions es posen a l'eix del 0 al 10 seguint
  com les ha puntuades l'usuari `avatar`.

* `egonet_mean_r_g_avatar`:
  Mostra el mateix gràfic que l'anterior.
  L'única diferència és que les opinions es posen a l'eix
  no com les ha puntuades l'usuari `avatar`,
  sinó com la mitjana de totes les puntuacions.

* `graph_r_g`:
  Mostra el mateix gràfic que l'anterior,
  però amb tots els compromisos que hi ha hagut,
  entre qualsevol parell d'usuaris.
  Els arcs que van cap a l'esquerra són de color vermell
  i els arcs que van cap a la dreta són de color blau.
