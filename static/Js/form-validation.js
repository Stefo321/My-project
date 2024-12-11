document.addEventListener('DOMContentLoaded', function () {
    // Form Validation Logic for Post Form
    var postForm = document.getElementById('postForm');
    if (postForm) {
        var titleField = document.getElementById('id_title');
        var contentField = document.getElementById('id_content');

        // Add custom validation message for empty fields
        titleField.addEventListener('invalid', function () {
            this.setCustomValidity('Title is required. Please enter a title.');
        });

        contentField.addEventListener('invalid', function () {
            this.setCustomValidity('Content is required. Please enter some content.');
        });

        // Clear validation messages when user starts typing
        titleField.addEventListener('input', function () {
            this.setCustomValidity('');
        });

        contentField.addEventListener('input', function () {
            this.setCustomValidity('');
        });

        // Prevent form submission if fields are empty
        postForm.addEventListener('submit', function (event) {
            if (titleField.value.trim() === '') {
                alert('Title is required!');
                event.preventDefault();
            } else if (contentField.value.trim() === '') {
                alert('Content is required!');
                event.preventDefault();
            }
        });
    }

    // Form Validation Logic for Comment Form
    var commentForm = document.getElementById('commentForm');
    if (commentForm) {
        var commentField = document.getElementById('id_text');

        // Add custom validation message for empty fields
        commentField.addEventListener('invalid', function () {
            this.setCustomValidity('Comment text is required!');
        });

        // Clear validation messages when user starts typing
        commentField.addEventListener('input', function () {
            this.setCustomValidity('');
        });

        // Prevent form submission if field is empty
        commentForm.addEventListener('submit', function (event) {
            if (commentField.value.trim() === '') {
                alert('Comment text is required!');
                event.preventDefault();
            }
        });
    }
});
