# -*- coding: utf-8 -*-
"""Dialoguem2023-Gefenol3-Clean.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/176JfRG2-eju7OzIHu6ddV8fWox66ZeeM
"""

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import random
import json
import os
from collections import Counter

from matplotlib.ticker import MultipleLocator
from matplotlib.colors import ListedColormap
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Arc

"""## Leer todos los datos"""

def leer_datos_ronda_1():

    # Obtén la lista de todos los nombres de archivos en la carpeta de avatares
    try:
        # Obtén la lista de todos los nombres de archivos en la carpeta de avatares
        avatar_files = os.listdir('Avatares')
    except FileNotFoundError:
        print("Error: Carpeta 'Avatares' no encontrada.")
        return None, []

    # Extrae los nombres de los avatares de los nombres de los archivos (eliminando la extensión .png)
    all_avatars = [os.path.splitext(file)[0] for file in avatar_files if file.endswith('.png')]

    if not avatar_files:
        print("Error: No se encontraron archivos de avatares con extensión .png en la carpeta 'Avatares'.")
        return None, []

    avatars = [avatar for avatar in all_avatars if os.path.exists(f"data/round_1/{avatar}.csv")]
    print(avatars)

    df_ronda = pd.DataFrame(index=avatars, columns=avatars)

    # Diccionario para almacenar las opiniones únicas de cada avatar en rondas anteriores
    opiniones_anteriores = {}

    df_autopuntuaciones = pd.read_csv(f"answers_round_1.csv", names=['avatar', 'opinion', 'autopuntuacion'])
    df_autopuntuaciones = df_autopuntuaciones[df_autopuntuaciones['avatar'].isin(avatars)]
    df_autopuntuaciones.set_index('avatar', inplace=True)

    for avatar, opinion, autopuntuacion in zip(df_autopuntuaciones.index, df_autopuntuaciones['opinion'], df_autopuntuaciones['autopuntuacion']):
        # Actualizar la opinión del avatar en el conjunto
        if avatar in opiniones_anteriores:
            print(f"Error: El avatar '{avatar}' tiene más de una opinión en 'answers_round_1.csv'.")
            raise ValueError("Inconsistencia en los datos: Algunos avatares tienen más de una opinión en 'answers_round_1.csv'.")
        else:
            opiniones_anteriores[avatar] = opinion

    # Procesamiento de los avatares
    for avatar in avatars:
        # Avatar no tiene autopuntuacion
        if avatar not in df_autopuntuaciones.index:
            print(f"Advertencia: El avatar '{avatar}' tiene un archivo en la carpeta 'round_1' pero no tiene una entrada en 'answers_round_1.csv'.")
            df_ronda.loc[:, avatar] = -1
            opiniones_anteriores[avatar] = None
        else:
            df_ronda.loc[avatar, avatar] = df_autopuntuaciones.loc[avatar, 'autopuntuacion']

        # Leer las puntuaciones que el avatar ha dado a los demás
        df_avatar = pd.read_csv(f"data/round_1/{avatar}.csv", names=['avatar', 'no_sirve', 'position'])
        for evaluated_avatar in avatars:
            if evaluated_avatar == avatar:
                continue

            # Obtener la posición del avatar evaluado, si está presente.
            position_df = df_avatar[df_avatar['avatar'] == evaluated_avatar]['position']

            if position_df.empty:
                position = -1  # Valor predeterminado si no se encuentra el avatar evaluado.
            else:
                position = position_df.iloc[0]

            df_ronda.loc[evaluated_avatar, avatar] = position

    df_ronda.fillna(-1, inplace=True)
    df_ronda = df_ronda.astype(int)

    return df_ronda, opiniones_anteriores

