$(document).ready(function() { /* code here */ 
	
	//var table_html = '<table class="table"><thead class="my_thead"><tr><th scope="col">Name</th><th scope="col">Close</th><th scope="col">Low</th><th scope="col">High</th><th scope="col">Open</th><th scope="col">SC Code</th></tr></thead><tbody><tr>';
	get_top_10();
	$("#spinnerdiv").css("display", "none");
	
	var input = document.getElementById("search-input");
	input.addEventListener("keyup", function(event) {
	  if (event.keyCode === 13) {
	   event.preventDefault();
	   makeRequest();
	   //document.getElementById("myBtn").click();
	  }
	});


		function get_top_10(){
			
			var get_top_10_table_html = '<table class="table"><thead class="my_thead"><tr><th scope="col">Name</th><th scope="col">Close</th><th scope="col">Low</th><th scope="col">High</th><th scope="col">Open</th><th scope="col">SC Code</th></tr></thead>';
					var settings = {
			  "async": true,
			  "crossDomain": true,
			  "url": "/get_top_10",
			  "method": "GET",
			  "headers": {
			    "content-type": "application/json",
			    "cache-control": "no-cache",
			    "postman-token": "66c24eda-81d8-6301-8f8c-6648dd3988c5"
			  },
			  "processData": false
			}
			
			$.ajax(settings).done(function (response) {
				
				get_top_10_table_html = get_top_10_table_html + '<tbody>';
				Object.keys(response).forEach(function(key) {
					
					var row="";
					row = row + '<tr><td>'+key+'</td>';
					for (var i=0;i<response[key].length;i++){
						row = row + '<td>'+response[key][i]+'</td>';
					}
					row = row + '</tr>';
					get_top_10_table_html = get_top_10_table_html + row;
				})
				get_top_10_table_html = get_top_10_table_html + '</tbody></table>';
				console.log(get_top_10_table_html);
				$('#top-ten-table').html(get_top_10_table_html);

     			
			});
		}


		function makeRequest(){

			// get_top_10()

			var data = "{\"stock_name\":\""+$('#search-input').val()+"\"}";
			console.log("data",data);
					var settings = {
			  "async": true,
			  "crossDomain": true,
			  "url": "/",
			  "method": "POST",
			  "headers": {
			    "content-type": "application/json",
			    "cache-control": "no-cache",
			    "postman-token": "66c24eda-81d8-6301-8f8c-6648dd3988c5"
			  },
			  "processData": false,
			  "data": data//"{\"stock_name\":\"OMAX AUTOS.\"}"
			}
			
			$.ajax(settings).done(function (response) {
				
				if(response["result"].length>0){

					var table_row_data;
				table_row_data = '<tr class="success"><td>'+$('#search-input').val().toUpperCase()+'</td>';
				var i;
				for (i = 0; i < response["result"].length; i++) { 
				  table_row_data = table_row_data + "<td>"+response["result"][i]+"</td>";
				  console.log(response["result"][i]);
				}
				table_row_data = table_row_data + '</tr>';
				// $('#top-ten-table').prepend(table_row_data);
				//$('#top-ten-table > tbody:last-child').append(table_row_data);
				$('#top-ten-table tr:nth-child(1)').replaceWith(table_row_data);
				$('.my_thead').html('<tr><th scope="col">Name</th><th scope="col">Close</th><th scope="col">Low</th><th scope="col">High</th><th scope="col">Open</th><th scope="col">SC Code</th></tr>');

				// table_html = table_html + table_row_data;
				// console.log(table_html);
				// $('#search-result-table').html(table_html);
     			console.log(table_row_data);	
				}else{
					alert("company name not found.")
					$('#search-input').val("");

				}
				
			});

		}
		

//});

});
