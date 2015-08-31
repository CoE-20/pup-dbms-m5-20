console.log('working');
function onFormSubmit(event){

    var data = $(event.target).serializeArray();
    var thesis = {};
    for (var i = 0; i<data.length; i++)
    {
        thesis[data[i].name] = data[i].value
    }

    var thesis_create_api = "/api/thesis";
    $.post(thesis_create_api, thesis, function(response){
        if (response.status = 'OK'){
            var full_details = response.data.year+ ' ' +response.data.Title+ ' ' +response.data.abstract+ ' ' +response.data.adviser+ ' ' +response.data.adviser 
            + ' ' +response.data.section
             $('#thesis-list').append('<li>' + full_details + '</li>')
        }else{

        }
    });
    
    return false;
}

function loadAllThesisdetails(){
    var student_list_api = '/api/thesis';
    $.get(student_list_api, {}, function(response){
        console.log('thesis-list', response)
        response.data.forEach(function(thesis) {
            var full_details = thesis.year + ' ' + thesis.Title + ' ' + thesis.abstract + ' ' + thesis.adviser + ' ' + thesis.section
        $('#thesis-list').append('<li>' + full_details + '</li>')    
        });
    });
}


$('#create-form').submit(onFormSubmit)
loadAllThesisdetails();
$('#create-form').submit(function(onFormSubmit){
    (this).reset()
});