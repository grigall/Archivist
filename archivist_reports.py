from fpdf import FPDF
from fpdf.enums import XPos, YPos
from archivist_analysis import rpt_eoy, rpt_yoy

class PDF(FPDF):
    def header(self):
        #self.image('fox_face.png', 10, 8, 25) #filename, xpos, ypos, width
        self.set_font('helvetica', 'B', 18)
        #title_w = self.get_string_width(title) + 6
        #doc_w = self.w
        #self.set_x((doc_w - title_w) / 2)

        self.cell(0, 10, 'Book Report', border=False, new_x=XPos.CENTER, new_y=YPos.NEXT, align='C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-10)
        self.set_font('helvetica', '', 10)
        self.cell(0,10, f'Page {self.page_no()}/{{nb}}', align='C')
        
    def add_rpt_pages(self, rpt_list):
        for report in rpt_list:
            self.add_page()
            self.set_font('helvetica', '', 12)
            self.multi_cell(0, 5, report)

def print_report(SAVE_PATH, EOY_STATS, YOY_STATS):        
    #Instantiate FPDF class
    pdf = PDF('P', 'mm', 'Letter')

    #General options
    pdf.set_auto_page_break(auto=True, margin=10)
    pdf.alias_nb_pages()

    #EOY Report Pages
    eoy_reports = rpt_eoy(EOY_STATS) #Generate EOY Report Page(s)
    pdf.add_rpt_pages(eoy_reports)

    #YOY Report Pages
    if len(YOY_STATS) > 0:
        yoy_reports = rpt_yoy(YOY_STATS) #Generate YOY Report Page(s)
        pdf.add_rpt_pages(yoy_reports)
    else:
        pass

    pdf.output(SAVE_PATH)
    print("PDF Output!") #DEBUG