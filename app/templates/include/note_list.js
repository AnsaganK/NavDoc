async function createList(data, list_id, display="card"){
            let previous_number = "";
            let next_number = "";
            let empty = '';

            data["data"].forEach(
                (i) => {
                let fast = i["fast"] ? ' <i class="material-icons" style="color: #ffbd29;margin-top: 4px;position: absolute;margin-left: 20px;">offline_bolt</i>' : '';
                let file = i["files"].length>0 ? ' <i class="material-icons right">attachment</i>' : '';
                let card_color = "";
                let card_status_text = "";
                if (i["status"] == "null"){
                  //card_color = "grey !important";
                  card_status_text = "(В ожидании)";
                }else if(i.status == "success"){
                  //card_color = "#689f38 !important";
                  card_status_text = "(Подписано)";
                }else if(i.status == "edit"){
                  //card_color = "#ffc107 !important";
                  card_status_text = "(Редактирование)";
                }else if(i.status == "error"){
                  //card_color = "#ef5350 !important";
                  card_status_text = "(Отказано)";
                }
                if (display === 'card'){
                empty+= '<div class="col s12 m4">' +
                    '<div class="row row_card"> ' +
                    '<div class="col s12 m12">' +
                    '<div class="card blue-grey darken-1" style="background: '+ card_color + '"> ' +
                    '<div class="card-content white-text">' +
                    '<span class="card-title activator grey-text text-darken-4" style="color:#fff !important;">СЗ №'
                    +i["number"] +
                     card_status_text+
                        fast +
                    '<i class="material-icons right">more_vert</i>\n' +
                    '</span> ' +
                    '<p>'+i["title"]+
                    '</p>' +
                    ' </div> ' +
                    '<div class="card-action"> ' +
                    '<a href="/notes/show/isSignature/'+i["id"]+'" target="_blank">PDF</a> ' +
                    '<a class="waves-effect waves-light modal-trigger" href="#modal1" onclick="getDetailNote('+i.id+')">Подробнее</a> ' +
                    '<a href="#">' +
                    file +
                    '</a> ' +
                    '</div> ' +
                    '<div class="card-reveal" style="background-color: #546e7ab8;">' +
                        '<span class="card-title white-text text-darken-4" style="margin-top:-1px">СЗ №'+
                        i["number"]+
                        '<i class="material-icons right">close</i></span>'+
                    '<span class="card-content grey-text text-darken-4" style="color:#ffffff !important">'+
                    ''+ i["text"] +
                    '</span>'+
                    '</div>' +
                    '</div> ' +
                    '</div> ' +
                    '</div> ' +
                    '</div>';
                }else{
                  empty+=`<a class="waves-effect waves-light modal-trigger new-collection-item collection-item" href="#modal1" onclick="getDetailNote(${i.id})">СЗ №${i["number"]} - ${i["title"]}</a>`;
                }}
            );

          let previous_number_page = '<li class="disabled"><a href="#!"><i class="material-icons">chevron_left</i></a></li>';
          let next_number_page = '<li class="disabled"><a href="#!"><i class="material-icons">chevron_right</i></a></li>'
            if (data["isPrevious"]){
              previous_number = data["page"]-1;
              let new_list_id = '"'+list_id+'"'
              previous_number_page = "<li class='waves-effect'><a href='#' onclick='loadNotesList(q="+new_list_id+",page="+previous_number+")'><i class=\"material-icons\">chevron_left</i></a></li>\n" +
                      "<li class='waves-effect'><a href='#' onclick='loadNotesList(q="+new_list_id+",page="+previous_number+")'>"+
                      previous_number+
                      '</a></li>\n';
            }
            if (data["isNext"]){
              next_number = data["page"]+1;
              let new_list_id = '"'+list_id+'"'
              next_number_page =
                    "<li class='waves-effect'><a href='#' onclick='loadNotesList(q="+new_list_id+",page="+next_number+")'>"+
                      next_number+
              '</a></li>\n' +
                    "<li class='waves-effect'><a href='#' onclick='loadNotesList(q="+new_list_id+",page="+next_number+")'><i class='material-icons'>chevron_right</i></a></li>\n";
            }

                    let display_card_color = getCookie('display') === 'card'? '#ff985f' : '#546e7a';
                    let display_list_color = getCookie('display') === 'list'? '#ff985f' : '#546e7a';
            let pagination = '' +
                    '<ul class="pagination">\n' +
                    previous_number_page+
                    '    <li class="active"><a href="#!">'+
                    data["page"]+
                    '</a></li>\n' +
                    next_number_page+
                    '  </ul>\n' +
                    '<i class="material-icons" onclick="setDisplay(1,'+"'"+list_id+"'"+','+data["page"]+')" style="\n' +
                    '                    float: right;\n' +
                    '                    cursor: pointer;\n' +
                    '                    position: absolute;\n' +
                    '                    left: 10px;\n' +
                    '                    top: 120px;\n' +
                    '                    font-size: 33px;\n' +
                    '                    color: '+
                    display_card_color+
                    ';\n' +
                    '                ">apps</i>'+
                    '<i class="material-icons" onclick="setDisplay(2,'+"'"+list_id+"'"+','+data["page"]+')" style="\n' +
                    '                    float: right;\n' +
                    '                    cursor: pointer;\n' +
                    '                    position: absolute;\n' +
                    '                    left: 50px;\n' +
                    '                    top: 120px;\n' +
                    '                    font-size: 33px;\n' +
                    '                    color: '+
                    display_list_color+
                    ';\n' +
                    '                ">reorder</i>'+
                    '<i class="material-icons" style="\n' +
                    '    float: right;\n' +
                    '    cursor: pointer;\n' +
                    '    position: absolute;\n' +
                    '    right: 10px;\n' +
                    '    display: block;\n' +
                    '    top: 120px;\n' +
                    '    font-size: 33px;\n' +
                    '    color: #546e7a;\n' +
                    '">filter_list</i>'
            let list = document.getElementById(list_id);
            if (empty === ""){
                empty = "<span style='color: grey;justify-content: center;display: flex;align-items: center;margin: 20px auto;'>Не найдено</span>"
            }else{
              if (display === 'card'){
                if(data["data"].length>10){
                  empty=pagination+"<div style='width:100%'>"+empty+"</div>"+pagination;
                }else{
                  empty=pagination+"<div style='width:100%'>"+empty+"</div>";
                }}else{
                if(data["data"].length>10){
                  empty=pagination+"<div class='collection' style='width:100%'>"+empty+"</div>"+pagination;
                }else{
                  empty=pagination+"<div class='collection' style='width:100%'>"+empty+"</div>";
                }
              }
            }

            list.innerHTML = empty;
        }