## 1. Diferencia entre Python global y `.venv`.  
Python global es para todo los trabajos y .venv es un entorno independiente en el que puedes trabajar con c ualquier version d epaquetes sin afectar a las demas versiones

## 2. ¿Para qué sirve `python -m pip` frente a llamar solo a `pip`?  
con el priemro dices que el python que tu quieres ejecute el pip. Con el segundo es el python del path el que ejecuta pip por lo que puede no ser el que tu querias

## 3. Explica working tree / staging / commit.  
Working tree son los qrchivos con los que trabajas
staging son aquellos que has seleccionado para guardar y subir a tu repositorio
Commit es la ccion en la que esos archivos se guardan en el historial de versiones y que terminaras subiendo

## 4. ¿Clone y pull son lo mismo? ¿Por qué?  
Clone copia el repo de github en tu local
Pull actualiza tu repo local con lo que haya en remoto

## 5. Lista cuatro cosas que no se suben a GitHub y justifica una.  
Los environment (.venv), contraseñas o tokens, datos personales, o archivos grandes
Las contraseñas, tokens o datos personales no deben subirse ya que pueden peligrar accesos a cuentas porque cualquier persona con acceso al repositorio podria acceder a ellas.

## 6. Reescribe a buen estilo: `update`, `fix final`, `cambios varios`.  
Update--> Updated fileX with changes xxx. Added fileY
fix final --> fixed mistake xxx in fileX
cambios varios --> changed xxx in fileX, changed yyy in fileY, ...

## 7. ¿Qué haces si el IDE no importa `pandas` pero la terminal sí?  
El IDE no esta configurado con el interprete correcto

## 8. ¿Qué haces si subiste `.env` por error?
Dejar de controlar el .venv en Git. Hacer un commit. Si es necesario cambiar claves.