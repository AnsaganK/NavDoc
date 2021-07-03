        function createDetail(data){
            let create_user_first_name;
            let create_user_last_name;
          let modal = document.getElementById("modal1");
          modal.classList.add("note_info");
          let buh = data.buh !== null ? `${data.buh.first_name} ${data.buh.last_name}(подписано)`: 'в ожидании';

          let tags = '';
          data.tags.length>0?data.tags.forEach((i)=>{tags+=`<li class="note_detail_tag">${i.name}</li>`}):"";

          let file_count = 0;
          let files = ''
          data.files.length>0?data.files.forEach((i)=>{
            file_count++;
            files+=`<a href="${i.file }" target="_blank" style="margin-left: 10px"><?xml version="1.0" encoding="UTF-8" standalone="no"?>
                    <svg fill="#1b61a9" id="Layer_1" width="30" data-name="Layer 1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
                        <title>file, document, office, work, letter</title>
                        <path d="M16.17,0H2V24H22V6.8ZM20,22H4V2h9V9h7ZM15,7V2h.25l4.29,5Z"/>
                        <rect x="6" y="12" width="12" height="2"/>
                        <rect x="6" y="15" width="12" height="2"/>
                        <rect x="6" y="18" width="12" height="2"/>
                        <rect x="6" y="7" width="5" height="2"/>
                    </svg></a>`;
          }):"";
          files !== ''? files = `<div class="note_info_item"><span>Файлы:</span><span>${files}</span></div>` : ''

          let status = data.status;
          let status_image = '';
          if (status === null){
            status_image = 'wait';
          }else if(status === 'success'){
            status_image = 'success';
          }else if(status === 'edit'){
            status_image = 'warning';
          }else if(status === 'error'){
            status_image = 'error';
          }

          let user_count = 0;
          let users = '';
          data.users.forEach((i)=>{
            let user_status = '';
            user_count++;
            if(user_count === data.user_index){
              console.log(i);
              if (status == null){
                user_status = 'current_user';
              }else if(status === 'success'){
                user_status = 'success_user';
              }else if(status === 'edit'){
                user_status = 'edit_user';
              }else if(status === 'error') {
                user_status = 'error_user';
              }
            }else if(user_count < data.user_index){
                user_status = 'success_user';
              }
            if (i.user !== null){
                let first_name = i.user.first_name;
                let last_name = i.user.last_name;
                users+=`<li class="note_detail_user ${user_status}">${first_name} ${last_name}</li><span class="user_line"></span>`
            }else{
                users+=`<li class="note_detail_user">Удаленный пользователь</li><span class="user_line"></span>`
            }
          });
          users = `<ul class="note_detail_users">${users}</ul>`

            if(data.user !== null){
                create_user_first_name = data.user.first_name;
                create_user_last_name = data.user.last_name;
            }else{
                create_user_first_name = "Удаленный";
                create_user_last_name = "пользователь";
            }
          modal.innerHTML = `<div class="note_detail">
                <div style="display: flex;
                margin-top: 14px;
                border-radius: 10px;
                flex-direction: column;">
                    <img src="/static/img/${status_image}.svg" class="note_info_img" width="60" height="60">
                    <div class="note_info_item"><span>Создал:</span>
                        <span>${create_user_first_name} ${create_user_last_name}</span></div>
                    <div class="note_info_item"><span>Название:</span> <span>${data.title}</span></div>
                    <div class="note_info_item"><span>Дата СЗ:</span> <span>${data.date}</span></div>
                    <div class="note_info_item"><span>Дата создания:</span> <span>22 июня 2021 г. 11:18</span></div>
                    <div class="note_info_item"><span>Текст:</span> <span><p>${data.text}</p></span></div>
                    <div class="note_info_item"><span>Итого:</span> <span>${data.summa}</span></div>
                    <div class="note_info_item"><span>Бухгалтер:</span> <span> <span style="color:grey;">${buh}</span> </span></div>
                    ${files}
                    <ul class="note_detail_tags">
                    ${tags}
                    </ul>
                </div>
                ${users}
            </div>`;

        }