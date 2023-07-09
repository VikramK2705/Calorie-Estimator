from flask import Flask, flash, request,redirect,url_for,render_template
from bs4 import BeautifulSoup
import os
import datetime
import requests
from werkzeug.utils import secure_filename
import shutil


from ultralytics import YOLO
UPLOAD_FOLDER='static/uploads/'


app=Flask(__name__)
app.secret_key="secret key"
app.config['UPLOAD_FOLDER']=UPLOAD_FOLDER

app.config['MAX_CONTENT_LENGTH']=16*1024*1024

ALLOWED_EXTENSIONS= set(['png','jpg','jpeg','gif'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def fetch_calories(prediction):
    cal_list={0: 122, 1: 132, 2: 152, 3: 168 , 4: 40, 5: 44, 6: 99, 7: 130, 8: 209, 9: 142, 10: 100}
    cal=0
    for i in prediction:
        cal=cal+cal_list[i]
    print('cal ',cal)
    return cal


@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/product')
def product():
    return 'product is here'

@app.route('/',methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(request.url)
    
    file=request.files['file']

    if file.filename=='':
        flash('No images selected for uploading')
        return redirect(request.url)
    
    if file and allowed_file(file.filename):
        filename=secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
        flash('Image successefully uploaded')
        filepath=os.path.join(app.config['UPLOAD_FOLDER'],filename)
        # perform the detection
        yolo=YOLO('best.pt')
        result=yolo.predict(filepath, save=True, imgsz=640,conf=0.5)
        list_item=result[0].names
        print(list_item)
        item_index=[]
        for i in result[0].boxes:
            print(int(i.cls.item()))
            item_index.append(int(i.cls.item()))
        msg=""
        items={}
        for i in item_index:
            if list_item[i] in items.keys():
                items[list_item[i]]+=1
            else:
                items[list_item[i]]=1
                
        for j in items.keys():
            msg=msg+ str(items[j])+" "+j+", "

        print(msg)
        total_len=len(result[0].boxes)
        # display(filename)
        # return display(filename)
        folder_path='runs/detect'
        subfolders=[f for f in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path,f))]
        latest_subfolder=max(subfolders, key=lambda x: os.path.getctime(os.path.join(folder_path,x)))
        directory=folder_path+'/'+latest_subfolder
        
        filess=os.listdir(directory)

        latest_file=filess[0]
        #copying fron run/prdict to static/prediction
        shutil.copy(os.path.join(directory,latest_file),app.config['UPLOAD_FOLDER'])
        pred_filename=os.path.join(folder_path,latest_subfolder,latest_file)
    
        # 
        cal=fetch_calories(item_index)
        print()
        print('cal : ',cal)
        return render_template('index.html',filename=filename,number=total_len, calories=cal, msg=msg)
        # return display(filename)
        
    else:
        flash("Image types should be jpg jpeg..")
        return redirect(request.url)

@app.route('/display/<filename>')
def display_image(filename):
    print("xxxxx")
    print(filename)
    return redirect(url_for('static',filename='uploads/'+filename))


if __name__ == "__main__":
    app.run(debug=True)