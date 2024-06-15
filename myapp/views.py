import pandas as pd
from django.shortcuts import render
from .forms import UploadFileForm
from django.core.files.storage import FileSystemStorage
import os
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64

def handle_uploaded_file(f):
    
    fs = FileSystemStorage()
    filename = fs.save(f.name, f)
    file_path = fs.path(filename)
    
    
    df = pd.read_csv(file_path)
    
    
    os.remove(file_path)
    
    return df

def index(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            df = handle_uploaded_file(request.FILES['file'])
            
            
            first_rows = df.head().to_html()
            summary_stats = df.describe().to_html()
            
            
            missing_values = df.isnull().sum().to_frame(name='Missing Values').to_html()
            
            
            plots = []
            for column in df.select_dtypes(include=['float', 'int']).columns:
                plt.figure()
                sns.histplot(df[column].dropna())
                plt.title(f'Histogram of {column}')
                buffer = BytesIO()
                plt.savefig(buffer, format='png')
                buffer.seek(0)
                image_png = buffer.getvalue()
                buffer.close()
                image_base64 = base64.b64encode(image_png).decode('utf-8')
                plots.append(image_base64)
            
            context = {
                'form': form,
                'first_rows': first_rows,
                'summary_stats': summary_stats,
                'missing_values': missing_values,
                'plots': plots,
            }
            
            return render(request, 'index.html', context)
    else:
        form = UploadFileForm()
    
    return render(request, 'index.html', {'form': form})
