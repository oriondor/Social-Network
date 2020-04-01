function loadPosts(){
	let load = "load_posts"
	$.ajax({
		url:"/posts",
		method:"POST",
		data:{load:load},
		success:function(message){
			$('#posts').html(message);
		},
		error:function(message){
			//console.log('Here"s an error');
			//console.log(message);
		}
	});
}

$(document).ready(function(){
	loadPosts();
});