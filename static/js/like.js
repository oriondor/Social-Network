function like(button){
	let post_user = $(button).attr('ident').split('|');
	let like = 'like';
	let disliked_class = 'btn-outline-info';
	let liked_class = 'btn-info';
	if ($(button).hasClass(disliked_class)){
		$(button).removeClass(disliked_class);
		$(button).addClass(liked_class);
		like='like';
	}else{
		$(button).removeClass(liked_class);
		$(button).addClass(disliked_class);
		like='dislike';
	}
	$.ajax({
		url:'/like',
		method:"POST",
		data:{like:like,post:post_user[0],user:post_user[1]},
		success:function(message){
			$(button).html(message);
		},
		error:function(message){
			//console.log(message);
		}
	});
	//console.log(post_user);
}