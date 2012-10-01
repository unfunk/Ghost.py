try:
    from PyQt4.QtCore import QSizeF
    from PyQt4.QtGui import QPrinter
except ImportError:
    try:
        from PySide.QtCore import QSizeF
        from PySide.QtGui import QPrinter
    except ImportError:
        raise Exception("Ghost.py requires PySide or PyQt")

    

        
class PaperSize(object):
    """This class tells to the PdfPrinter how to render the webpage
    
    :param width: An int representing the width of the page
    :param height: An int representing the height of the page
    :param margin: a tuple of ints representing the margins of the page
        (margin_left, margin_top, margin_right, margin_bottom)
    :param orientation: landscape | portrait. This option only makes
        sense if page_type it's not None
    :param page_type: The format of the page, it can be :
        A0|A1|A2|A3|A4|A5|A6|A7|A8|A9|B0|B1|B2|B3|B4|B5|B6|B7|
        B8|B9|B10|C5E|Comm10E|DLE|Executive|Folio|Ledger|
        Legal|Letter|Tabloid|
    """
        
    def __init__(self, width, height, margin, orientation=None, page_type=None):
        self.width = width
        self.height = height
        self.margin = margin
        self.orientation = orientation
        self.page_type = page_type

class Pdf(object):
    
    def __init__(self):
        self.PAGE_TYPE = [
            ("A0", QPrinter.A0),
            ("A1", QPrinter.A1),
            ("A2", QPrinter.A2),
            ("A3", QPrinter.A3),
            ("A4", QPrinter.A4),
            ("A5", QPrinter.A5),
            ("A6", QPrinter.A6),
            ("A7", QPrinter.A7),
            ("A8", QPrinter.A8),
            ("A9", QPrinter.A9),
            ("B0", QPrinter.B0),
            ("B1", QPrinter.B1),
            ("B2", QPrinter.B2),
            ("B3", QPrinter.B3),
            ("B4", QPrinter.B4),
            ("B5", QPrinter.B5),
            ("B6", QPrinter.B6),
            ("B7", QPrinter.B7),
            ("B8", QPrinter.B8),
            ("B9", QPrinter.B9),
            ("B10", QPrinter.B10),
            ("C5E", QPrinter.C5E),
            ("Comm10E", QPrinter.Comm10E),
            ("DLE", QPrinter.DLE),
            ("Executive", QPrinter.Executive),
            ("Folio", QPrinter.Folio),
            ("Ledger", QPrinter.Ledger),
            ("Legal", QPrinter.Legal),
            ("Letter", QPrinter.Letter),
            ("Tabloid", QPrinter.Tabloid)
        ]
    
    def _get_default_dpi(self):
        # TODO: implement
        return 72
    
    def render_pdf(self, page, fileName, paperSize=None):
        """Renders the page into a pdf
        :param page: The webpage that we want to render
        :param fileName: The path where we want to save the pdf.
            For example /home/user/mypdf.pdf
        :param paperSize: An PaperSize object that will be used
            to render the webpage
        """
        mainFrame = page.currentFrame()
        
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fileName)
        printer.setResolution(self._get_default_dpi())
        
        if paperSize is None:
            ps = mainFrame.contentsSize()
            paperSize = PaperSize(width=ps.width(),
                    height=ps.width(),
                    margin=(0, 0, 0, 0),
                    orientation=None,
                    page_type=None)
            
        
        if paperSize.page_type is not None:
            if paperSize.orientation.lower() == "landscape":
                orientation = QPrinter.Landscape
            else:
                orientation = QPrinter.Portrait
            printer.setOrientation(orientation)
            
            printer.setPaperSize(QPrinter.A4) # Fallback
            for f in self.PAGE_TYPE:
                if paperSize.page_type.lower() == f[0].lower():
                    printer.setPaperSize(f[1])
                    break
        else:
            sizePt = QSizeF(paperSize.width, 
                            paperSize.height)
            printer.setPaperSize(sizePt, QPrinter.Point)
           
        printer.setPageMargins(paperSize.margin[0],
                               paperSize.margin[1],
                               paperSize.margin[2],
                               paperSize.margin[3],
                               QPrinter.Point)
        mainFrame.print_(printer)
