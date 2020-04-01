

function deletePost(post){
	let post_id = $(post).attr('ident');
	let del = "post_by_id";
	$.ajax({
		url:'/delete',
		method:"POST",
		data:{post_id:post_id,delete:del},
		success:function(message){
			//console.log(message);
			loadPosts();
		},
		error:function(message){
			console.log(message);
		}
	})
}