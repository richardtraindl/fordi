
  function platziere_termine(wdth, tpwdth){
    var dwtagvor = -1;
    var schedule = [(24*4)]; // [(24*2)]

    $('div.termin').each( function(){
        var dautor = $(this).attr( "data-autor");
        var dwtag = $(this).attr( "data-wtag");
        var dstunde = $(this).attr( "data-stunde");
        var dviertel = $(this).attr( "data-viertel");
        var ddauer_viertel = $(this).attr( "data-dauer_viertel");

        var vwidth = wdth; // 100;
        var vheight = 10;
        var vtop = 15;
        var border = 0;
        var borderheight = 0;
        var vstageleft = 1;

        // farbe für autoren setzen
        if( dautor == "Elfi"){
            var bg = "#BBE4F3";
        }

        if( dautor == "Ordi" || dautor == "Gerold" ){
            var bg = "#FBFBB1";
        }

        if( dautor == "TP"){
            var bg = "#EDA9D5";
            vwidth = tpwdth; // 50  30
        }

        // 1) clear schedule wenn neuer tag: alle viertel stunden auf null setzen
        if( dwtag != dwtagvor){
            for( var i = (7 * 4); i < (24 * 4); i++ ){
                schedule[i] = [15];
                schedule[i][0] = 0;
                schedule[i][1] = 0;
                schedule[i][2] = 0;
                schedule[i][3] = 0;
                schedule[i][4] = 0;
                schedule[i][5] = 0;
                schedule[i][6] = 0;
                schedule[i][7] = 0;
                schedule[i][8] = 0;
                schedule[i][9] = 0;
                schedule[i][10] = 0;
                schedule[i][11] = 0;
                schedule[i][12] = 0;
                schedule[i][13] = 0;
                schedule[i][14] = 0;
            }
        }

        // 2) strutur befuellen (pro viertel stunden)
        var startzeit = Number(dstunde) * 4 + Number(dviertel);
        var endzeit = startzeit + Number(ddauer_viertel);
        var index = 0;
        for( var j = 0; j < 15; j++ ){
            if(schedule[startzeit][j] == 0){
                index = j;
                break;
            }
        }
        for( var i = startzeit; i < endzeit; i++ ){
            schedule[i][index] = 1;
        }

        if(dwtag < 10){
          leadingtag = "0";
        }
        else{
          leadingtag = "";
        }
        if(dstunde < 10){
          leadingstd = "0";
        }
        else{
          leadingstd = "";
        }
        var caltdid = '#c' + leadingtag + dwtag + "_" + leadingstd + dstunde;
        // console.log( "caltdid=" + caltdid );
        var caltd = $( caltdid );
        var px_pro_viertelstunde = 16 // caltd.height() / 4 + 0; // + 2
        dwtagvor = dwtag;
        dstundevor = dstunde;
        ddauervor = ddauer_viertel;
        // position (top und left) setzen
        if(index < 5){
            vstageleft = index;
        }
        if(index > 4 && index < 10){
            vtop = 19;
            vstageleft = (index - 5);
        }
        if(index > 9 && index < 15){
            vtop = 39;
            vstageleft = (index - 10);
        }
        // height setzen
        if( dautor == "TP"){
            vheight = 40; // 20
        }
        else{
            vheight = (px_pro_viertelstunde * Number(ddauer_viertel));
        }

        border = Number(dviertel) / 4;

        borderheight = Number(dviertel) / 4;

        var cssprops = {
            'background' : bg,
            'border' : '1px solid black',
            'position' : 'absolute',
            'width' : vwidth + 'px',
            'height' : vheight - 20 + 'px', // + borderheight
            'top' : (caltd.offset().top + 68 / 4 * Number(dviertel) + vtop) + 'px', // + border
            'left' : (caltd.offset().left + 20 * vstageleft) + 'px', // + 36 + 
            'overflow' : 'hidden'
        }

        $(this).css( cssprops );

    });
  }
