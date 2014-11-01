function average(list) {

    var sum = list.reduce(function(a, b) { return a + b; });
    return (sum /list.length).toFixed(1);

}

function displayJudging() {

    $(".title").click(function(evt) {

        $('#list-heading').html($(this).text());
        $('.result-list').html("Be patient while the Eye deliberates.");
        var td_id = $(this).attr("id");
        var movie_id = td_id.substr(5, td_id.length); // hacking the string, fix later

        $.get(
            "/movie",
            {'id': movie_id},
            function(result) {

                var beratement = result['beratement'];
                var prediction = result['prediction'];
                var userRating = result['user rating'];

                if (userRating !== null) {
                    $('.result-list').html("You gave this movie "+userRating+" stars.");
                } else {
                    $('.result-list').html("The Eye predicts your rating will be "+prediction.toFixed(1));
                }
                
                $('.result-list').append('<div class="beratement"><p id="the-eye-says">The Eye says...</p><p>'+beratement+'</p></div>');

            });
    });
}

function loadDashboard(){

    $.get(
        "/get-user-ratings",
        function(result) {

            var ratings = [];

            $('.result-list').html("<table id='movie-list'><th>Title</th><th>Rating</th><th><button id='update-button'>Update?</button></th></table>");

            Object.keys(result).forEach(function(movie_title) {

                var movie_rating = result[movie_title][0];
                var movie_id = result[movie_title][1];
                ratings.push(movie_rating);

                $('#movie-list').append("<tr><td class='title' id=title"+movie_id+">"+movie_title+"</td><td id=rating"+movie_id+">"+movie_rating+"</td><td><input type='text' class='update-box' id="+movie_id+" style='width:25px'></td></tr>");

            });

            displayJudging();

            $('#update-button').click(function(evt) {

                var updates = {};

                $('.update-box').each(function(index) {
                    var ratingUpdate = $(this).val();
                    var movieId = $(this).attr("id");
                    $(this).val("");
                    if (ratingUpdate !== "") {
                        updates[movieId] = ratingUpdate;
                    }

                });

                $.post(
                    "/update_ratings",
                    {"updates": JSON.stringify(updates)},
                    function(result) {

                        Object.keys(updates).forEach(function(movie_id){

                            var rating = updates[movie_id];
                            $('#rating'+movie_id.toString()).html(rating);
                            loadDashboard();

                        });
                    });
            });

            $('#list-heading').html('Dashboard: Your average rating is '+average(ratings).toString());

    });
}

$(document).ready(function(e) {

    loadDashboard();

});

$('#get-dashboard').click(function(evt) {

    loadDashboard();

});

$('#log-out').click(function(evt) {

    $.post(
        "/log-out",
        function(result) {
            window.location = result;
        });

});
    
$('#get-users').click(function(evt) {

    $.get(
        "/get-user-list",
        function(result) {

            $('.result-list').html("<div id='users'><p id='users-list'></p></div>");
            result["users"].forEach(function(user_id){

                $("#users-list").append("<button class='user-button' value="+user_id+">"+user_id+"</button>");
            
            });

            $('.user-button').click(function(evt) {

                $.get(
                    "/get-user-ratings",
                    {"id": $(this).val()},
                    function(result) {

                        var ratings = [];

                        $('.result-list').html("<table id='movie-list'><th>Title</th><th>Rating</th><table>");

                        Object.keys(result).forEach(function(movie_title) {

                            var rating = result[movie_title][0];
                            var movie_id = result[movie_title][1];
                            ratings.push(rating);

                            $('#movie-list').append("<tr><td class='title' id=title"+movie_id+">"+movie_title+"</td><td>"+rating+"</td></tr>");

                        });

                        $('#list-heading').html('The average rating for this user is '+average(ratings).toString());

                displayJudging();

                });
                
            });
    });

    $('#list-heading').html('Click on User ID for a list of their ratings!');

});
