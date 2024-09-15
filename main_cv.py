from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, Frame, PageTemplate, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, mm  # Add this import at the top

class Line(Flowable):
    def __init__(self, width=450):
        Flowable.__init__(self)
        self.width = width

    def draw(self):
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)

def create_cv(filename):
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#003366"),  # Navy blue color
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'subtitle',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor("#003366"),  # Navy blue color
        spaceAfter=8
    )
    
    normal_style = ParagraphStyle(
        'normal',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6
    )
    
    bullet_style = ParagraphStyle(
        'bullet',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        spaceAfter=6,
        bulletIndent=0,
        leftIndent=12
    )
    
    link_style = ParagraphStyle(
        'link',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor("#003366"),  # Navy blue color
        spaceAfter=6
    )
    
    # Center-aligned title style (now using mm for positioning)
    center_title_style = ParagraphStyle(
        'center_title',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#003366"),
        alignment=1,  # Center alignment
        spaceAfter=12
    )
    
    # Main Content
    content = []
    
    # Header (centered, with fine-tuned positioning)
    content.append(Spacer(1, 4*mm))  # Adjust top space in mm
    content.append(Paragraph('<para leftIndent="-20mm"><b>Marios Hasa</b></para>', center_title_style))
    content.append(Paragraph('<para leftIndent="-20mm">Junior FullStack Engineer</para>', center_title_style))
    content.append(Spacer(1, 3*mm))  # Adjust bottom space in mm
    
    # Contact Info with Icons (in two columns)
    contact_info = [
        [Paragraph('<img src="email.png" width="12" height="12"/> <a href="mailto:marioshasas@gmail.com">marioshasas@gmail.com</a>', link_style),
         Paragraph('<img src="phone.png" width="12" height="12"/> +30 698 844 5346', link_style)],
        [Paragraph('<img src="linkedin.png" width="12" height="12"/> <a href="https://linkedin.com/in/marios-hasa">linkedin.com/in/marios-hasa</a>', link_style),
         Paragraph('<img src="github.png" width="12" height="12"/> <a href="https://github.com/HashiraEvenus">github.com/HashiraEvenus</a>', link_style)]
    ]
    
    contact_table = Table(contact_info, colWidths=[3.75*inch, 3.75*inch])
    contact_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    content.append(contact_table)
    content.append(Spacer(1, 6))  # Reduced space before the line
    
    # Separator line
    content.append(Line(450))
    content.append(Spacer(1, 12))  # Reduced space after the line
    
    # Side Column for Languages and Technical Skills
    side_content = []
    side_content.append(Paragraph("Languages", subtitle_style))
    side_content.append(Paragraph(
        "English: Fluent<br/>"
        "Greek: Native<br/>"
        "Albanian: Native", normal_style))
    side_content.append(Spacer(1, 12))
    
    side_content.append(Paragraph("Technical Skills", subtitle_style))
    side_content.append(Paragraph(
        "<b>Languages:</b> Python, SQL, C#<br/>"
        "<b>Frameworks:</b> React, Material-UI, TailwindCSS<br/>"
        "<b>Tools:</b> GitHub, Tkinter, Unity<br/>"
        "<b>Databases:</b> MySQL, SQLite<br/>"
        "<b>Methodologies:</b> Agile", normal_style))
    
    # Add empty spaces to fill the rest of the side column
    for _ in range(20):  # Adjust this number as needed
        side_content.append(Spacer(1, 12))

    # Main Column Content
    main_content = []
    
    # Professional Summary
    main_content.append(Paragraph("Professional Summary", subtitle_style))
    main_content.append(Paragraph(
        "<b>Fullstack Engineer</b> at the University of Nicosia with expertise in Python, SQL, and front-end technologies like React, HTML, CSS, Tailwind, and Material-UI. "
        "I actively develop personal projects, including a docx reader and a Python-based weather forecast app, while exploring AI integration. "
        "With a passion for game development, I've built an indie game from scratch and continue to deepen my knowledge of C# and game development through smaller projects.",
        normal_style))
    main_content.append(Spacer(1, 12))
    
    # Professional Experience
    main_content.append(Paragraph("Professional Experience", subtitle_style))
    main_content.append(Paragraph("Junior Front-end Developer", normal_style))
    main_content.append(Paragraph("University of Nicosia, Remote", normal_style))
    main_content.append(Paragraph("October 2023–Present", normal_style))

    # Bullet points for experience
    bullet_points = [
        "Primarily responsible for front-end development, frequently completing tasks at a senior engineer level, ensuring responsive, user-friendly interfaces.",
        "Expanded expertise in front-end technologies such as React, HTML, CSS, Tailwind, and Material-UI, focusing on building dynamic components and refining the user experience.",
        "Occasionally handled backend tasks (around once every 20 days), primarily fixing front-end related issues and performing minor backend development using Python and SQL.",
        "Actively collaborated in an Agile environment, participating in regular sprint meetings, planning sessions, and retrospectives to enhance team productivity.",
        "Developed side projects, including a Syllabus project that parses docx and PDF files for improved readability, demonstrating innovation and problem-solving skills.",
        "Explored AI integration in both personal and professional projects, applying cutting-edge technology to enhance applications and stay current with industry trends."
    ]

    for point in bullet_points:
        main_content.append(Paragraph(f"<bullet>&bull;</bullet> {point}", bullet_style))

    main_content.append(Spacer(1, 12))
    
    # Education
    main_content.append(Paragraph("Education", subtitle_style))
    main_content.append(Paragraph("<b>Bachelor of Science in Computer Science</b> (Second Class Honours)", normal_style))
    main_content.append(Paragraph("<b>University of East London</b> — October 2018 – July 2021", normal_style))
    main_content.append(Spacer(1, 6))
    main_content.append(Paragraph("Relevant Coursework:", normal_style))
    main_content.append(Paragraph("<bullet>&bull;</bullet> CS50, CS50P, and CS50SQL (Harvard University courses)", bullet_style))
    main_content.append(Paragraph("<bullet>&bull;</bullet> Complete C# Unity Game Developer 2D (Udemy Course, currently undertaking)", bullet_style))
    main_content.append(Spacer(1, 12))
    
    # Projects
    main_content.append(Paragraph("Projects", subtitle_style))
    project_points = [
        "Python GUI Application (In development): A docx reader that parses and displays content using a Tkinter interface. Currently adding advanced file management features.",
        "Yoru: A fully indie game, developed entirely by myself, including artwork, sound design, and coding. It is available on my GitHub, and I integrated custom features beyond the course I followed.",
        "Snowboarder Platform Game: A small platform game hosted on my GitHub.",
        "Additional personal projects and smaller games available on GitHub."
    ]
    for point in project_points:
        main_content.append(Paragraph(f"<bullet>&bull;</bullet> {point}", bullet_style))
    main_content.append(Spacer(1, 12))
    
    # Define frames for top, side, and main content (using mm)
    top_frame = Frame(25.4*mm, 228.6*mm, 190.5*mm, 50.8*mm, id='top')

    # Side frame remains the same, as it's on the left
    side_frame = Frame(25.4*mm, 25.4*mm, 50.8*mm, 177.8*mm, id='side', showBoundary=1)

    # Main content frame with a right margin of 4mm (by reducing the width and shifting the x-position)
    main_frame = Frame(88.9*mm, 25.4*mm, 110*mm, 203.2*mm, id='main')  # Adjusted width for right margin

    # Create a page template with all frames
    template = PageTemplate(id='cv', frames=[top_frame, side_frame, main_frame])
    
    # Create a page template with all frames
    template = PageTemplate(id='cv', frames=[top_frame, side_frame, main_frame])
    doc.addPageTemplates([template])
    
    # Build PDF with content
    doc.build(content + side_content + main_content)

create_cv("cv.pdf")