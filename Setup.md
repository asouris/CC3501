---
clase: Setup
creationDate: 19-03-2024
ramo: Grafica
---

## Windows

### Python

Descargamos la ultima version estable de Python aquí: https://www.python.org/downloads/windows/
![](./captures/0.png|550)

Abrimos el instalador y **TENEMOS** que seleccionar `Add python.exe to PATH`, si no lo hacen tienen que empezar de nuevo la instalación :)
![](./captures/1.png|550)
Cuando la instalación termine, habren una terminal y escriben:

``` powershell
python
```

Si todo está bien deberían obtener lo siguiente o algo similar.

``` powershell
Python 3.11.8 (tags/v3.11.8:db85d51, Feb  6 2024, 22:03:32) [MSC v.1937 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>
```

No queremos usar esto asi que cierrenlo con

``` python
>>> exit()
```

Ahora, el instalador debería haber intalado pip junto a python. Prueben si lo tienen escribiendo en la terminal

``` powershell
pip
```

Si les aparece un texto largo con comandos estan bien :).
Si les dice que el comando no existe (*no deberia pasar pero si es que pasa...*) tienen que instalar pip como dicen por aquí: https://www.liquidweb.com/kb/install-pip-windows/

### Creacion del venv

*(Para Powershell, si tienen otro shell me piden ayuda pero si tienen otro shell probablemente no necesiten mi ayuda)*

Vamos a usar los virtual environments (*venv*) de Python para contener las librerias que necesitamos.
Primero en la terminal vamos a un lugar donde queramos guardar nuestro trabajo.
Al abrir una terminal nueva siempre se van a encontrar en el `home`.
Aquí voy a crear una carpeta llamada `Grafica` con el comando `mkdir`

``` powershell
mkdir Grafica
```

Luego con el comando `cd` me muevo dentro de esa carpeta:

``` powershell
cd Grafica
```

Ahora creamos un `venv` escribiendo lo siguiente:

``` powershell
python -m venv venv
```

*Aqui el segundo venv es un nombre que ustedes pueden cambiar si quieren*
Se deberia haber creado una carpeta llamada **venv**

Ahora queremos ejecutar un script que **activa el** **venv**. Para ello, estando en la carpeta donde esta `venv` vamos a escribir:

``` powershell
venv\Scripts\Activate.ps1
```

Si esto le produce algun error, lo más probable es que por defecto windows no les permite ejecutar scripts (*medida de seguridad, no descarguen scripts random de internet porfavor*).
Para bypasear eso ejecutamos lo siguiente:

``` powershell
Set-ExecutionPolicy AllSigned -Scope CurrentUser
```

y volvemos a intentar.

Si salio bién deberían ver un parentesis de color al inicio de su linea en la terminal indicando que estan en el **venv**.

``` powershell
(venv) PS C:\Users\su_nombre\Grafica
```

### Git

Instalen Git con

``` powershell
`winget install --id Git.Git -e --source winget`
```

### Clonar repositorio

Durante las prosimas semanas les voy a subir a un repo en github ejemplos, shaders, los codigos de los aux y otras cosas utiles.
Con git pueden clonar el repositorio en su maquina. Primero copian el link.
![](./captures/2.png|550)

Al clonar el repo se les va a crear una carpeta, asi que antes, **en la terminal** vayan donde quieren colocar el repo (*vayan dentro del venv*). Luego usan `git clone` para copiar el repo

``` powershell
cd Grafica/venv/
git clone https://github.com/asouris/CC3501.git
```

## MacOs

*(Para Zsh, si tienen otro shell me piden ayuda pero si tienen otro shell probablemente no necesiten mi ayuda)*
\### Python
Mac viene con una version antigua de python. Si escriben en la terminal:

``` zsh
python3
```

Podria ser que
1. Tengan python y vean algo asi:

