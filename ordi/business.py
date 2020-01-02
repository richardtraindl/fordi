Public Function calc_Rechnung(ByVal RechnungID As Long, ByRef Brutto_Summe, ByRef Netto_Summe, ByRef Steuerbetrag_Zwanzig, ByRef Steuerbetrag_Dreizehn, ByRef Steuerbetrag_Zehn)
    Dim dbs As DAO.Database
    Dim rs As DAO.Recordset
    Dim colArtikelarten As Collection
    Dim aktsteuersatz As Single
    Dim aktnettobetrag As Single
    

    On Error GoTo calc_Rechnung_error

    Set colArtikelarten = New Collection
    Set dbs = OpenDatabase(CurrentDb.Name)
    Set rs = dbs.OpenRecordset("SELECT * FROM tblArtikelart ORDER BY ID;")
    rs.MoveFirst
    Do While Not rs.EOF
        colArtikelarten.Add (rs!Steuersatz)
        rs.MoveNext
    Loop
    rs.Close
    Set rs = Nothing

    Brutto_Summe = 0
    Netto_Summe = 0
    Steuerbetrag_Zwanzig = 0
    Steuerbetrag_Dreizehn = 0
    Steuerbetrag_Zehn = 0
    Set rs = dbs.OpenRecordset("SELECT * FROM tblRechnungzeile WHERE FK_RechnungID = " & RechnungID & ";")
    rs.MoveFirst
    Do While Not rs.EOF
        Brutto_Summe = Brutto_Summe + rs!Betrag
        ' sKey = Str(rs!FK_ArtikelartID)
        aktsteuersatz = colArtikelarten.Item(rs!FK_ArtikelartID)
        aktnettobetrag = rs!Betrag * 100 / (100 + aktsteuersatz)
        If (aktsteuersatz = 20) Then
            Steuerbetrag_Zwanzig = Steuerbetrag_Zwanzig + rs!Betrag - aktnettobetrag
        ElseIf (aktsteuersatz = 13) Then
            Steuerbetrag_Dreizehn = Steuerbetrag_Dreizehn + rs!Betrag - aktnettobetrag
        ElseIf (aktsteuersatz = 10) Then
            Steuerbetrag_Zehn = Steuerbetrag_Zehn + rs!Betrag - aktnettobetrag
        End If
        rs.MoveNext
    Loop
    
    Steuerbetrag_Zwanzig = Round(Steuerbetrag_Zwanzig, 2)
    Steuerbetrag_Dreizehn = Round(Steuerbetrag_Dreizehn, 2)
    Steuerbetrag_Zehn = Round(Steuerbetrag_Zehn, 2)
    Netto_Summe = Brutto_Summe - (Steuerbetrag_Zwanzig + Steuerbetrag_Dreizehn + Steuerbetrag_Zehn)

    rs.Close
    Set rs = Nothing
    dbs.Close
    Set dbs = Nothing
    Exit Function

calc_Rechnung_error:
    Set dbs = Nothing
End Function
