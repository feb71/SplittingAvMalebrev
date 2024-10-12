# Button to start the process
if uploaded_pdf and st.button("Start Splitting av PDF"):
    if os.path.exists(ny_mappe):
        st.write(f"Lagring i mappen: {ny_mappe}")
        # Lese tekst fra PDF
        tekst_per_side = les_tekst_fra_pdf(uploaded_pdf)  # Bruker filobjektet direkte

        startside = 0
        for i, tekst in enumerate(tekst_per_side):
            if "Målebrev" in tekst and i > startside:
                postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
                if postnummer != "ukjent" and mengde != "ukjent":
                    filnavn = f"{postnummer}_{dato}.pdf"
                    output_sti = os.path.join(ny_mappe, filnavn)

                    # Bruker uploaded_pdf direkte som filobjekt
                    opprett_ny_pdf(uploaded_pdf, startside, i - 1, output_sti)
                    st.success(f"Ny PDF opprettet og lagret: {output_sti}")
                else:
                    st.warning(f"Kunne ikke opprette ny PDF for side {startside} til {i - 1}, mangler nødvendig informasjon.")
                startside = i

        # Håndter siste segment
        postnummer, mengde, dato = trekk_ut_verdier(tekst_per_side[startside])
        filnavn = f"{postnummer}_{dato}.pdf"
        output_sti = os.path.join(ny_mappe, filnavn)

        # Bruker uploaded_pdf direkte som filobjekt
        opprett_ny_pdf(uploaded_pdf, startside, len(tekst_per_side) - 1, output_sti)
        st.success(f"Ny PDF opprettet og lagret: {output_sti}")
    else:
        st.error(f"Den angitte mappen eksisterer ikke. Vennligst sjekk banen og prøv igjen.")
