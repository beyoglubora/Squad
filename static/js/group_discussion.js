function create_form(this_element) {
    $(".post_form").remove();
    var parent_id = this_element.parentElement.id;

    var container = document.createElement("div");
    container.setAttribute('class', 'post_form');

    var body = document.createElement("input"); //input element, text
    body.setAttribute('type',"text");
    body.setAttribute('id',"reply"+toString(parent_id));

    var buttonElement = document.createElement("button");
    buttonElement.onclick = function () { create_post(parent_id, body.id) };

    container.appendChild(body);
    container.appendChild(buttonElement);

    var parent = document.getElementById(parent_id);

    parent.appendChild(container);

}

function create_post(parent_id,body_id){
    var bodyElement = document.getElementById(body_id);
    var body = bodyElement.value;
        $.ajax({
                url: '/discussion/create/',
                method: 'post',
                data: {
                    'csrfmiddlewaretoken': '{{ csrf_token }}',
                    'body': body,
                    'group_instance': '',
                    'parent_id': parent_id,
                    'class_instance': ''
                },
                dataType: 'json',
                success: function (data) {
                    if(data["result"]){
                        window.location.href = ""
                    }
                    else {
                        window.location.href = ""
                    }
                },
                error: function (data){
                }
              });
    }

function delete_post(post_id){
    $.ajax({
            url: '/discussion/delete/',
            method: 'post',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
                'post_id': post_id
            },
            dataType: 'json',
            success: function (data) {
                if(data["result"]){
                    window.location.href = ""
                }
                else {
                    window.location.href = ""
                }
            },
            error: function (data){
            }
          });
}

function edit_post(post_id, new_body){
    $.ajax({
            url: '/discussion/edit/',
            method: 'post',
            data: {
                'csrfmiddlewaretoken': '{{ csrf_token }}',
                'post_id': post_id,
                'new_body': new_body
            },
            dataType: 'json',
            success: function (data) {
                if(data["result"]){
                    window.location.href = ""
                }
                else {
                    window.location.href = ""
                }
            },
            error: function (data){
            }
          });
}