def leer_datos_ronda_2(opiniones_ronda_1, df_ronda_1):
    avatars = list(opiniones_ronda_1.keys())

    # 1. Inicializar df_ronda_2 con -1
    df_ronda_2 = pd.DataFrame(-1, index=avatars, columns=avatars)

    # 2. Leer el archivo 'answers_round_2.csv'
    try:
        df_autopuntuaciones = pd.read_csv("answers_round_2.csv", names=['avatar', 'opinion', 'autopuntuacion'])
    except FileNotFoundError:
        print("Error: No se encontró el archivo 'answers_round_2.csv'.")
        return None, None

    df_autopuntuaciones = df_autopuntuaciones.set_index('avatar').reindex(avatars).reset_index()

    # 2.1 Crear el diccionario opiniones_ronda_2 con las opiniones
    opiniones_ronda_2 = df_autopuntuaciones[['avatar', 'opinion']].set_index('avatar').to_dict()['opinion']

    # 2.2 Actualizar df_ronda_2 con las autopuntuaciones
    for avatar in avatars:
        if pd.isna(df_autopuntuaciones.loc[df_autopuntuaciones['avatar'] == avatar, 'autopuntuacion'].iloc[0]):
            df_ronda_2.loc[avatar, avatar] = df_ronda_1.loc[avatar, avatar]
        else:
            df_ronda_2.loc[avatar, avatar] = df_autopuntuaciones.loc[df_autopuntuaciones['avatar'] == avatar, 'autopuntuacion'].iloc[0]

    # 2.3 Comparar opiniones_ronda_2 con opiniones_ronda_1 y actualizar opiniones_ronda_2
    for avatar, opinion in opiniones_ronda_2.items():
        if pd.isna(opinion):
            opiniones_ronda_2[avatar] = None
        elif opinion == opiniones_ronda_1[avatar]:
            opiniones_ronda_2[avatar] = "Same"

    # 2.4 Comprobar si hay avatares en opiniones_ronda_1 que no están en opiniones_ronda_2 y añadirlos con valor None
    for avatar in avatars:
        if avatar not in opiniones_ronda_2:
            opiniones_ronda_2[avatar] = None
            print(f"Advertencia: El avatar '{avatar}' no está presente en 'answers_round_2.csv'.")

    # 3. Para cada avatar_1 en avatares:
    for avatar_1 in avatars:
        # 3.1 Crear una lista evaluar_avatars con todos los avatares menos avatar_1
        evaluar_avatars = [avatar for avatar in avatars if avatar != avatar_1]

        # 3.2 Leer el archivo de evaluaciones de avatar_1 si existe
        try:
            df_avatar = pd.read_csv(f"data/round_2/{avatar_1}.csv", names=['avatar', 'no_sirve', 'position'])

            for avatar_2 in avatars:
                position_df = df_avatar[df_avatar['avatar'] == avatar_2]['position']

                if not position_df.empty:
                    # 3.2.1 Si existe, poner las evaluaciones en df_ronda_2
                    df_ronda_2.loc[avatar_2, avatar_1] = position_df.iloc[0]
                    # y quitar los avatares evaluados de evaluar_avatars
                    evaluar_avatars.remove(avatar_2)

        except FileNotFoundError:
            print(f"Advertencia: No se encontró el archivo para el avatar '{avatar_1}' en la carpeta 'round_2'.")

        # 3.3 Para cada avatar_2 en evaluar_avatars:
        for avatar_2 in evaluar_avatars:
            # 3.3.1 Comprobar si su opinión es "Same" o None en opiniones_ronda_2
            if opiniones_ronda_2[avatar_2] in ["Same", None]:
                # 3.3.2 Si lo es, copiar la evaluación de avatar_1 a avatar_2 de df_ronda_1 a df_ronda_2
                df_ronda_2.loc[avatar_2, avatar_1] = df_ronda_1.loc[avatar_2, avatar_1]

    # 4. Devolver df_ronda_2 y opiniones_ronda_2
    df_ronda_2.fillna(-1, inplace=True)
    df_ronda_2 = df_ronda_2.astype(int)

    return df_ronda_2, opiniones_ronda_2

def leer_compatibilidades(num_rondas, avatars_existentes):
    compatibilidades = {avatar: {} for avatar in avatars_existentes}

    for i in range(1, num_rondas+1):
        ronda = f'ronda_{i}'
        avatars_ronda = [avatar for avatar in avatars_existentes if os.path.exists(f"data/round_{i}/{avatar}.csv")]

        for avatar in avatars_ronda:
            filepath = f"data/round_{i}/{avatar}_answer.csv"

            # Si el archivo no existe, salta a la siguiente iteración del bucle
            if not os.path.exists(filepath):
                print(f"Advertencia: no se encontró el archivo {filepath}.")
                compatibilidades[avatar][ronda] = []
                continue

            df_compatibilidad = pd.read_csv(filepath, names=['avatar', 'no_sirve', 'compatible'])
            df_compatibilidad.set_index('avatar', inplace=True)

            compatibilidades[avatar][ronda] = df_compatibilidad[df_compatibilidad['compatible'] == 'yes'].index.tolist()

    return compatibilidades