``` zsh
Python 3.6.6 (default, Sep 12 2018, 18:26:19)
[GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

2.  No lo tengan y pero tengan xcode y se ponga a instalarlo
3.  No lo tenga y punto

Si son el caso 3. vamos a instalarlo con **brew**. Vean si ya tienen brew con

``` zsh
brew
```

Si les dice que no conoce el comando lo instalan, si ya lo tenian sigan con la instalación.
Instalar brew es muy simple, sigan las instrucciones que hay en https://brew.sh/ *(copian lo que les dice y lo ponen en la terminal)*

Ahora instalan **python** con:

``` zsh
brew install python3
```

### Creacion del venv

Vamos a usar los virtual environments (*venv*) de Python para contener las librerias que necesitamos.
Primero en la terminal vamos a un lugar donde queramos guardar nuestro trabajo.
Al abrir una terminal nueva siempre se van a encontrar en el `home`.
Aquí voy a crear una carpeta llamada `Grafica` con el comando `mkdir`

``` powershell
mkdir Grafica
```

Luego con el comando `cd` me muevo dentro de esa carpeta:

``` powershell
cd Grafica
```

Ahora creamos un `venv` escribiendo lo siguiente:

``` zsh
python3 -m venv venv
```

*Aqui el segundo venv es un nombre que ustedes pueden cambiar si quieren*
Se deberia haber creado una carpeta llamada **venv**

Ahora queremos ejecutar un script que activa en **venv**. Para ello vamos a ejecutar:

``` zsh
source ~/Grafica/venv/bin/activate
```

*(El path puede cambiar dependiendo de como organizaron sus carpetas)*
Aparecerá **(venv)** al lado izquierdo de su prompt, indicando que dicho environment se encuentra activo.
\### Git
Instalen git ejecutando:

``` zsh
brew install git
```

### Clonar repositorio

Durante las prosimas semanas les voy a subir a un repo en github ejemplos, shaders, los códigos de los aux y otras cosas útiles.
Con git pueden clonar el repositorio en su maquina. Primero copian el link.
![](./captures/2.png|550)

Al clonar el repo se les va a crear una carpeta, asi que antes, **en la terminal** vayan donde quieren colocar el repo (*vayan dentro del venv*). Luego usan `git clone` para copiar el repo

``` bash
cd Grafica/venv
git clone https://github.com/asouris/CC3501.git
```

## Linux (Debian/Ubuntu)

*(Para bash, si tienen otro shell me piden ayuda pero si tienen otro shell probablemente no necesiten mi ayuda)*
\### Python
Primero vemos si tenemos python. Ejecuten:

``` bash
python3
```

Podria ser que
1. Tengan python y vean algo asi:

``` bash
Python 3.6.6 (default, Sep 12 2018, 18:26:19)
[GCC 8.0.1 20180414 (experimental) [trunk revision 259383]] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

2.  Les tire error y no lo tienen

Si no tienen python instalado, ejecuten en el mismo orden lo siguiente:

``` bash
sudo apt-get update
sudo apt-get install python3 python3-dev
sudo apt-get install python3-pip
sudo apt-get install python3-venv
```

### Creacion del venv

Vamos a usar los virtual environments (*venv*) de Python para contener las librerias que necesitamos.
Primero en la terminal vamos a un lugar donde queramos guardar nuestro trabajo.
Al abrir una terminal nueva siempre se van a encontrar en el `home`.
Aquí voy a crear una carpeta llamada `Grafica` con el comando `mkdir`

``` powershell
mkdir Grafica
```

Luego con el comando `cd` me muevo dentro de esa carpeta:

``` powershell
cd Grafica
```

Ahora cree el venv ejecutando:

``` bash
python3 -m venv venv
```

*Aqui el segundo venv es un nombre que ustedes pueden cambiar si quieren*
Se deberia haber creado una carpeta llamada **venv**.

Ahora queremos ejecutar un script que **activa el** **venv**. Para ello vamos a escribir:

``` bash
source ~/Grafica/venv/bin/activate
```

*(El path puede cambiar dependiendo de como organizaron sus carpetas)*
Aparecerá **(venv)** al lado izquierdo de su prompt, indicando que dicho environment se encuentra activo.

### Git

Instalen con

``` bash
sudo apt-get install git
```

### Clonar repositorio

Durante las prosimas semanas les voy a subir a un repo en github ejemplos, shaders, los códigos de los aux y otras cosas útiles.
Con git pueden clonar el repositorio en su maquina. Primero copian el link.
![](./captures/2.png|550)

Al clonar el repo se les va a crear una carpeta, asi que antes, **en la terminal** vayan donde quieren colocar el repo (*vayan dentro del venv*). Luego usan `git clone` para copiar el repo

``` bash
cd Grafica/venv
git clone https://github.com/asouris/CC3501.git
```

## Probando un ejemplo (para todos)

Con nuestro **venv activo**, vamos a instalar las librerias:

``` zsh
pip install numpy pyglet pyopengl
```

Y habiendo clonado el repositorio previamente, vamos a ejecutar un ejemplo llamado **ej_aux1.py**

``` zsh
python CC3501/ejemplos/ej_aux1.py
```

Si todo sale bien deberia habrirse una ventana y veriamos algo así:
![](./captures/3.png|550)
