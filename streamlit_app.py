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

def opprett_ny_pdf(original_pdf, startside, sluttside, output_path):
    """Opprett og lagre en ny PDF fra et utvalg sider i den originale PDF-en."""
    original_pdf.seek(0)  # Tilbakestill strømmen til starten
    dokument = fitz.open(stream=original_pdf.read(), filetype="pdf")
    ny_pdf = fitz.open()
    ny_pdf.insert_pdf(dokument, from_page=startside, to_page=sluttside)
    ny_pdf.save(output_path)
    ny_pdf.close()
    dokument.close()

# Streamlit app
st.title("Målebrev Splitting av PDF")

# Finn brukermappen
brukermappe = os.path.expanduser("~")

# Finn "Downloads"-mappen
downloads_mappe = os.path.join(brukermappe, "Downloads")

# Opprett en ny mappe i "Downloads"
ny_mappe = os.path.join(downloads_mappe, "Splittet_malebrev")
if not os.path.exists(ny_mappe):
    os.makedirs(ny_mappe)

# Display the new folder for saving PDFs
st.write(f"Filer vil bli lagret i: {ny_mappe}")

# File uploader for the PDF
uploaded_pdf = st.file_uploader("Last opp PDF-fil", type=["pdf"])

# Button to start the process
if uploaded_pdf and st.button("Start Splitting av PDF"):
    if os.path.exists(ny_mappe):
        st.write(f"Lagring i mappen: {ny_mappe}")
        # Lese tekst fra PDF
        tekst_per_side = les_tekst_fra_pdf(uploaded_pdf)  # Bruker filobjektet direkte

        startside = 0
        for i, tekst in enumerate(tekst_per_side):
            if "Målebrev" i tekst and i > startside:
                postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
                if postnummer != "ukjent" and mengde != "ukjent":
                    filnavn = f"{postnummer}_{dato}.pdf"
                    output_sti = os.path.join(ny_mappe, filnavn)

                    # Tilbakestill strømmen før ny lesing
                    uploaded_pdf.seek(0)
                    opprett_ny_pdf(uploaded_pdf, startside, i - 1, output_sti)
                    st.success(f"Ny PDF opprettet og lagret: {output_sti}")
                else:
                    st.warning(f"Kunne ikke opprette ny PDF for side {startside} til {i - 1}, mangler nødvendig informasjon.")
                startside = i

        # Håndter siste segment
        postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
        filnavn = f"{postnummer}_{dato}.pdf"
        output_sti = os.path.join(ny_mappe, filnavn)

        # Tilbakestill strømmen før ny lesing
        uploaded_pdf.seek(0)
        opprett_ny_pdf(uploaded_pdf, startside, len(tekst_per_side) - 1, output_sti)
        st.success(f"Ny PDF opprettet og lagret: {output_sti}")
    else:
        st.error(f"Den angitte mappen eksisterer ikke. Vennligst sjekk banen og prøv igjen.")