def procesar_datos():
    datos = {}
    datos['rondas'] = {}
    datos['compatibilidades'] = {}

    # Leer los datos de la ronda 1
    df_ronda_1, opiniones_ronda_1 = leer_datos_ronda_1()
    datos['rondas']['ronda_1'] = df_ronda_1

    # Leer los datos de la ronda 2
    df_ronda_2, opiniones_ronda_2 = leer_datos_ronda_2(opiniones_ronda_1, df_ronda_1)
    datos['rondas']['ronda_2'] = df_ronda_2

    # Leer las compatibilidades
    num_rondas = 2  # Número total de rondas
    avatars_existentes = df_ronda_1.index.tolist()  # La lista de avatars existentes
    datos['compatibilidades'] = leer_compatibilidades(num_rondas, avatars_existentes)

    return datos

# función auxiliar de checkeo
def leer_datos_ronda_avatar(ronda, avatar):
    df_avatar = pd.read_csv(f"data/round_{ronda}/{avatar}.csv", names=['avatar', 'no_sirve', 'position'])
    df_avatar = df_avatar.groupby('avatar').first()  # Se queda con la primera entrada para cada avatar

    return df_avatar

print(leer_datos_ronda_avatar(2, 'pumpkin'))

"""## Do it"""

datos1, opiniones1 = leer_datos_ronda_1()

datos = procesar_datos()

print(datos['compatibilidades']['pepper'])

"""## Visualizaciones"""

# Ordenar avatares en función de la autopuntuación de la primera ronda
first_ronda_df = datos['rondas']["ronda_1"]
avatars = first_ronda_df.index
avatars_sorted = avatars[np.argsort(np.diag(first_ronda_df))[::-1]]

# Crea un mapa de calor para cada ronda
for ronda, df in datos['rondas'].items():
    df_sorted = df.loc[avatars_sorted, avatars_sorted]

    fig, ax = plt.subplots(figsize=(12, 12))
    cmap = sns.color_palette("YlGnBu", 10)
    cmap.insert(0, '#808080')  # Añadir gris al comienzo para -1
    cmap = ListedColormap(cmap)
    sns.heatmap(df_sorted, cmap=cmap, annot=True, fmt="d", vmin=-1, vmax=10, cbar=False, ax=ax)

    # Mover la barra de los tics a la parte superior
    ax.xaxis.tick_top()

    # Cargar imágenes de avatares
    aux_img = []
    for avatar in df_sorted.index:
        my_name = avatar
        aux_img.append(plt.imread(f"Avatares/{my_name}.png"))

    # Configurar tamaño de las imágenes
    emoji_size = 0.6/len(df_sorted.index)

    # Remover las etiquetas de texto en los ejes
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Agregar imágenes como etiquetas en los ejes y
    for i, im in enumerate(aux_img):
        ib = OffsetImage(im, zoom=emoji_size)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, [0.25, i], frameon=False, xybox=(-0.5, i+0.5))
        ax.add_artist(ab)

    # Agregar imágenes como etiquetas en los ejes x
    for i, im in enumerate(aux_img):
        ib = OffsetImage(im, zoom=emoji_size)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, [i, 0.25], frameon=False, xybox=(i+0.5, -0.5))
        ax.add_artist(ab)

    # Guardar la figura con el título completo como nombre de archivo
    plt.savefig(f"{ronda}_puntuaciones.png", bbox_inches="tight")

# compatibles giraffe: ['dolphin', 'lion', 'elephant', 'cow', 'frog', 'monkey', 'bear', 'sheep', 'octopus']
# [10,9,5,9,6,1,5,7,6]

# Crea un mapa de calor para cada ronda
for ronda, df in datos['rondas'].items():
    df_sorted = df.loc[avatars_sorted, avatars_sorted]

    # Resta a cada fila el valor de la diagonal correspondiente
    diff_dict = {}
    for avatar in df_sorted.index:
        diff_dict[avatar] = []
        for p in df_sorted.loc[avatar]:
            if p == -1:
                diff_dict[avatar].append(-11)
            else:
                diff_dict[avatar].append(p - df_sorted.loc[avatar,avatar])

    df_diff = pd.DataFrame(diff_dict).transpose()  # Convertir el diccionario en un DataFrame y transponer

    plt.figure(figsize=(12, 12))

    # Define una lista de colores que incluye gris para el valor -11
    colors = ["grey"] + sns.color_palette("coolwarm", 21).as_hex()
    cmap = sns.color_palette(colors)
    ax = sns.heatmap(df_diff, cmap=cmap, annot=True, fmt="d", vmin=-11, vmax=10, cbar=False)

    # Mover la barra de los tics a la parte superior
    ax.xaxis.tick_top()

    # Cargar imágenes de avatares
    aux_img = []
    for avatar in df_sorted.index:
        my_name = avatar
        aux_img.append(plt.imread(f"Avatares/{my_name}.png"))

    # Configurar tamaño de las imágenes
    emoji_size = 0.6/len(df_sorted.index)

    # Remover las etiquetas de texto en los ejes
    ax.set_xticklabels([])
    ax.set_yticklabels([])

    # Agregar imágenes como etiquetas en los ejes y
    for i, im in enumerate(aux_img):
        ib = OffsetImage(im, zoom=emoji_size)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, [0.25, i], frameon=False, xybox=(-0.5, i+0.5))
        ax.add_artist(ab)

    # Agregar imágenes como etiquetas en los ejes x
    for i, im in enumerate(aux_img):
        ib = OffsetImage(im, zoom=emoji_size)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, [i, 0.25], frameon=False, xybox=(i+0.5, -0.5))
        ax.add_artist(ab)

    # Guardar la figura con el nombre del archivo que incluye "simetria"
    plt.savefig(f"{ronda}_simetria.png", bbox_inches="tight")

