# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#app.py
from flask import Flask, flash, request, redirect, url_for, render_template
from werkzeug.utils import secure_filename
#import urllib.request
import os
import numpy as np
#import numpy.matlib
import cv2
import skfuzzy as fuzz
 
app = Flask(__name__)
 
UPLOAD_FOLDER = 'static/uploads/' 
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
 
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
def HEfun(Ruta):
    RUTA=str(Ruta)
    gris=cv2.imread(RUTA,0)
    histo=np.zeros(256)
    filas=gris.shape[0] #
    columnas=gris.shape[1]
    salida=np.zeros((filas,columnas))
    for i in range(filas):
        for j in range(columnas):
            pixel = int(gris[i,j])
            histo[pixel]  +=1   #ocurrencia en el univero
    pro = histo/(filas*columnas)  
    ecualiza=np.zeros(256)
    acumulado = 0
    for k in range(256):
        acumulado = pro[k] + acumulado
        ecualiza[k]=acumulado * 255.0           
    for i in range(filas):
        for j in range(columnas):
            entrada = int(gris[i,j])
            salida[i,j]=ecualiza[entrada]
    return salida
def HEBMpfun(Ruta):
    RUTA=str(Ruta)
    im=cv2.imread(RUTA,0)
    a,b = im.shape
    n_i=np.zeros((256))
    y=np.zeros((a,b))
    for i in range(a):
        for j in range(b):
            pxl=im[i,j]#Valor del pixel en la posicion (i,j)
            n_i[pxl]+=1
    pro=n_i/(a*b)
    ecualiza=np.zeros(256)
    acumulado = 0
    for k in range(256):
            acumulado = pro[k] + acumulado
            ecualiza[k]=acumulado 
    #Treshold
    G=50
    #####
    c_i=np.zeros((256))
    for i in range(a):
        for j in range(b):
            pxl=im[i,j]#Valor del pixel en la posicion (i,j)
            if pxl<=G:
                c_i[pxl]+=1
    for i in range(256):
        if c_i[i]>0:
            c_i[i]=1/c_i[i]
    L_k=np.zeros(256)
    acumulado = 0
    for k in range(256):
            acumulado = c_i[k] + acumulado
            L_k[k]=acumulado 
    N_c=sum(c_i)
    G_g=255/N_c
    L_k=L_k*G_g
    for i in range(a):
        for j in range(b):
           entrada =im[i,j]
           y[i,j]=L_k[entrada]
    return y
def FUZZYfun(Ruta):
    RUTA=str(Ruta)
    pixel = np.linspace(0, 255, 256)
    claros = fuzz.smf(pixel, 130, 230)
    grises = fuzz.gbellmf(pixel, 55, 3, 128)
    oscuros = fuzz.zmf(pixel, 25, 130)
##################################################
    s1 = 30
    s2 = 220
    s3 = 245
    salida = np.zeros(256)
    for i in range (256):
        salida [i] = ((oscuros[i]*s1)+(grises[i]*s2)+(claros[i]*s3)) / (oscuros[i]+grises[i]+claros[i])
    
    #=======================================================================#
    gris = cv2.imread(RUTA,0)
    [filas, columnas] = gris.shape
    EHF = np.zeros( (filas, columnas) )
    
    for i in range(filas):
        for j in range(columnas):
            valor = gris[i, j]
            EHF[i,j] = np.uint8(salida[valor])
    return EHF

@app.route('/')
def home():
    return render_template('index.html')
 
   
@app.route('/', methods=['POST'])
def upload_image1():
    if 'Archivo' not in request.files:
        flash('No file part')
        return redirect(request.url)
    file = request.files['Archivo']
    if file.filename == '':
        flash('No se seleccionó ninguna imagen para subir')
        return redirect(request.url)
    if file and allowed_file(file.filename):
        if request.form.get('v1') == 'HE':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            RUTA=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #########################
            salida=HEfun(RUTA)
        
            filename='process'+filename
            cv2.imwrite(os.path.join(UPLOAD_FOLDER,filename),salida)        
            flash('Imagen procesada de manera exitosa: ')
            return render_template('index.html', filename=filename)
        elif  request.form.get('v2') == 'HEBM+':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            RUTA=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #########################
            salida=HEBMpfun(RUTA)
        
            filename='process'+filename
            cv2.imwrite(os.path.join(UPLOAD_FOLDER,filename),salida)        
            flash('Imagen procesada de manera exitosa: ')
            return render_template('index.html', filename=filename)
        elif  request.form.get('v3') == 'fuzzy':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            RUTA=os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #########################
            salida=FUZZYfun(RUTA)
        
            filename='process'+filename
            cv2.imwrite(os.path.join(UPLOAD_FOLDER,filename),salida)        
            flash('Imagen procesada de manera exitosa: ')
            return render_template('index.html', filename=filename)
        else:
            pass # unknown
        
    else:
        flash('Solo imagenes con extensión: png, jpg, jpeg, gif')
        return redirect(request.url)
 
 
@app.route('/display/<filename>')
def display_image1(filename): 
    return redirect(url_for('static', filename='uploads/' + filename), code=301)


if __name__ == "__main__":
    app.run()