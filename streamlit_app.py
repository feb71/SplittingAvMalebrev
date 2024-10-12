# Input for the folder path
output_directory = st.text_input("Skriv inn mappenavn der PDF-filer skal lagres (Shift + Høyreklikk -> Kopier som bane)", "")

# Konverter til rå streng
output_directory = r"{}".format(output_directory)  # Sikrer at backslashes tolkes riktig

# Debug: Display the path entered by the user
st.write(f"Mappen som ble angitt er: {output_directory}")

# Button to start the process
if uploaded_pdf and output_directory and st.button("Start Splitting av PDF"):
    if os.path.exists(output_directory):
        st.write(f"Lagring i mappen: {output_directory}")
        # Lese tekst fra PDF
        tekst_per_side = les_tekst_fra_pdf(uploaded_pdf)

        startside = 0
        for i, tekst in enumerate(tekst_per_side):
            if "Målebrev" in tekst and i > startside:  # Korrigert "i" til "in"
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
        st.error(f"Den angitte mappen eksisterer ikke. Vennligst sjekk banen og prøv igjen. Mappen som ble angitt er: {output_directory}")