"""### Quién se ha movido y hacia dónde?

#### Percepción media
"""

# Crea una figura y un eje
fig, ax = plt.subplots(figsize=(12, 12))

# Lista para almacenar todos los cambios
cambios = []

# Crea un diccionario que mapee cada avatar a su índice en avatars_sorted
index_dict = {avatar: i for i, avatar in enumerate(avatars_sorted)}

# Para cada avatar
for avatar in avatars_sorted:
    i = index_dict[avatar]  # Usa el diccionario para obtener el índice correcto
    # Calcula la media de la puntuación que le han dado los otros en la ronda_1 y en la ronda_2
    media_ronda_1 = datos['rondas']['ronda_1'].loc[avatar].drop(avatar).mean()
    media_ronda_2 = datos['rondas']['ronda_2'].loc[avatar].drop(avatar).mean()

    # Calcula el cambio en la puntuación media
    cambio = media_ronda_2 - media_ronda_1

    # Agrega el cambio a la lista de cambios
    cambios.append(abs(cambio))

# Encuentra el valor absoluto máximo en la lista de cambios
cambio_max = max(cambios)

# Para cada avatar
for avatar in avatars_sorted:
    i = index_dict[avatar]  # Usa el diccionario para obtener el índice correcto
    # Calcula la media de la puntuación que le han dado los otros en la ronda_1 y en la ronda_2
    media_ronda_1 = datos['rondas']['ronda_1'].loc[avatar].drop(avatar).mean()
    media_ronda_2 = datos['rondas']['ronda_2'].loc[avatar].drop(avatar).mean()

    # Calcula el cambio en la puntuación media
    cambio = media_ronda_2 - media_ronda_1

    # Si ha habido algún cambio, dibuja flechas
    if cambio_max:
        # Normaliza el valor absoluto del cambio para obtener la intensidad del color
        if cambio_max == 0:
            color_intensity = 0
        else:
            color_intensity = color_intensity = 0.2 + 0.8 * abs(cambio) / cambio_max

        # Define el color de la flecha según el cambio
        color = (1 - color_intensity, 1 - color_intensity, 1) if cambio >= 0 else (1, 1 - color_intensity, 1 - color_intensity)

        # Dibuja una flecha que va del primer valor al segundo, con un color que depende del cambio y con un grosor mayor
        ax.arrow(media_ronda_1, i, cambio, 0, head_width=0.15, head_length=0.15, linewidth=5, fc=color, ec=color)

    # Dibuja un punto en el valor de inicio
    ax.plot(media_ronda_1, i, 'o', color='black', markersize=10)

    # Dibuja las puntuaciones medias que los otros avatars han dado al avatar considerado
    compatibles = datos['compatibilidades'][avatar]['ronda_1']
    puntuaciones_medias = [datos['rondas']['ronda_1'].loc[comp].drop(comp).mean() for comp in compatibles]

    if puntuaciones_medias:
        for puntuacion in puntuaciones_medias:
            # Dibuja una 'x' en la posición de cada puntuación media de los avatars compatibles
            ax.plot(puntuacion, i, 'x', color='black', markersize=8)

        media_comp = sum(puntuaciones_medias) / len(puntuaciones_medias)

        # Determina la dirección y, por lo tanto, el color
        if media_comp > media_ronda_1:
            color_comp = 'blue'
        else:
            color_comp = 'red'

        # Dibuja una 'X' más grande en la posición de la media de las puntuaciones medias de los avatars compatibles
        ax.plot(media_comp, i, 'X', color=color_comp, markersize=16)

