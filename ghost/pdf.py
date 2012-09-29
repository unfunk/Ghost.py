from PyQt4.QtGui import QPrinter

class Pdf(object):
    FORMATS = [
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
    
    def render_pdf(page, fileName):
        """Renders the page into a pdf
        :param page: The webpage that we want to render
        :param fileName: The path where we want to save the pdf.
            For example /home/user/mypdf.pdf
        """
        
        mainFrame = page.currentFrame()
        
        printer = QPrinter()
        printer.setOutputFormat(QPrinter.PdfFormat)
        printer.setOutputFileName(fileName)
        printer.setResolution(self._get_default_dpi())
        paperSize = None
    
        if paperSize is None:
            pageSize = mainFrame.contentsSize()
            paperSize = {}
            paperSize["width"] = "{0}px".format(pageSize.width())
            paperSize["height"] = "{0}px".format(pageSize.height())
            paperSize["margin"] = "0px".format(pageSize.height())
            paperSize["format"] = "A4"
            
        if False and "width" in paperSize  and "height" in paperSize:
            sizePt = (paperSize["width"], 
                                paperSize["height"])
            printer.setPaperSize(sizePt, QPrinter.Point)
        elif "format" in paperSize:
            if "orientation" in paperSize and \
                paperSize["orientation"].lower() == "landscape":
                    orientation = QPrinter.Landscape
            else:
                orientation = QPrinter.Portrait
            printer.setOrientation(orientation)
            
            printer.setPaperSize(QPrinter.A4) # Fallback
            for f in FORMATS:
                if paperSize["format"].lower() == f[0].lower():
                    printer.setPaperSize(f[1])
                    break
        else:
            return False
            
    
        if "border" in paperSize and not "margin" in paperSize:
            # backwards compatibility
            paperSize["margin"] = paperSize["border"]
    
        marginLeft = 0;
        marginTop = 0;
        marginRight = 0;
        marginBottom = 0;
    
        """
        if paperSize["margin"]:
            margins = paperSize["margin"]
            if margins.canConvert(QVariant.Map):
                mmap = margins.toMap()
                marginLeft = printMargin(mmap, "left")
                marginTop = printMargin(mmap, "top")
                marginRight = printMargin(mmap, "right")
                marginBottom = printMargin(mmap, "bottom")
            elif margins.canConvert(QVariant.String):
                margin = stringToPointSize(margins.toString())
                marginLeft = margin
                marginTop = margin
                marginRight = margin
                marginBottom = margin
        
        printer.setPageMargins(marginLeft, marginTop, marginRight, marginBottom, QPrinter.Point)
        """
        printer.setPageMargins(0, 0, 0, 0, QPrinter.Point)
        mainFrame.print_(printer)
        
        return True