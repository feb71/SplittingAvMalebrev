import fitz  # PyMuPDF
import re
import os
from datetime import datetime
import streamlit as st

def les_tekst_fra_pdf(pdf_file):
    """Leser tekst fra en spesifisert PDF-fil."""
    dokument = fitz.open(stream=pdf_file.read(), filetype="pdf")
    tekst_per_side = []
    for side_num in range(len(dokument)):
        side = dokument[side_num]
        tekst_per_side.append(side.get_text("text"))
    dokument.close()
    return tekst_per_side

def trekk_ut_verdier(tekst):
    """Trekk ut postnummer og mengde fra gitt tekst."""
    beskrivelse_pattern = r'Beskrivelse\s*(\d{1,2}\.\d{1,2}\.\d{2,3})'
    mengde_pattern = r'(?<=Utført pr. d.d.:\n)([\d,]+)'
    dato_pattern = r'(\d{2}\.\d{2}\.\d{4})'  # Mønster for dato

    postnummer_match = re.search(beskrivelse_pattern, tekst)
    mengde_match = re.search(mengde_pattern, tekst)
    dato_match = re.search(dato_pattern, tekst)

    postnummer = postnummer_match.group(1) if postnummer_match else "ukjent"
    mengde = mengde_match.group(1) if mengde_match else "ukjent"
    dato = datetime.strptime(dato_match.group(1), "%d.%m.%Y").strftime("%Y%m%d") if dato_match else datetime.now().strftime("%Y%m%d")

    return postnummer, mengde, dato

def opprett_ny_pdf(original_pdf_path, startside, sluttside, output_path):
    """Opprett og lagre en ny PDF fra et utvalg sider i den originale PDF-en."""
    dokument = fitz.open(original_pdf_path)
    ny_pdf = fitz.open()
    ny_pdf.insert_pdf(dokument, from_page=startside, to_page=sluttside)
    ny_pdf.save(output_path)
    ny_pdf.close()
    dokument.close()

# Streamlit app
st.title("Målebrev Splitting av PDF")

# File uploader for the PDF
uploaded_pdf = st.file_uploader("Last opp PDF-fil", type=["pdf"])

# Input for the folder path
output_directory = st.text_input("Skriv inn mappenavn der PDF-filer skal lagres (Shift + Høyreklikk -> Kopier som bane)", "")

# Button to start the process
if uploaded_pdf and output_directory and st.button("Start Splitting av PDF"):
    if os.path.exists(output_directory):
        st.write(f"Lagring i mappen: {output_directory}")

        # Lese tekst fra PDF
        tekst_per_side = les_tekst_fra_pdf(uploaded_pdf)

        startside = 0
        for i, tekst in enumerate(tekst_per_side):
            if "Målebrev" in tekst and i > startside:
                postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
                if postnummer != "ukjent" and mengde != "ukjent":
                    filnavn = f"{postnummer}_{dato}.pdf"
                    output_sti = os.path.join(output_directory, filnavn)

                    # Reopen the PDF for splitting and save the section as a new PDF
                    with open(uploaded_pdf.name, "rb") as original_pdf:
                        opprett_ny_pdf(uploaded_pdf.name, startside, i - 1, output_sti)
                    st.success(f"Ny PDF opprettet og lagret: {output_sti}")
                else:
                    st.warning(f"Kunne ikke opprette ny PDF for side {startside} til {i - 1}, mangler nødvendig informasjon.")
                startside = i

        # Håndter siste segment
        postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
        filnavn = f"{postnummer}_{dato}.pdf"
        output_sti = os.path.join(output_directory, filnavn)

        # Reopen the PDF for splitting and save the section as a new PDF
        with open(uploaded_pdf.name, "rb") as original_pdf:
            opprett_ny_pdf(uploaded_pdf.name, startside, len(tekst_per_side) - 1, output_sti)
        st.success(f"Ny PDF opprettet og lagret: {output_sti}")
    else:
        st.error("Den angitte mappen eksisterer ikke. Vennligst sjekk banen og prøv igjen.")