# Encuentra el valor absoluto máximo en la lista de cambios
cambio_max = max(cambios)

# Cargar las imágenes de los avatares
avatar_imgs = []
for avatar in avatars_sorted:
    my_name = avatar
    avatar_img = plt.imread(f"Avatares/{my_name}.png")
    avatar_imgs.append(avatar_img)

# Configurar tamaño de las imágenes
img_size = 0.04

# Para cada avatar
for i, avatar in enumerate(avatars_sorted):
    # Dibujar la imagen de avatar como etiqueta
    ib = OffsetImage(avatar_imgs[i], zoom=img_size)
    ib.image.axes = ax
    ab = AnnotationBbox(ib, (0, i), frameon=False, xybox=(-30, 0), xycoords='data', boxcoords="offset points")
    ax.add_artist(ab)
    # Dibujar líneas grises delgadas y discontinuas correspondientes a cada avatar
    ax.axhline(i, color='gray', linestyle='--', linewidth=0.5)


# Establecer los límites del eje
ax.set_xlim(0, 10)
ax.set_ylim(len(avatars_sorted), -1)  # Línea modificada

# Establecer las etiquetas del eje
ax.set_yticks(range(len(avatars_sorted)-1, -1, -1))  # Línea modificada
ax.set_yticklabels([], fontsize=12)

# Ajustar la posición de los ticks en el eje X
ax.xaxis.set_ticks_position('bottom')
ax.xaxis.set_major_locator(MultipleLocator(1)) # Establecer el intervalo de los ticks en el eje x
ax.tick_params(axis='x', direction='out')

# Aumentar el tamaño de los números en el eje X
ax.tick_params(axis='x', labelsize=16)

# Establecer la etiqueta y título del eje X
ax.set_xlabel('Puntuació mitjana', fontsize=18)

# Guardar la figura
plt.savefig('avatar_move_mitjanes.png', bbox_inches='tight')

"""#### Percepción propia"""

# Crea una figura y un eje
fig, ax = plt.subplots(figsize=(12, 12))

# Lista para almacenar todos los cambios
cambios = []

# Extraer las rondas y compatibilidades de los datos procesados
rondas = datos['rondas']
compatibilidades = datos['compatibilidades']

# Crea un diccionario que mapee cada avatar a su índice en avatars_sorted
index_dict = {avatar: i for i, avatar in enumerate(avatars_sorted)}

# Para cada avatar
for avatar in avatars_sorted:
    i = index_dict[avatar]  # Usa el diccionario para obtener el índice correcto
    # Calcula la puntuación que el avatar ha dado a sí mismo en las rondas 1 y 2
    puntuacion_ronda_1 = rondas['ronda_1'].loc[avatar, avatar]
    puntuacion_ronda_2 = rondas['ronda_2'].loc[avatar, avatar]

    # Calcula el cambio en la puntuación
    cambio = puntuacion_ronda_2 - puntuacion_ronda_1

    # Agrega el cambio a la lista de cambios
    cambios.append(abs(cambio))

# Encuentra el valor absoluto máximo en la lista de cambios
cambio_max = max(cambios)

# Para cada avatar
for avatar in avatars_sorted:
    i = index_dict[avatar]  # Usa el diccionario para obtener el índice correcto
    # Calcula la puntuación que el avatar ha dado a sí mismo en las rondas 1 y 2
    puntuacion_ronda_1 = rondas['ronda_1'].loc[avatar, avatar]
    puntuacion_ronda_2 = rondas['ronda_2'].loc[avatar, avatar]

    # Calcula el cambio en la puntuación
    cambio = puntuacion_ronda_2 - puntuacion_ronda_1

    # Normaliza el valor absoluto del cambio para obtener la intensidad del color
    if cambio_max == 0:
        color_intensity = 0
    else:
        color_intensity = color_intensity = 0.2 + 0.8 * abs(cambio) / cambio_max

    # Define el color de la flecha según el cambio
    color = (1 - color_intensity, 1 - color_intensity, 1) if cambio >= 0 else (1, 1 - color_intensity, 1 - color_intensity)

    # Dibuja una flecha que va del primer valor al segundo, con un color que depende del cambio y con un grosor mayor
    ax.arrow(puntuacion_ronda_1, i, cambio, 0, head_width=0.15, head_length=0.15, linewidth=5, fc=color, ec=color)

    # Dibuja un punto en el valor de partida
    ax.plot(puntuacion_ronda_1, i, 'o', color='black', markersize=10)

    # Dibuja las puntuaciones que el avatar ha dado a sus avatares compatibles
    puntuaciones_comp = [rondas['ronda_1'].loc[comp, avatar] for comp in compatibilidades[avatar]['ronda_1']]
    if puntuaciones_comp:
        for puntuacion in puntuaciones_comp:
            # Dibuja una 'x' en la posición de cada puntuación
            ax.plot(puntuacion, i, 'x', color='black', markersize=8)

        media_comp = sum(puntuaciones_comp) / len(puntuaciones_comp)

        # Determina la dirección y por ende el color
        if media_comp > puntuacion_ronda_1:
            color_comp = 'blue'
        else:
            color_comp = 'red'

        # Dibuja una 'X' más grande en la posición de la media
        ax.plot(media_comp, i, 'X', color=color_comp, markersize=14)

