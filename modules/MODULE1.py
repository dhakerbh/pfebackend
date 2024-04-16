#PDF SUMMARIZERR 

from PyPDF2 import PdfReader 
import fitz
from im_to_txt import get_text_from_image
from ai import send_to_ai

def summarize_pdf(path):
    reader = PdfReader(path) 
    extracted_text=""
    summary=""
    extracted_page_text = ""
    counter = -1
    for page in reader.pages:
        counter+=1
        if len(page.extract_text()):
            pdf_type="TEXT PDF"
            break
        if counter>=2:
            pdf_type="IMAGE PDF"
            break
    ## TEXT PDF manipulation ;)
    if(pdf_type=="TEXT PDF"):
        ##WOOORKS GOOOD "START"
        for page in reader.pages:
            extracted_page_text += page.extract_text() 
            extracted_text += extracted_page_text
            summary += send_to_ai(extracted_page_text)
    #SCANNED PDF extraction || pdf is a list of images 
    elif(len(reader.pages)):
        print('Entered ELSE phase \n')
        extracted_text = ""
        doc = fitz.open(path)
        #Summarizing each page alone
        for page in doc: 
            pix = page.get_pixmap(matrix=fitz.Identity,
                                   dpi=None,colorspace=fitz.csRGB, clip=None, annots=True)
            pix.save("PdfImage-%i.jpg" % page.number)  # save file 
            extracted_text+=get_text_from_image("PdfImage-%i.jpg" % page.number)
        summary =extracted_text 
    else:    
        summary="ERROR : Could'nt find any text "
    open(f"Summary_{path[:path.find('.')].capitalize()}.txt","w+").write(summary)
    return summary
