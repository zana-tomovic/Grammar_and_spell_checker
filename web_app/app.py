import io, docx, os
from pypdf import PdfReader
from fpdf import FPDF
from flask import Flask, request, render_template, send_file
from Model import TextCheckerModel

app = Flask(__name__)
text_checker_module = TextCheckerModel()

@app.route('/')
def home():
  return render_template("home.html")
    
@app.route('/text', methods=['POST', 'GET'])
def text():
  if request.method == 'POST':
    text = request.form.get('text')
    
    if text == "":
      return render_template("home.html", err="Please enter text you want to check.")
      
    corrected_text, mistakes = text_checker_module.correct_text(text)
    
    return render_template("home.html", corrected_text = corrected_text, mistakes = mistakes)
       
  return render_template("home.html")

@app.route('/file', methods=['POST', 'GET'])
def file():
  if request.method == 'POST':
    file = request.files.get('file')
    
    if not file or file.filename == '':
      return render_template("home.html", errFile="Please select a file.")
    
    filename = file.filename
    text = ""
    output_filename = "corrected_" + filename
    
    if filename.endswith(".txt"):
      text = file.read().decode('utf-8')
      corrected_text, mistakes = text_checker_module.correct_text(text)

      with open(output_filename, 'w', encoding='utf-8') as f:
        f.write(str(corrected_text))
      
    elif filename.endswith(".docx"):
      file_bytes = io.BytesIO(file.read())
      doc = docx.Document(file_bytes)
      
      text = "\n".join([p.text for p in doc.paragraphs]) 
      corrected_text, mistakes = text_checker_module.correct_text(text)

      new_doc = docx.Document()
      for line in corrected_text.split('\n'):
        new_doc.add_paragraph(line)
      
      new_doc.save(output_filename)
    
    elif filename.endswith(".pdf"):
      file_bytes = io.BytesIO(file.read())
      reader = PdfReader(file_bytes)
      
      pages_text = []
      for page in reader.pages:
        extracted = page.extract_text()
        
        if extracted:
          pages_text.append(extracted)
        
      text = "\n".join(pages_text)  
      corrected_text, mistakes = text_checker_module.correct_text(text)

      pdf = FPDF()
      pdf.add_page()

      pdf.set_font("Helvetica", size=12)
      
      pdf.multi_cell(w=0, h=10, txt=str(corrected_text))
      pdf.output(output_filename)
      
    else:
      return render_template("home.html", errFile="Unsupported file type. Please upload a .txt, .docx, or .pdf file. ")
      
    return render_template("home.html", corrected_file = output_filename, corrected_text_file = corrected_text, mistakes_file = mistakes)
       
  return render_template("home.html")

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
  file_path = os.path.join('', filename)
  
  return send_file(file_path, as_attachment = True)

if __name__ == "__main__":
    app.run(debug=True)