# Cargar las imágenes de los avatares
avatar_imgs = []
for avatar in avatars_sorted:
    my_name = avatar
    avatar_img = plt.imread(f"Avatares/{my_name}.png")
    avatar_imgs.append(avatar_img)

# Configurar tamaño de las imágenes
img_size = 0.04

# Para cada avatar
for i, avatar in enumerate(avatars_sorted):
    # Dibujar la imagen de avatar como etiqueta
    ib = OffsetImage(avatar_imgs[i], zoom=img_size)
    ib.image.axes = ax
    ab = AnnotationBbox(ib, (0, i), frameon=False, xybox=(-30, 0), xycoords='data', boxcoords="offset points")
    ax.add_artist(ab)
    # Dibujar líneas grises delgadas y discontinuas correspondientes a cada avatar
    ax.axhline(i, color='gray', linestyle='--', linewidth=0.5)

# Establecer los límites del eje
ax.set_xlim(0, 10)
ax.set_ylim(len(avatars_sorted), -1)  # Línea modificada

# Establecer las etiquetas del eje
ax.set_yticks(range(len(avatars_sorted)-1, -1, -1))  # Línea modificada
ax.set_yticklabels([], fontsize=12)

# Ajustar la posición de los ticks en el eje X
ax.xaxis.set_ticks_position('bottom')
ax.xaxis.set_major_locator(MultipleLocator(1))  # Establecer el intervalo de los ticks en el eje x
ax.tick_params(axis='x', direction='out')

# Aumentar el tamaño de los números en el eje X
ax.tick_params(axis='x', labelsize=16)

# Establecer la etiqueta y título del eje X
ax.set_xlabel('Puntuació propia', fontsize=18)

# Guardar la figura
plt.savefig('avatar_move_propies.png', bbox_inches='tight')

"""## Ego-networks of compatibilities

### Average
"""

def plot_avatar_compatibles(avatar, ronda):
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(bottom=0.25)

    y_point = 1

    media_avatar = datos['rondas'][ronda].loc[avatar].mean()

    ib = OffsetImage(plt.imread(f"Avatares/{avatar}.png"), zoom=0.05)
    ib.image.axes = ax
    ab = AnnotationBbox(ib, (media_avatar, y_point+0.05), frameon=False, xybox=(0, -30), xycoords='data', boxcoords="offset points")
    ax.add_artist(ab)

    todas_las_medias = [media_avatar]

    medias_avatars = [(avatar_comp, datos['rondas'][ronda].loc[avatar_comp].mean()) for avatar_comp in datos['compatibilidades'][avatar][ronda]]
    medias_avatars = sorted(medias_avatars, key=lambda x: x[1])
    counter = Counter(media for avatar, media in medias_avatars)

    seen = {}
    for i, (avatar_comp, media_avatar_comp) in enumerate(medias_avatars):
        todas_las_medias.append(media_avatar_comp)

        # calculate y position to avoid overlapping
        if counter[media_avatar_comp] > 1:
            print('Intentamos dispersar en la posición ',media_avatar_comp)
            seen[media_avatar_comp] = seen.get(media_avatar_comp, 0) + 1
            y_pos = y_point + 0.06 + (seen[media_avatar_comp] -1) * 0.1
        else:
            y_pos = y_point + 0.06

        ib = OffsetImage(plt.imread(f"Avatares/{avatar_comp}.png"), zoom=0.03)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, (media_avatar_comp, y_pos), frameon=False, xybox=(0, -10), xycoords='data', boxcoords="offset points")
        ax.add_artist(ab)

        centro = (media_avatar + media_avatar_comp) / 2
        radio = abs(media_avatar - media_avatar_comp) / 2
        arco = Arc((centro, y_pos), radio*2, radio*2, theta1=0, theta2=180, edgecolor='grey', linestyle='--')
        ax.add_patch(arco)
    min_medias, max_medias = min(todas_las_medias), max(todas_las_medias)

    avatars_considered = [avatar] + datos['compatibilidades'][avatar][ronda]

    for avatar_comp in avatars:
        if avatar_comp in avatars_considered:
            continue

        media_avatar_comp = datos['rondas'][ronda].loc[avatar_comp].mean()

        if min_medias <= media_avatar_comp <= max_medias:
            ax.text(media_avatar_comp, y_point-0.15, '?', color='red', fontsize=20, ha='center')

    ax.set_xlim(min(todas_las_medias) - 0.5, max(todas_las_medias) + 0.5)

    y_max = (max(todas_las_medias) - min(todas_las_medias))/2. + y_point + 0.2
    ax.set_ylim(0.8, y_max)
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)  # Hacer visible el eje x
    ax.spines['left'].set_visible(False)

    ax.set_xticks(np.arange(min(todas_las_medias), max(todas_las_medias)+1))  # Mostrar más ticks en el eje x
    x_min = round(min(todas_las_medias),1) - 0.2
    x_max = round(max(todas_las_medias),1) + 0.2  # Agregamos un pequeño incremento al valor máximo

    # Use np.linspace to create an array of evenly spaced values between x_min and x_max
    x_ticks = np.linspace(x_min, x_max, num=5)
    ax.set_xticks(x_ticks)
    ax.set_xticklabels([round(x,1) for x in x_ticks])

    numero_ronda = ronda.split("_")[1]  # extrae el número de la ronda
    ax.set_title(f'Compatible Avatars in Round {numero_ronda} for avatar {avatar} \n Average Scores', fontsize=16)

    # Guardar la figura con el nombre deseado
    fig.savefig(f'compatibles_{avatar}_{ronda}.png')

