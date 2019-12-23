

    function showPromotion(){
        var fieldid = $('#move-src').val();
        var piece = $('#' + fieldid).attr("value");
        if( piece == 'wPw' ){
            var row = $('#move-dst').val();
            if( row.charAt(1) == '8' ){
                $('#white-pieces').removeClass("invisible");
                $('#prom-piece').removeAttr("readonly");
                return true;
            }
        }
        else if( piece == 'bPw' ){
            var row = $('#move-dst').val();
            if( row.charAt(1) == '1' ){
                $('#black-pieces').removeClass("invisible");
                $('#prom-piece').removeAttr("readonly");
                return true;
            }
        }

        return false;
    }

    function performMove(){
        $('#board > div').click(function(){
            if( $(this).hasClass("marked") ){
                $(this).removeClass("marked");
                $('#white-pieces').addClass("invisible");
                $('#black-pieces').addClass("invisible");
                $('#prom-piece').attr("readonly", "readonly");
                if( $('#move-dst').val().trim() == $(this).attr("id") ){
                    $('#move-dst').val("");
                }
                else if( $('#move-src').val().trim() == $(this).attr("id") ){
                    $('#move-src').val("");
                    $('#move-dst').val("");
                }
            }
            else{
                $(this).addClass("marked");
                var src = $('#move-src').val();
                if(! src.trim() ){
                    $('#move-src').val($(this).attr("id"));
                }
                else{
                    $('#move-dst').val($(this).attr("id"));
                    if(showPromotion() == false){
                        $("#move").submit();
                    }
                }
            }
        });
    }
    
    
    function drag() {
        $('.draggable').draggable({
          start: function( event, ui ){
            var src = $(this).parent().attr("id");
            $('#move-src').val( src );
          }
        });
    }

    function drop() {
        $('.droppable').droppable({
          drop: function( event, ui ) { 
              var dst1 = $(this).attr("id");
              $('#move-dst').val( dst1 );

              var src1 = $('#move-src').val();
              if( src1.trim() == dst1.trim() ){
                $('#move-src').val("");
                $('#move-dst').val("");
              }else{
                if(showPromotion() == false){
                    $("#move").submit(); 
                }
              }
          }
        });
    }

    function addThreeMins(fmttime) {
        var ary_time = fmttime.split(":");
        var secs = parseInt(ary_time[2]);
        var mins = parseInt(ary_time[1]) * 60;
        var hours = parseInt(ary_time[0]) * 3600;
        var newtime = hours + mins + secs + 3;
        hours = parseInt(newtime / 3600);
        mins = parseInt(newtime % 3600 / 60);
        secs = parseInt(newtime % 3600 % 60);
        var str_hours = hours.toString();
        var str_mins = mins.toString();
        var str_secs = secs.toString();
        if(str_hours.length == 1){
            str_hours = "0" + str_hours;
        }
        if(str_mins.length == 1){
            str_mins = "0" + str_mins;
        }
        if(str_secs.length == 1){
            str_secs = "0" + str_secs;
        }
        return str_hours + ":" + str_mins + ":" + str_secs;
    }

