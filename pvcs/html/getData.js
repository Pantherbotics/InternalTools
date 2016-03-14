var xmlhttp = new XMLHttpRequest();
var url = "customData.json";

xmlhttp.onreadystatechange = function() {
    if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
        var myArr = JSON.parse(xmlhttp.responseText);
        setRepos(myArr);
    }
}

xmlhttp.open("GET", url, true);
xmlhttp.send();

var dataArray = {}

function setRepos(arr) {
    dataArray = arr
    var ip = arr['__data']['ip']
    $("#header").text('Pantherbotics Version Control Software (server: '+ip+')')

    for(var index in arr) {
      if (index.substring(0, 2) == "__"){continue;}
      
      
      var rowA = '<tr class="repo" id="'+index+'"><td>' +index+ "</td><td>" +arr[index]['path']+ "</td><td>";
      var rowB =  arr[index]['state']+ '</td><td>'+arr[index]['date']+ '</td><td><a href="'+arr[index]['link']+'">'+arr[index]['link']+'</a></td></tr';
      $("#repos tr:last").after(rowA+rowB);
    }
}

$('#nameSubmit').click(function() {
    for (var index in dataArray) {
    var l = String(dataArray[index]['link'])
    var u = $('#nameChange').val();
    dataArray[index]['link'] = u+"@"+l.split("@")[1] 
    $('.repo').remove();
    }
    setRepos(dataArray);
});
