$(function() {
    $('#btnlogin').click(function() {
	$.ajax({
	    url: '/login',
	    data: $('form').serialize(),
	    type: 'POST',
	    success: function(response) {
		console.log(response);
	    },
	    error: function(error) {
		console.log(error);
	    }
	});
    });
});