avatar = 'pepper'
ronda = 'ronda_1'
plot_avatar_compatibles(avatar, ronda)

"""### Subjective"""

def plot_avatar_compatibles_subj(avatar, ronda):
    fig, ax = plt.subplots(figsize=(12, 7))
    fig.subplots_adjust(bottom=0.25)

    y_point = 1

    puntuacion_avatar = datos['rondas'][ronda].loc[avatar].loc[avatar]

    ib = OffsetImage(plt.imread(f"Avatares/{avatar}.png"), zoom=0.05)
    ib.image.axes = ax
    ab = AnnotationBbox(ib, (puntuacion_avatar, y_point+0.05), frameon=False, xybox=(0, -30), xycoords='data', boxcoords="offset points")
    ax.add_artist(ab)

    todas_las_puntuaciones = [puntuacion_avatar]

    puntuaciones_avatars = [(avatar_comp, datos['rondas'][ronda].loc[avatar_comp].loc[avatar_comp]) for avatar_comp in datos['compatibilidades'][avatar][ronda]]
    puntuaciones_avatars = sorted(puntuaciones_avatars, key=lambda x: x[1])
    counter = Counter(puntuacion for avatar, puntuacion in puntuaciones_avatars)

    seen = {}
    for i, (avatar_comp, puntuacion_avatar_comp) in enumerate(puntuaciones_avatars):
        todas_las_puntuaciones.append(puntuacion_avatar_comp)

        # calculate y position to avoid overlapping
        if counter[puntuacion_avatar_comp] > 1:
            print('Intentamos dispersar en la posición ',puntuacion_avatar_comp)
            seen[puntuacion_avatar_comp] = seen.get(puntuacion_avatar_comp, 0) + 1
            y_pos = y_point + 0.3 + (seen[puntuacion_avatar_comp] -1) * 0.3
        else:
            y_pos = y_point + 0.3

        ib = OffsetImage(plt.imread(f"Avatares/{avatar_comp}.png"), zoom=0.03)
        ib.image.axes = ax
        ab = AnnotationBbox(ib, (puntuacion_avatar_comp, y_pos), frameon=False, xybox=(0, -10), xycoords='data', boxcoords="offset points")
        ax.add_artist(ab)

        centro = (puntuacion_avatar + puntuacion_avatar_comp) / 2
        radio = abs(puntuacion_avatar - puntuacion_avatar_comp) / 2
        arco = Arc((centro, y_pos), radio*2, radio*2, theta1=0, theta2=180, edgecolor='grey', linestyle='--')
        ax.add_patch(arco)

    min_puntuaciones, max_puntuaciones = min(todas_las_puntuaciones), max(todas_las_puntuaciones)

    avatars_considered = [avatar] + datos['compatibilidades'][avatar][ronda]

    for avatar_comp in avatars:
        if avatar_comp in avatars_considered:
            continue

        puntuacion_avatar_comp = datos['rondas'][ronda].loc[avatar_comp].loc[avatar_comp]

        if min_puntuaciones <= puntuacion_avatar_comp <= max_puntuaciones:
            ax.text(puntuacion_avatar_comp, y_point-0.05, '?', color='red', fontsize=20, ha='center')

    ax.set_xlim(min(todas_las_puntuaciones) - 0.5, max(todas_las_puntuaciones) + 0.5)

    y_max = (max(todas_las_puntuaciones) - min(todas_las_puntuaciones))/2. + y_point + 0.2
    ax.set_ylim(0.8, y_max)
    ax.set_yticks([])

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)  # Hacer visible el eje x
    ax.spines['left'].set_visible(False)

    ax.set_xticks(np.arange(min(todas_las_puntuaciones), max(todas_las_puntuaciones)+1))  # Mostrar más ticks en el eje x
    ax.set_xticklabels(np.arange(min(todas_las_puntuaciones), max(todas_las_puntuaciones)+1))  # Poner los números en el eje x

    numero_ronda = ronda.split("_")[1]  # extrae el número de la ronda
    ax.set_title(f'Compatible Avatars in Round {numero_ronda} for avatar {avatar} \n Scores given by avatar {avatar}', fontsize=16)

    # Guardar la figura con el nombre deseado
    fig.savefig(f'compatibles_{avatar}_{ronda}_SUBJ.png')

avatar = 'broccoli'
ronda = 'ronda_1'
plot_avatar_compatibles_subj(avatar, ronda)

def generar_grafo(ronda, datos):
    fig, ax = plt.subplots(figsize=(20, 15))

    # Calcular la media de las puntuaciones para cada avatar y ordenarlas
    medias = datos['rondas'][ronda].mean().sort_values()
    max_dif = max(medias) - min(medias)

    # Posicionar cada avatar en el gráfico de acuerdo a su puntuación media
    for i, (avatar, media) in enumerate(medias.items()):
        ax.plot(media, 0, 'o', color='black')
        ib = OffsetImage(plt.imread(f"Avatares/{avatar}.png"), zoom=0.1)
        ib.image.axes = ax
        yoffset = 20 if i % 2 == 0 else -20
        ab = AnnotationBbox(ib, (media, 0), frameon=False, xybox=(0, yoffset), xycoords='data', boxcoords="offset points")
        ax.add_artist(ab)

    # Dibujar un arco para cada relación de compatibilidad
    for avatar_principal, compats in datos['compatibilidades'].items():
        if compats.keys():
            for avatar_compat in compats[ronda]:
                # Obtener las medias de las puntuaciones para los avatares
                media_principal = medias[avatar_principal]
                media_compat = medias[avatar_compat]

                # Calcular el centro y el radio del arco
                centro = (media_principal + media_compat) / 2
                radio = abs(media_principal - media_compat) / 2

                # Dibujar el arco en el sentido correcto y con el color correcto
                if media_principal < media_compat:
                    color = 'blue'
                    arco = Arc((centro, 0), radio*2, radio*2, theta1=0, theta2=180, edgecolor=color, linewidth=2, alpha=1-(2*radio/max_dif))
                else:
                    color = 'red'
                    arco = Arc((centro, 0), radio*2, radio*2, theta1=180, theta2=360, edgecolor=color, linewidth=2, alpha=1-(2*radio/max_dif))
                ax.add_patch(arco)

    # Ajustar los límites del gráfico
    ax.set_xlim(medias.min() - 0.2, medias.max() + 0.2)
    ax.set_ylim((medias.min()-medias.max())/2.-0.2, (medias.max()-medias.min())/2.+0.2)

    # Eliminar el eje y y el eje x
    ax.set_yticks([])
    ax.set_xticks([])

    # Remover el borde de la figura
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Guardar la figura con el nombre deseado
    fig.savefig(f'xarxa_compatibles_{ronda}.png')

#rondas = ['ronda ' + str(i+1) for i in range(num_rondas)]
rondas = ['ronda_1']
for avatar in avatars:
    for ronda in rondas:
        plot_avatar_compatibles(avatar, ronda)

#rondas = ['ronda ' + str(i+1) for i in range(num_rondas)]
rondas = ['ronda_1']
for avatar in avatars:
    for ronda in rondas:
        plot_avatar_compatibles_subj(avatar, ronda)

"""## Graphs by average positions"""

generar_grafo('ronda_1',datos)

generar_grafo('ronda_2', datos)

